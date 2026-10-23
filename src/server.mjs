import http from 'node:http';
import crypto from 'node:crypto';
import {isIP} from 'node:net';
import {createReceipts,clientError} from './receipts.mjs';
import {createStatistics,MemoryStatsStore,PgStatsStore} from './statistics.mjs';
import {createPool} from './database.mjs';
import {PgProgressStore,MemoryProgressStore} from './progress.mjs';
import {gzipSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {loadContent,createLazyContent,hints,scoreAnswer,catalogue} from './content.mjs';

const FIRST_PLAYABLE_DATE='2026-10-23';
const zoneFormatters=new Map();
export function dateInZone(now, zone='Europe/Budapest') {
  let format=zoneFormatters.get(zone);
  if(!format){format=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'});zoneFormatters.set(zone,format)}
  return format.format(now);
}
export function createApp({days=createLazyContent(),zone=process.env.GAME_TIMEZONE||'Europe/Budapest',clock=()=>new Date(),
  previewDate=process.env.DEV_DATE||'',production=process.env.NODE_ENV==='production',
  allowedOrigins=(process.env.ALLOWED_ORIGINS||'http://localhost:5173,http://127.0.0.1:5173').split(',').map(x=>x.trim()).filter(Boolean),rateLimit=Number(process.env.RATE_LIMIT_PER_MINUTE||600),
  writeRateLimit=Number(process.env.WRITE_RATE_LIMIT_PER_MINUTE||120),
  apiKeys=(process.env.API_KEYS||'').split(',').map(x=>x.trim()).filter(Boolean),
  store=null,progressStore=store?.mode==='postgres'?new PgProgressStore(store.pool):store?.mode==='memory'?new MemoryProgressStore():null,signingSecret=process.env.SIGNING_SECRET,playerSecret=process.env.PLAYER_HASH_SECRET,trustProxy=process.env.TRUST_PROXY==='railway'}={}) {
  if(!Number.isInteger(rateLimit)||rateLimit<0||!Number.isInteger(writeRateLimit)||writeRateLimit<0)throw new Error('Rate limits must be non-negative integers');
  if(apiKeys.some(k=>k.length<24))throw new Error('Each API_KEYS entry must be at least 24 characters');
  const keyDigests=apiKeys.map(k=>crypto.createHash('sha256').update(k).digest());
  if(production && previewDate) throw new Error('DEV_DATE is forbidden in production');
  if(production && !store)throw new Error('Production requires PostgreSQL statistics storage');
  if(production && progressStore?.mode!=='postgres')throw new Error('Production requires PostgreSQL player progress');
  if(production && store?.mode!=='postgres')throw new Error('Production requires PostgreSQL, never memory statistics');
  if(production && (!signingSecret||!playerSecret||!process.env.ALLOWED_ORIGINS))throw new Error('Production requires SIGNING_SECRET, PLAYER_HASH_SECRET and explicit ALLOWED_ORIGINS');
  const receipts=createReceipts({secret:signingSecret||crypto.randomBytes(32).toString('hex'),playerSecret:playerSecret||crypto.randomBytes(32).toString('hex'),clock});
  const statistics=store?createStatistics(store):null;
  if(previewDate && (!/^\d{4}-\d{2}-\d{2}$/.test(previewDate)||!days.has(previewDate))) throw new Error('DEV_DATE must be an installed date');
  dateInZone(clock(),zone); // Fail fast on invalid timezone.
  const buckets=new Map(), writeBuckets=new Map(), dailyBuffers=new Map();
  const stats={requests:0,errors:0,rateLimited:0};
  const today=()=>previewDate||dateInZone(clock(),zone);
  // All access to dated questions and writes goes through this publication gate.
  function publishedDay(requested,now=today(),metadataOnly=false) {
    if(typeof requested!=='string'||!/^(\d{4})-(\d{2})-(\d{2})$/.test(requested)||requested>now||requested<FIRST_PLAYABLE_DATE||
       !Number.isFinite(Date.parse(requested+'T00:00:00Z'))||
       new Date(requested+'T00:00:00Z').toISOString().slice(0,10)!==requested)
      throw clientError('Unpublished or future day','DAY_NOT_AVAILABLE',404);
    // Archive/progress metadata must never compile an enormous question bank.
    if(metadataOnly && typeof days.status==='function') {
      if(days.status(requested)!=='scheduled')throw clientError('Unpublished day','DAY_NOT_AVAILABLE',404);
      return true;
    }
    const found=days.get(requested);
    if(found?.day.publication_status!=='scheduled')throw clientError('Unpublished day','DAY_NOT_AVAILABLE',404);
    return found;
  }
  function send(req,res,status,value,cache='no-store') {
    let body=Buffer.from(JSON.stringify(value));
    const headers={'Content-Type':'application/json; charset=utf-8','Cache-Control':cache,'X-Content-Type-Options':'nosniff',Vary:'Origin, Accept-Encoding'};
    if(body.length>1024 && /\bgzip\b/.test(req.headers['accept-encoding']||'')) {body=gzipSync(body);headers['Content-Encoding']='gzip';}
    res.writeHead(status,{...headers,'Content-Length':body.length}); res.end(body);
  }
  const error=(req,res,status,code,message)=>{stats.errors++;send(req,res,status,{error:{code,message},date:today()});};
  function validKey(req) {
    if(!keyDigests.length) return true;
    const given=req.headers['x-api-key'];
    if(typeof given!=='string'||!given) return false;
    const digest=crypto.createHash('sha256').update(given).digest();
    let ok=false; for(const d of keyDigests) if(crypto.timingSafeEqual(d,digest)) ok=true;
    return ok;
  }
  function limited(req,map=buckets,limit=rateLimit) {
    if(limit===0) return false;
    // Only enable this deployment-specific header trust behind Railway's managed HTTP ingress.
    // X-Forwarded-For is never read; local/direct deployments use the socket address.
    const forwarded=req.headers['x-real-ip'];
    const ip=trustProxy&&typeof forwarded==='string'&&isIP(forwarded)?forwarded:req.socket.remoteAddress, minute=Math.floor(Date.now()/60000), found=map.get(ip);
    if(!found||found.minute!==minute) {
      if(map.size>=50000) {for(const [k,b] of map) if(b.minute!==minute) map.delete(k);}
      if(map.size>=50000) return true;
      map.set(ip,{minute,count:1});return false;
    }
    return ++found.count>limit;
  }
  async function body(req,maxBytes=4096) {
    if(!/^application\/json(?:\s*;|$)/i.test(req.headers['content-type']||'')) throw Object.assign(new Error('JSON required'),{status:415});
    let data='', size=0;
    for await(const chunk of req) {size+=chunk.length;if(size>maxBytes) throw Object.assign(new Error('Body too large'),{status:413});data+=chunk;}
    try {return JSON.parse(data);} catch {throw Object.assign(new Error('Invalid JSON'),{status:400});}
  }
  const server=http.createServer({maxHeaderSize:8192,requestTimeout:15000,headersTimeout:10000},async(req,res)=>{
    const requestStarted=performance.now();
    res.setHeader('Server-Timing','app;dur=0');
    const originalWriteHead=res.writeHead.bind(res);
    res.writeHead=function(...args){if(!res.headersSent)res.setHeader('Server-Timing',`app;dur=${(performance.now()-requestStarted).toFixed(1)}`);return originalWriteHead(...args)};
    stats.requests++;
    const origin=req.headers.origin;
    if(origin && !allowedOrigins.includes(origin)) return error(req,res,403,'ORIGIN_REJECTED','Origin is not allowed');
    if(origin) {res.setHeader('Access-Control-Allow-Origin',origin);res.setHeader('Access-Control-Expose-Headers','ETag, Retry-After, Server-Timing');}
    if(req.method==='OPTIONS') {res.writeHead(204,{'Access-Control-Allow-Methods':'GET, POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type, X-API-Key','Access-Control-Max-Age':'600',Vary:'Origin'});res.end();return;}
    try {
      if((req.url||'').length>2048) return error(req,res,414,'URL_TOO_LONG','URL too long');
      const url=new URL(req.url,'http://localhost');
      if(url.pathname==='/healthz' && req.method==='GET') return send(req,res,200,{status:'ok',contentDays:days.size});
      if(url.pathname==='/readyz' && req.method==='GET'){
        try{if(store)await store.ready();if(progressStore)await progressStore.ready();return send(req,res,200,{status:'ready',statistics:store?.mode||'disabled'})}
        catch{return error(req,res,503,'DATABASE_UNAVAILABLE','Database readiness check failed')}
      }
      if(limited(req)) {stats.rateLimited++;res.setHeader('Retry-After','60');return error(req,res,429,'RATE_LIMIT','Too many requests');}
      if(url.pathname.startsWith('/api/') && !validKey(req)) return error(req,res,401,'API_KEY_REQUIRED','Missing or invalid API key');
      const write=req.method==='POST' && (url.pathname.startsWith('/api/v1/progress/') || url.pathname==='/api/v1/results' || /^\/api\/v1\/questions\/[^/]+\/answer$/.test(url.pathname));
      if(write && limited(req,writeBuckets,writeRateLimit)) {stats.rateLimited++;res.setHeader('Retry-After','60');return error(req,res,429,'RATE_LIMIT','Too many write requests');}
      if(!['GET','POST'].includes(req.method)) {res.setHeader('Allow','GET, POST, OPTIONS');return error(req,res,405,'METHOD','Method not allowed');}
      const date=today(); // Compile answer banks only for question-data routes, never for statistics/history.
      if(url.pathname==='/api/v1/progress' && req.method==='GET') {
        if(!progressStore)return error(req,res,503,'PROGRESS_NOT_CONFIGURED','Player storage unavailable');
        const playerHash=receipts.playerHash(url.searchParams.get('playerId'));
        const selected=url.searchParams.get('day')||date;
        // The selected day is for restoring a single historical run; month is for calendar history.
        if(url.searchParams.has('day'))publishedDay(selected,date,true);
        const month=url.searchParams.get('month')||selected.slice(0,7);
        if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(month))throw clientError('Invalid month');
        const [current,monthRows,official,oldResults]=await Promise.all([progressStore.one(selected,playerHash),progressStore.month(month,playerHash),store?.find(selected,playerHash),store?.month(month,playerHash)]);
        let daysOfMonth=monthRows;
        const known=new Set(daysOfMonth.map(x=>x.date));
        for(const item of oldResults||[])if(!known.has(item.date))daysOfMonth.push({date:item.date,revision:item.revision,answers:6,completed:true,legacyResult:true});
        daysOfMonth=daysOfMonth.filter(item=>item.date>=FIRST_PLAYABLE_DATE);
        daysOfMonth.sort((a,b)=>a.date.localeCompare(b.date));
        return send(req,res,200,{date:selected,current_date:date,progress:current,days:daysOfMonth,month,counted:!!official,officialScore:official?.score??null},'private, no-store');
      }
      if(url.pathname==='/api/v1/progress/start' && req.method==='POST') {
        if(!progressStore)return error(req,res,503,'PROGRESS_NOT_CONFIGURED','Player storage unavailable');
        const input=await body(req);
        const selected=input.date,day=publishedDay(selected,date);
        if(input.revision!==day.revision)throw clientError('Content changed','DAY_CHANGED',409);
        const hash=receipts.playerHash(input.playerId),runId=receipts.run(input.runId);
        if(store&&(await store.find(selected,hash))&&!(await progressStore.one(selected,hash)))throw clientError('This day has already been completed','DAY_ALREADY_COMPLETED',409);
        if(!Number.isInteger(input.activeRound)||input.activeRound<0||input.activeRound>5)throw clientError('Invalid round');
        const deadline=input.activeDeadline;
        if(typeof deadline!=='number'||!Number.isFinite(deadline)||Math.abs(deadline-Date.now())>300000)throw clientError('Invalid round deadline');
        const progress=await progressStore.milestone({date:selected,hash,revision:day.revision,runId,
          activeRound:input.activeRound,activeDeadline:deadline,phase:'play'});
        return send(req,res,200,{progress});
      }
      if(url.pathname==='/api/v1/progress/import' && req.method==='POST') {
        if(!progressStore)return error(req,res,503,'PROGRESS_NOT_CONFIGURED','Player storage unavailable');
        const input=await body(req,16000);
        if(!input||typeof input!=='object'||Array.isArray(input))throw clientError('Invalid progress');
        if(typeof input.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(input.date)||input.date<FIRST_PLAYABLE_DATE||input.date>date)throw clientError('Invalid date');
        const hash=receipts.playerHash(input.playerId),runId=receipts.run(input.runId);
        if(!Array.isArray(input.responses)||input.responses.length<1||input.responses.length>6)throw clientError('Invalid responses');
        // Verify signatures/expiry before touching a potentially enormous historical bank.
        const tokens=input.responses.map(response=>receipts.verify(response?.receipt));
        const old=days.get(input.date);
        if(!old||input.revision!==old.revision)throw clientError('Cannot import a different content version','REVISION_MISMATCH',409);
        const responses=input.responses.map((response,i)=>{
          const token=tokens[i],q=old.questions[i];
          if(token.p!==hash||token.run!==runId||token.d!==input.date||token.r!==input.revision||token.q!==q.q.id)throw clientError('Receipt mismatch');
          const kind=['skipped','timeout'].includes(response.kind)?response.kind:'answer';
          const checked=kind==='answer'?scoreAnswer(q,String(response.raw||'').trim(),response.autoLocked===true):{raw:'',canonical:null,points:0,tier:kind==='skipped'?'SKIPPED':'TIME OUT',kind,metric_value:null};
          if(checked.points!==token.s)throw clientError('Answer does not match signed score');
          return {...checked,receipt:response.receipt};
        });
        const value=await progressStore.import({date:input.date,hash,revision:input.revision,runId,responses});
        return send(req,res,200,value);
      }
      if(['/api/v1/results','/api/v1/statistics'].includes(url.pathname)){
        if(req.method!=='POST')return error(req,res,405,'METHOD','Use POST');
        if(!statistics)return error(req,res,503,'STATS_NOT_CONFIGURED','Daily statistics are not configured');
        const input=await body(req,16384);
        if(!input||typeof input!=='object'||Array.isArray(input))throw clientError('Object required');
        if(typeof input.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(input.date)||!Number.isFinite(Date.parse(input.date+'T00:00:00Z'))||new Date(input.date+'T00:00:00Z').toISOString().slice(0,10)!==input.date||input.date<FIRST_PLAYABLE_DATE||input.date>date)throw clientError('Invalid completed game date');
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
      const dated=url.pathname.match(/^\/api\/v1\/days\/(\d{4}-\d{2}-\d{2})$/);
      if((url.pathname==='/api/v1/today'||dated) && req.method==='GET') {
        if(url.search) return error(req,res,400,'QUERY','Use the dated path without query parameters');
        const selected=dated?dated[1]:date;
        const chosen=dated?publishedDay(selected,date):days.get(date);
        const ready=selected>=FIRST_PLAYABLE_DATE && chosen?.day.publication_status==='scheduled';
        const key=selected+':'+(ready?chosen.revision:'none')+':'+date;
        if(!dailyBuffers.has(key)) {
          dailyBuffers.clear();
          const data={date:selected,current_date:date,timezone:zone,available:!!ready,day_number:ready?chosen.day.day_number:null,
            revision:ready?chosen.revision:null,legacy_progress_key:ready?chosen.legacyKey:null,
            start_date:FIRST_PLAYABLE_DATE,published_dates:[...days].filter(([d,x])=>d>=FIRST_PLAYABLE_DATE&&d<=date&&x.day.publication_status==='scheduled').map(([d])=>d),
            questions:ready?chosen.publicQuestions:{},preview:!!previewDate,statistics:store?.mode||'disabled'};
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
      const [_,id,action]=match;
      if((action==='answer' && req.method!=='POST') || (action!=='answer' && req.method!=='GET')) return error(req,res,405,'METHOD','Wrong method');
      const input=action==='answer'?await body(req):Object.fromEntries(url.searchParams);
      if(!input || typeof input!=='object' || Array.isArray(input)) return error(req,res,400,'BODY','Object required');
      const selected=input.date,chosen=publishedDay(selected,date);
      if(input.revision!==chosen.revision) return error(req,res,409,'DAY_CHANGED','This day’s content has changed. Reload its challenge.');
      const questionIndex=chosen.questions.findIndex(x=>x.q.id===id);
      const compiled=chosen.questions[questionIndex];
      if(!compiled) return error(req,res,404,'QUESTION_NOT_FOUND','This question is not part of the selected day');
      const raw=action==='answer'?input.raw:input.q||'';
      if(typeof raw!=='string' || raw.length>(compiled.q.input_max_length||115)) return error(req,res,400,'INPUT','Invalid text length');
      if(action==='hints') return send(req,res,200,{candidates:hints(compiled,raw)});
      if(action==='answer') {
        const kind=input.kind||'answer';
        if(!['answer','skipped','timeout'].includes(kind))throw clientError('Invalid answer kind');
        if(kind==='answer'&&!raw.trim())return error(req,res,400,'EMPTY_ANSWER','Answer is empty');
        const result=kind==='answer'?scoreAnswer(compiled,raw.trim(),input.automatic===true):{raw:'',canonical:null,points:0,tier:kind==='skipped'?'SKIPPED':'TIME OUT',kind,metric_value:null};
        if(input.playerId!==undefined||input.runId!==undefined) {
          result.receipt=receipts.issue({playerId:input.playerId,runId:input.runId,date:selected,revision:chosen.revision,questionId:compiled.q.id,points:result.points});
          if(progressStore){
            const playerHash=receipts.playerHash(input.playerId),runId=receipts.run(input.runId);
            // First-round shortcut cannot bypass the completed-day lock.
            if(questionIndex===0&&store&&(await store.find(selected,playerHash))&&!(await progressStore.one(selected,playerHash)))
              throw clientError('This day has already been completed','DAY_ALREADY_COMPLETED',409);
            const progress=await progressStore.answer({date:selected,hash:playerHash,revision:chosen.revision,runId,round:questionIndex,response:result});
            // The last persisted round also records the official statistics.
            // The durable browser outbox remains a fallback if statistics are unavailable.
            let counted=false;
            if(progress.completed&&store){
              try{
                const official=await store.record({date:selected,revision:chosen.revision,playerHash,runId,
                  score:progress.responses.reduce((total,item)=>total+item.points,0)});
                counted=!!official;
              }catch(e){console.error(JSON.stringify({event:'automatic_result_record_failed',code:e.code||'UNKNOWN'}))}
            }
            // Duplicate/ambiguous retries always return the FIRST persisted response.
            return send(req,res,200,{result:progress.responses[questionIndex],progress,counted});
          }
        }
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
  return {server,stats,days,today,close:async()=>{await new Promise(resolve=>server.close(resolve));await store?.close()}};
}
if(process.argv[1]===fileURLToPath(import.meta.url)) {
  let store=null;
  if(process.env.DATABASE_URL)store=new PgStatsStore(createPool());
  else if(process.env.STATS_MODE==='memory'&&process.env.NODE_ENV!=='production')store=new MemoryStatsStore();
  if(store)await store.ready();
  const app=createApp({store});
  if(app.days?.get)app.days.get(app.today());
  const port=Number(process.env.PORT||3000),host=process.env.HOST||(process.env.RAILWAY_ENVIRONMENT_ID||process.env.NODE_ENV==='production'?'0.0.0.0':'127.0.0.1');
  app.server.listen(port,host,()=>console.log(`CLOSEISH API http://${host}:${port} | ${app.today()} | statistics: ${store?.mode||'disabled'}`));
  let stopping=false;
  for(const signal of ['SIGTERM','SIGINT']) process.on(signal,()=>{
    if(stopping)return;stopping=true;
    app.close().then(()=>process.exit(0)).catch(()=>process.exit(1));
    setTimeout(()=>process.exit(1),10000).unref(); 
  });
}
