import http from 'k6/http';
import {check} from 'k6';
// OWN STAGING ONLY. This creates real result rows: never run against production data.
const RATE=Number(__ENV.RATE||1200),COMPLETIONS=Number(__ENV.COMPLETIONS_PER_SECOND||20);
export const options={
 scenarios:{
  browsing:{executor:'constant-arrival-rate',exec:'browse',rate:RATE,timeUnit:'1s',duration:__ENV.DURATION||'10m',preAllocatedVUs:200,maxVUs:2000},
  completions:{executor:'constant-arrival-rate',exec:'finish',rate:COMPLETIONS,timeUnit:'1s',duration:__ENV.DURATION||'10m',preAllocatedVUs:40,maxVUs:400}
 },
 thresholds:{http_req_failed:['rate<0.001'],http_req_duration:['p(95)<300','p(99)<1000'],dropped_iterations:['count==0'],checks:['rate>0.999']}
};
const uuid=()=> 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.floor(Math.random()*16);return(c==='x'?r:(r&3)|8).toString(16)});
const json={headers:{'Content-Type':'application/json'}};
export function setup(){
 if(!__ENV.BASE_URL||__ENV.CONFIRM_STAGING!=='yes')throw new Error('Set BASE_URL and CONFIRM_STAGING=yes for an isolated staging database');
 const boot=http.get(__ENV.BASE_URL+'/api/v1/today').json();
 if(!boot.available||boot.statistics!=='postgres')throw new Error('A current daily set and real PostgreSQL statistics are required');
 return boot;
}
export function browse(boot){
 const base=__ENV.BASE_URL,q=Object.values(boot.questions)[Math.floor(Math.random()*6)],kind=Math.random();
 const words=['inter','blue','river','United','Paris','San','new','Saint','Lincoln','1912'];
 const text=words[Math.floor(Math.random()*words.length)],common=`date=${boot.date}&revision=${boot.revision}`;
 let r;
 if(kind<.65)r=http.get(`${base}/api/v1/questions/${q.id}/hints?${common}&q=${encodeURIComponent(text)}`);
 else if(kind<.75)r=http.get(`${base}/api/v1/questions/${q.id}/catalogue?${common}&q=${encodeURIComponent(text)}&limit=120`);
 else if(kind<.85)r=http.post(base+'/api/v1/statistics',JSON.stringify({date:boot.date,revision:boot.revision,playerId:uuid()}),json);
 else r=http.get(base+'/api/v1/today');
 check(r,{'browse HTTP 200':x=>x.status===200});
}
export function finish(boot){
 const playerId=uuid(),runId=uuid(),receipts=[],base=__ENV.BASE_URL;
 for(const q of Object.values(boot.questions)){
  const r=http.post(base+'/api/v1/questions/'+q.id+'/answer',JSON.stringify({date:boot.date,revision:boot.revision,playerId,runId,raw:'',kind:'skipped'}),json);
  if(!check(r,{'signed score HTTP 200':x=>x.status===200}))return;
  receipts.push(r.json().result.receipt);
 }
 const body=JSON.stringify({date:boot.date,revision:boot.revision,playerId,runId,receipts});
 const r=http.post(base+'/api/v1/results',body,json);check(r,{'completion HTTP 200':x=>x.status===200});
 // Retry a subset to exercise the unique constraint under pressure.
 if(Math.random()<.1)check(http.post(base+'/api/v1/results',body,json),{'retry HTTP 200':x=>x.status===200});
}
