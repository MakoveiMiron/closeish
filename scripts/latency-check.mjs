/* External latency tracer. Never requests unpublished data, writes no DB rows. */
const origin=(process.argv[2]||process.env.API_ORIGIN||'').replace(/\/+$/,'');
if(!/^https?:\/\//.test(origin)){console.error('Usage: node scripts/latency-check.mjs https://api.example.com [UUID]');process.exit(1)}
const playerId=process.argv[3]||process.env.PLAYER_ID||'';
for(let i=0;i<8;i++){
 const tasks=[['today','/api/v1/today'],...(playerId?[['progress','/api/v1/progress?playerId='+encodeURIComponent(playerId)]]:[])];
 for(const [name,path] of tasks){
  const t=performance.now();try{
   const r=await fetch(origin+path,{headers:{'Accept-Encoding':'gzip'}});await r.arrayBuffer();
   console.log(JSON.stringify({trial:i+1,endpoint:name,status:r.status,clientMs:+(performance.now()-t).toFixed(1),app:r.headers.get('server-timing'),cache:r.headers.get('cache-control')}));
  }catch(e){console.log(JSON.stringify({trial:i+1,endpoint:name,error:e.message}))}
 }
}
