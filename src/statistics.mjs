export function calculateStats(rows,own=null){
  const counts=new Map(rows.map(row=>[Number(row.score),Number(row.count)]));
  const histogram=Array.from({length:37},(_,i)=>({score:i*200,count:counts.get(i*200)||0}));
  const total=histogram.reduce((sum,x)=>sum+x.count,0),sum=histogram.reduce((n,x)=>n+x.score*x.count,0);
  function quantile(p){if(!total)return null;let n=0;for(const row of histogram){n+=row.count;if(n>=Math.ceil(total*p))return row.score}return 7200}
  const lower=own?histogram.reduce((n,x)=>n+(x.score<own.score?x.count:0),0):null;
  const equal=own?(counts.get(own.score)||0)-1:null;
  const others=own?Math.max(0,total-1):total;
  return {histogram,total,mean:total?sum/total:null,q25:quantile(.25),median:quantile(.5),q75:quantile(.75),
    comparison:own?{score:own.score,others,lower,equal:Math.max(0,equal),higher:Math.max(0,others-lower-Math.max(0,equal)),
      betterThanPercent:others>0?100*lower/others:null}:null};
}
export class PgStatsStore {
  constructor(pool){this.pool=pool;this.mode='postgres'}
  async ready(){await this.pool.query('SELECT 1 FROM daily_results LIMIT 0');await this.pool.query('SELECT 1 FROM daily_score_counts LIMIT 0')}
  async record(value){
    const shard=parseInt(value.playerHash.slice(0,8),16)%32;
    // One atomic SQL statement: only a genuinely new completion increments its counter.
    await this.pool.query(`WITH inserted AS (
      INSERT INTO daily_results(game_date,player_hash,content_revision,run_id,score)
      VALUES($1,$2,$3,$4,$5) ON CONFLICT(game_date,player_hash) DO NOTHING
      RETURNING game_date,content_revision,score
    ) INSERT INTO daily_score_counts(game_date,content_revision,score,shard,player_count)
      SELECT game_date,content_revision,score,$6,1 FROM inserted
      ON CONFLICT(game_date,content_revision,score,shard) DO UPDATE
      SET player_count=daily_score_counts.player_count+1`,[value.date,value.playerHash,value.revision,value.runId,value.score,shard]);
    return this.find(value.date,value.playerHash);
  }
  async find(date,playerHash){
    const result=await this.pool.query('SELECT content_revision AS revision,run_id AS "runId",score,completed_at AS "completedAt" FROM daily_results WHERE game_date=$1 AND player_hash=$2',[date,playerHash]);
    return result.rows[0]||null;
  }
  async aggregate(date,revision){
    const result=await this.pool.query('SELECT score,SUM(player_count)::bigint AS count FROM daily_score_counts WHERE game_date=$1 AND content_revision=$2 GROUP BY score ORDER BY score',[date,revision]);
    return result.rows;
  }
  async close(){await this.pool.end()}
}
// Explicit local testing only. Never selected automatically, never allowed in production.
export class MemoryStatsStore {
  constructor(){this.mode='memory';this.results=new Map()}
  async ready(){}
  async record(value){const key=value.date+':'+value.playerHash;if(!this.results.has(key))this.results.set(key,{...value,completedAt:new Date()});return this.results.get(key)}
  async find(date,hash){return this.results.get(date+':'+hash)||null}
  async aggregate(date,revision){const counts=new Map();for(const row of this.results.values())if(row.date===date&&row.revision===revision)counts.set(row.score,(counts.get(row.score)||0)+1);return [...counts].map(([score,count])=>({score,count}))}
  async close(){}
}
export function createStatistics(store,{cacheMs=10000}={}){
  const cache=new Map(),inflight=new Map();
  async function snapshot(date,revision,force=false){
    const key=date+':'+revision,hit=cache.get(key);
    if(!force&&hit&&Date.now()-hit.at<cacheMs)return hit;
    // A completion requires a snapshot started after its commit, not an older in-flight read.
    if(force&&inflight.has(key))await inflight.get(key);
    if(!inflight.has(key))inflight.set(key,(async()=>{
      const rows=await store.aggregate(date,revision),value={rows,at:Date.now()};
      if(cache.size>=32)cache.delete(cache.keys().next().value);cache.set(key,value);return value;
    })().finally(()=>inflight.delete(key)));
    return inflight.get(key);
  }
  async function get(date,revision,playerHash,{force=false,own:knownOwn}={}){
    const own=knownOwn===undefined?await store.find(date,playerHash):knownOwn;
    const comparable=own?.revision===revision?own:null;
    let snap=await snapshot(date,revision,force);
    if(!force&&comparable&&new Date(comparable.completedAt).getTime()>=snap.at-cacheMs)snap=await snapshot(date,revision,true);
    return {...calculateStats(snap.rows,comparable),date,revision,asOf:new Date(snap.at).toISOString(),mode:store.mode,
      official:own?{score:own.score,revision:own.revision,runId:own.runId,completedAt:own.completedAt}:null};
  }
  async function record(value){const own=await store.record(value);return get(value.date,own.revision,value.playerHash,{force:true,own})}
  return {get,record};
}
