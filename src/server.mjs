import http from 'node:http';
import crypto from 'node:crypto';
import {isIP} from 'node:net';
import {createReceipts,clientError} from './receipts.mjs';
import {createStatistics,MemoryStatsStore,PgStatsStore} from './statistics.mjs';
import {createPool} from './database.mjs';
import {gzipSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {loadContent,hints,scoreAnswer,catalogue} from './content.mjs';

export function dateInZone(now, zone='Europe/Budapest') {
  return new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).format(now);
}
export function createApp({days=loadContent(),zone=process.env.GAME_TIMEZONE||'Europe/Budapest',clock=()=>new Date(),
  previewDate=process.env.DEV_DATE||'',production=process.env.NODE_ENV==='production',
  allowedOrigins=(process.env.ALLOWED_ORIGINS||'http://localhost:5173,http://127.0.0.1:5173').split(',').map(x=>x.trim()).filter(Boolean),rateLimit=Number(process.env.RATE_LIMIT_PER_MINUTE||600),
  store=null,signingSecret=process.env.SIGNING_SECRET,playerSecret=process.env.PLAYER_HASH_SECRET,trustProxy=process.env.TRUST_PROXY==='railway'}={}) {
  if(production && previewDate) throw new Error('DEV_DATE is forbidden in production');
  if(production && !store)throw new Error('Production requires PostgreSQL statistics storage');
  if(production && store?.mode!=='postgres')throw new Error('Production requires PostgreSQL, never memory statistics');
  if(production && (!signingSecret||!playerSecret||!process.env.ALLOWED_ORIGINS))throw new Error('Production requires SIGNING_SECRET, PLAYER_HASH_SECRET and explicit ALLOWED_ORIGINS');
  const receipts=createReceipts({secret:signingSecret||crypto.randomBytes(32).toString('hex'),playerSecret:playerSecret||crypto.randomBytes(32).toString('hex'),clock});
  const statistics=store?createStatistics(store):null;
  if(previewDate && (!/^\d{4}-\d{2}-\d{2}$/.test(previewDate)||!days.has(previewDate))) throw new Error('DEV_DATE must be an installed date');
  dateInZone(clock(),zone); // Fail fast on invalid timezone.
  const buckets=new Map(), dailyBuffers=new Map();
  const stats={requests:0,errors:0,rateLimited:0};
  const today=()=>previewDate||dateInZone(clock(),zone);
  function send(req,res,status,value,cache='no-store') {
    let body=Buffer.from(JSON.stringify(value));
    const headers={'Content-Type':'application/json; charset=utf-8','Cache-Control':cache,'X-Content-Type-Options':'nosniff',Vary:'Origin, Accept-Encoding'};
    if(body.length>1024 && /\bgzip\b/.test(req.headers['accept-encoding']||'')) {body=gzipSync(body);headers['Content-Encoding']='gzip';}
    res.writeHead(status,{...headers,'Content-Length':body.length}); res.end(body);
  }
  const error=(req,res,status,code,message)=>{stats.errors++;send(req,res,status,{error:{code,message},date:today()});};
  function limited(req) {
    if(rateLimit===0) return false;
    // Only enable this deployment-specific header trust behind Railway's managed HTTP ingress.
    // X-Forwarded-For is never read; local/direct deployments use the socket address.
    const forwarded=req.headers['x-real-ip'];
    const ip=trustProxy&&typeof forwarded==='string'&&isIP(forwarded)?forwarded:req.socket.remoteAddress, minute=Math.floor(Date.now()/60000), found=buckets.get(ip);
    if(!found||found.minute!==minute) {
      if(buckets.size>=50000) {for(const [k,b] of buckets) if(b.minute!==minute) buckets.delete(k);}
      if(buckets.size>=50000) return true;
      buckets.set(ip,{minute,count:1});return false;
    }
    return ++found.count>rateLimit;
  }
  async function body(req,maxBytes=4096) {
    if(!/^application\/json(?:\s*;|$)/i.test(req.headers['content-type']||'')) throw Object.assign(new Error('JSON required'),{status:415});
    let data='', size=0;
    for await(const chunk of req) {size+=chunk.length;if(size>maxBytes) throw Object.assign(new Error('Body too large'),{status:413});data+=chunk;}
    try {return JSON.parse(data);} catch {throw Object.assign(new Error('Invalid JSON'),{status:400});}
  }
  const server=http.createServer({maxHeaderSize:8192,requestTimeout:15000,headersTimeout:10000},async(req,res)=>{
    stats.requests++;
    const origin=req.headers.origin;
    if(origin && !allowedOrigins.includes(origin)) return error(req,res,403,'ORIGIN_REJECTED','Origin is not allowed');
    if(origin) res.setHeader('Access-Control-Allow-Origin',origin);
    if(req.method==='OPTIONS') {res.writeHead(204,{'Access-Control-Allow-Methods':'GET, POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'600',Vary:'Origin'});res.end();return;}
    try {
      if((req.url||'').length>2048) return error(req,res,414,'URL_TOO_LONG','URL too long');
      const url=new URL(req.url,'http://localhost');
      if(url.pathname==='/healthz' && req.method==='GET') return send(req,res,200,{status:'ok',contentDays:days.size});
      if(url.pathname==='/readyz' && req.method==='GET'){
        try{if(store)await store.ready();return send(req,res,200,{status:'ready',statistics:store?.mode||'disabled'})}
        catch{return error(req,res,503,'DATABASE_UNAVAILABLE','Database readiness check failed')}
      }
      if(limited(req)) {stats.rateLimited++;res.setHeader('Retry-After','60');return error(req,res,429,'RATE_LIMIT','Too many requests');}
      if(!['GET','POST'].includes(req.method)) {res.setHeader('Allow','GET, POST, OPTIONS');return error(req,res,405,'METHOD','Method not allowed');}
      const date=today(), active=days.get(date), published=active?.day.publication_status==='scheduled';
      if(['/api/v1/results','/api/v1/statistics'].includes(url.pathname)){
        if(req.method!=='POST')return error(req,res,405,'METHOD','Use POST');
        if(!statistics)return error(req,res,503,'STATS_NOT_CONFIGURED','Daily statistics are not configured');
        const input=await body(req,16384);
        if(!input||typeof input!=='object'||Array.isArray(input))throw clientError('Object required');
        if(typeof input.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(input.date)||!Number.isFinite(Date.parse(input.date+'T00:00:00Z'))||new Date(input.date+'T00:00:00Z').toISOString().slice(0,10)!==input.date||input.date>date)throw clientError('Invalid completed game date');
        if(typeof input.revision!=='string'||!/^[a-f0-9]{24}$/.test(input.revision))throw clientError('Invalid content revision');
        const playerHash=receipts.playerHash(input.playerId);
        let value;
        if(url.pathname==='/api/v1/results'){
          const complete=receipts.completion(input);
          try{value=await statistics.record(complete)}catch(e){console.error(JSON.stringify({event:'statistics_write_failed',code:e.code||'UNKNOWN'}));return error(req,res,503,'STATS_UNAVAILABLE','Your result could not be stored. Retry later.')}
        }else{
          try{value=await statistics.get(input.date,input.revision,playerHash)}catch(e){console.error(JSON.stringify({event:'statistics_read_failed',code:e.code||'UNKNOWN'}));return error(req,res,503,'STATS_UNAVAILABLE','Statistics are temporarily unavailable')}
        }
        return send(req,res,200,{statistics:value});
      }
      if(url.pathname==='/api/v1/today' && req.method==='GET') {
        if(url.search) return error(req,res,400,'QUERY','This endpoint takes no date or preview parameters');
        const key=date+':'+(published?active.revision:'none');
        if(!dailyBuffers.has(key)) {
          dailyBuffers.clear();
          const data={date,timezone:zone,available:!!published,day_number:published?active.day.day_number:null,
            revision:published?active.revision:null,legacy_progress_key:published?active.legacyKey:null,
            start_date:[...days.keys()][0],published_dates:[...days].filter(([d,x])=>d<=date&&x.day.publication_status==='scheduled').map(([d])=>d),
            questions:published?active.publicQuestions:{},preview:!!previewDate,statistics:store?.mode||'disabled'};
          const plain=Buffer.from(JSON.stringify(data)),gzip=gzipSync(plain);
          dailyBuffers.set(key,{plain,gzip,etag:'"'+crypto.createHash('sha256').update(plain).digest('hex').slice(0,24)+'"'});
        }
        const item=dailyBuffers.get(key),gzip=/\bgzip\b/.test(req.headers['accept-encoding']||'');
        // No shared caching for this clock-dependent alias; dated access is intentionally absent.
        const headers={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-cache, max-age=0, must-revalidate',ETag:item.etag,Vary:'Origin, Accept-Encoding','X-Content-Type-Options':'nosniff'};
        if(req.headers['if-none-match']===item.etag) {res.writeHead(304,headers);res.end();return;}
        const data=gzip?item.gzip:item.plain;
        res.writeHead(200,{...headers,'Content-Length':data.length,...(gzip?{'Content-Encoding':'gzip'}:{})});res.end(data);return;
      }
      const match=url.pathname.match(/^\/api\/v1\/questions\/([^/]+)\/(hints|answer|catalogue)$/);
      if(!match) return error(req,res,404,'NOT_FOUND','Endpoint not found');
      if(!published) return error(req,res,404,'NO_DAILY_GAME','No question set is published today');
      const [_,id,action]=match;
      const compiled=active.questions.find(x=>x.q.id===id);
      if(!compiled) return error(req,res,404,'QUESTION_NOT_TODAY','Only today’s questions are accessible');
      if((action==='answer' && req.method!=='POST') || (action!=='answer' && req.method!=='GET')) return error(req,res,405,'METHOD','Wrong method');
      const input=action==='answer'?await body(req):Object.fromEntries(url.searchParams);
      if(!input || typeof input!=='object' || Array.isArray(input)) return error(req,res,400,'BODY','Object required');
      if(input.date!==date || input.revision!==active.revision) return error(req,res,409,'DAY_CHANGED','The day or its content changed. Reload to fetch today’s game.');
      const raw=action==='answer'?input.raw:input.q||'';
      if(typeof raw!=='string' || raw.length>(compiled.q.input_max_length||115)) return error(req,res,400,'INPUT','Invalid text length');
      if(action==='hints') return send(req,res,200,{candidates:hints(compiled,raw)});
      if(action==='answer') {
        const kind=input.kind||'answer';
        if(!['answer','skipped','timeout'].includes(kind))throw clientError('Invalid answer kind');
        if(kind==='answer'&&!raw.trim())return error(req,res,400,'EMPTY_ANSWER','Answer is empty');
        const result=kind==='answer'?scoreAnswer(compiled,raw.trim(),input.automatic===true):{raw:'',canonical:null,points:0,tier:kind==='skipped'?'SKIPPED':'TIME OUT',kind,metric_value:null};
        if(input.playerId!==undefined||input.runId!==undefined)result.receipt=receipts.issue({playerId:input.playerId,runId:input.runId,date,revision:active.revision,questionId:compiled.q.id,points:result.points});
        return send(req,res,200,{result});
      }
      const offset=Number(input.offset||0),limit=Number(input.limit||120),filter=input.filter||'all';
      if(!Number.isInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>120||!compiled.pools.has(filter)) return error(req,res,400,'PAGINATION','Invalid filter or pagination');
      return send(req,res,200,catalogue(compiled,{query:raw,filter,offset,limit}));
    } catch(e) {
      if(!res.headersSent) error(req,res,e.status||500,e.code||(e.status?'INVALID_REQUEST':'INTERNAL'),e.status?e.message:'Server error');
      if(!e.status) console.error(e);
    }
  });
  server.keepAliveTimeout=5000;
  return {server,stats,today,close:async()=>{await new Promise(resolve=>server.close(resolve));await store?.close()}};
}
if(process.argv[1]===fileURLToPath(import.meta.url)) {
  let store=null;
  if(process.env.DATABASE_URL)store=new PgStatsStore(createPool());
  else if(process.env.STATS_MODE==='memory'&&process.env.NODE_ENV!=='production')store=new MemoryStatsStore();
  if(store)await store.ready();
  const app=createApp({store});
  const port=Number(process.env.PORT||3000),host=process.env.HOST||(process.env.RAILWAY_ENVIRONMENT_ID||process.env.NODE_ENV==='production'?'0.0.0.0':'127.0.0.1');
  app.server.listen(port,host,()=>console.log(`CLOSEISH API http://${host}:${port} | ${app.today()} | statistics: ${store?.mode||'disabled'}`));
  let stopping=false;
  for(const signal of ['SIGTERM','SIGINT']) process.on(signal,()=>{
    if(stopping)return;stopping=true;
    app.close().then(()=>process.exit(0)).catch(()=>process.exit(1));
    setTimeout(()=>process.exit(1),10000).unref();
  });
}
