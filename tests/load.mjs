/* Local, closed-loop benchmark. Not a production capacity certification. */
import {spawn} from 'node:child_process';
import {performance} from 'node:perf_hooks';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const base=process.env.LOAD_URL||'http://127.0.0.1:3099',seconds=Number(process.env.LOAD_SECONDS||15),concurrency=Number(process.env.LOAD_CONCURRENCY||40);
let child;
if(!process.env.LOAD_URL){
 child=spawn(process.execPath,['src/server.mjs'],{cwd:root,env:{...process.env,PORT:'3099',DEV_DATE:'2026-10-21',RATE_LIMIT_PER_MINUTE:'0'},stdio:['ignore','pipe','inherit']});
 await new Promise((resolve,reject)=>{child.stdout.on('data',chunk=>{if(String(chunk).includes('CLOSEISH API'))resolve()});child.on('exit',code=>reject(new Error('API exited: '+code)))});
}
try{
 const today=await (await fetch(base+'/api/v1/today')).json();
 const latencies=[],statuses={};let requests=0;const errors=[];let responseBytes=0;
 const start=performance.now(),end=start+seconds*1000;
 await Promise.all(Array.from({length:concurrency},async(_,worker)=>{
  let i=worker;
  while(performance.now()<end){
   const now=performance.now(),kind=i++%10;
   const q=Object.values(today.questions)[i%6],args={date:today.date,revision:today.revision};
   let url=base+'/api/v1/today',options;
   if(kind<5)url=base+'/api/v1/questions/'+q.id+'/hints?'+new URLSearchParams({...args,q:['inter','unusual','Canada','river','Paris'][i%5]});
   else if(kind<8){url=base+'/api/v1/questions/'+q.id+'/answer';options={method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...args,raw:['Canada','cat','Blue','United States'][i%4]})}}
   else if(kind===8)url=base+'/api/v1/questions/'+q.id+'/catalogue?'+new URLSearchParams({...args,q:'',limit:120});
   try{const r=await fetch(url,options),body=await r.arrayBuffer();statuses[r.status]=(statuses[r.status]||0)+1;responseBytes+=body.byteLength;if(!r.ok)errors.push(r.status)}catch(e){errors.push(e.message)}
   requests++;latencies.push(performance.now()-now);
  }
 }));
 const elapsed=(performance.now()-start)/1000;latencies.sort((a,b)=>a-b);
 const result={kind:'local closed-loop mixed API benchmark, no TLS/CDN',date:new Date().toISOString(),node:process.version,cpu:os.cpus()[0].model,cpu_count:os.cpus().length,concurrency,elapsed_seconds:elapsed,requests,requests_per_second:requests/elapsed,error_count:errors.length,statuses,p50_ms:latencies[Math.floor(latencies.length*.5)],p95_ms:latencies[Math.floor(latencies.length*.95)],p99_ms:latencies[Math.floor(latencies.length*.99)],response_bytes:responseBytes,workload:'50% hints, 30% score, 10% catalogue first page, 10% daily; largest dictionary day; repeated queries; server process separate from load generator'};
 console.log(JSON.stringify(result,null,2));
 if(process.env.LOAD_REPORT)fs.writeFileSync(process.env.LOAD_REPORT,JSON.stringify(result,null,2)+'\n');
 if(errors.length)process.exitCode=1;
}finally{child?.kill('SIGTERM')}
