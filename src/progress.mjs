/* A day's signed/server-scored answers are append-only. The browser may update
   the active round but never alter recorded answers or unlock a completed day. */
export function publicProgress(row) {
  if(!row)return null;
  const responses=Array.isArray(row.responses)?row.responses:JSON.parse(row.responses||'[]');
  const completed=responses.length===6;
  return {date:row.date instanceof Date?row.date.toISOString().slice(0,10):String(row.date).slice(0,10),
    revision:row.revision,runId:row.runId,responses,completed,
    activeRound:completed?null:row.activeRound,activeDeadline:completed?null:(row.activeDeadline?new Date(row.activeDeadline).getTime():null),
    phase:completed?'end':row.phase,updatedAt:new Date(row.updatedAt).getTime()};
}
export class PgProgressStore {
  constructor(pool){this.pool=pool;this.mode='postgres'}
  async ready(){await this.pool.query('SELECT 1 FROM player_progress LIMIT 0')}
  async one(date,hash){
    const {rows}=await this.pool.query(`SELECT game_date AS date,content_revision AS revision,
      run_id AS "runId",responses,active_round AS "activeRound",active_deadline AS "activeDeadline",phase,updated_at AS "updatedAt"
      FROM player_progress WHERE game_date=$1 AND player_hash=$2`,[date,hash]);
    return publicProgress(rows[0]);
  }
  async month(month,hash){
    const {rows}=await this.pool.query(`SELECT game_date::text AS date,content_revision AS revision,
      jsonb_array_length(responses) AS answers,updated_at AS "updatedAt"
      FROM player_progress WHERE player_hash=$1 AND game_date>=$2::date AND game_date<($2::date + INTERVAL '1 month') ORDER BY game_date`,[hash,month+'-01']);
    return rows.map(r=>({date:r.date,revision:r.revision,answers:Number(r.answers),completed:Number(r.answers)===6,updatedAt:new Date(r.updatedAt).getTime()}));
  }
  async milestone({date,hash,revision,runId,activeRound,activeDeadline,phase}){
    const {rows}=await this.pool.query(`INSERT INTO player_progress(player_hash,game_date,content_revision,run_id,active_round,active_deadline,phase)
      VALUES($1,$2,$3,$4,$5,$6,$7)
      ON CONFLICT(player_hash,game_date) DO UPDATE SET
        active_round=CASE WHEN jsonb_array_length(player_progress.responses)<6
          AND jsonb_array_length(player_progress.responses)=EXCLUDED.active_round
          AND (player_progress.active_round IS NULL OR EXCLUDED.active_round>=player_progress.active_round)
          THEN EXCLUDED.active_round ELSE player_progress.active_round END,
        active_deadline=CASE WHEN jsonb_array_length(player_progress.responses)<6
          AND jsonb_array_length(player_progress.responses)=EXCLUDED.active_round
          AND (player_progress.active_round IS NULL OR EXCLUDED.active_round>=player_progress.active_round)
          THEN COALESCE(player_progress.active_deadline,EXCLUDED.active_deadline) ELSE player_progress.active_deadline END,
        phase=CASE WHEN jsonb_array_length(player_progress.responses)=6 THEN 'end'
          WHEN EXCLUDED.phase='play' AND jsonb_array_length(player_progress.responses)=EXCLUDED.active_round THEN 'play' ELSE player_progress.phase END,
        updated_at=now()
      WHERE player_progress.content_revision=EXCLUDED.content_revision AND player_progress.run_id=EXCLUDED.run_id
      RETURNING game_date AS date,content_revision AS revision,run_id AS "runId",responses,
        active_round AS "activeRound",active_deadline AS "activeDeadline",phase,updated_at AS "updatedAt"`,
      [hash,date,revision,runId,activeRound,activeDeadline?new Date(activeDeadline):null,phase]);
    if(!rows.length)throw Object.assign(new Error('A different run is already registered for this day'),{status:409,code:'DAY_ALREADY_STARTED'});
    return publicProgress(rows[0]);
  }
  async answer({date,hash,revision,runId,round,response}){
    const serialized=JSON.stringify([response]);
    // A zero-row INSERT ... SELECT would never execute ON CONFLICT for rounds 1–5.
    // Round 0 may create the row; every later round must UPDATE an existing row.
    const returning=`RETURNING game_date AS date,content_revision AS revision,run_id AS "runId",responses,
      active_round AS "activeRound",active_deadline AS "activeDeadline",phase,updated_at AS "updatedAt"`;
    const sql=round===0?
      `INSERT INTO player_progress(player_hash,game_date,content_revision,run_id,responses,phase)
        VALUES($1,$2,$3,$4,$5::jsonb,'reveal')
        ON CONFLICT(player_hash,game_date) DO UPDATE SET
          responses=CASE WHEN jsonb_array_length(player_progress.responses)=0
            THEN player_progress.responses || EXCLUDED.responses ELSE player_progress.responses END,
          active_round=CASE WHEN jsonb_array_length(player_progress.responses)=0 THEN NULL ELSE player_progress.active_round END,
          active_deadline=CASE WHEN jsonb_array_length(player_progress.responses)=0 THEN NULL ELSE player_progress.active_deadline END,
          phase=CASE WHEN jsonb_array_length(player_progress.responses)=0 THEN 'reveal' ELSE player_progress.phase END,
          updated_at=now()
        WHERE player_progress.content_revision=EXCLUDED.content_revision AND player_progress.run_id=EXCLUDED.run_id
        ${returning}`:
      `UPDATE player_progress SET
         responses=CASE WHEN jsonb_array_length(responses)=$6 THEN responses || $5::jsonb ELSE responses END,
         active_round=CASE WHEN jsonb_array_length(responses)=$6 THEN NULL ELSE active_round END,
         active_deadline=CASE WHEN jsonb_array_length(responses)=$6 THEN NULL ELSE active_deadline END,
         phase=CASE WHEN jsonb_array_length(responses)=$6 THEN
           CASE WHEN $6=5 THEN 'end' ELSE 'reveal' END ELSE phase END,
         updated_at=now()
       WHERE player_hash=$1 AND game_date=$2 AND content_revision=$3 AND run_id=$4
       ${returning}`;
    const args=round===0?[hash,date,revision,runId,serialized]:[hash,date,revision,runId,serialized,round];
    const {rows}=await this.pool.query(sql,args);
    if(!rows.length)throw Object.assign(new Error('A different run is already registered for this day'),{status:409,code:'DAY_ALREADY_STARTED'});
    const result=publicProgress(rows[0]);
    if(result.responses.length<round+1)throw Object.assign(new Error('A previous answer is missing'),{status:409,code:'ROUND_OUT_OF_ORDER'});
    return result;
  }
  async import({date,hash,revision,runId,responses}){
    const {rows}=await this.pool.query(`INSERT INTO player_progress(player_hash,game_date,content_revision,run_id,responses,phase)
       VALUES($1,$2,$3,$4,$5::jsonb,$6)
       ON CONFLICT(player_hash,game_date) DO NOTHING RETURNING player_hash`,
      [hash,date,revision,runId,JSON.stringify(responses),responses.length===6?'end':'reveal']);
    return {imported:rows.length>0,progress:await this.one(date,hash)};
  }
}
// In-memory implementation exists for deterministic local API tests only.
export class MemoryProgressStore {
  constructor(){this.mode='memory';this.rows=new Map()}
  async ready(){}
  key(date,hash){return hash+':'+date}
  async one(date,hash){return publicProgress(this.rows.get(this.key(date,hash))||null)}
  async month(month,hash){return [...this.rows.values()].filter(x=>x.date.startsWith(month)&&x.hash===hash).map(({date,revision,responses,updatedAt})=>({date,revision,answers:responses.length,completed:responses.length===6,updatedAt}))}
  async milestone({date,hash,revision,runId,activeRound,activeDeadline,phase}){
    const key=this.key(date,hash);let r=this.rows.get(key);
    if(!r){r={date,hash,revision,runId,responses:[],activeRound:null,activeDeadline:null,phase:'intro',updatedAt:Date.now()};this.rows.set(key,r)}
    if(r.revision!==revision||r.runId!==runId)throw Object.assign(new Error('Run locked'),{status:409,code:'DAY_ALREADY_STARTED'});
    if(r.responses.length<6&&r.responses.length===activeRound&&(r.activeRound===null||activeRound>=r.activeRound)){
      r.activeRound=activeRound;r.activeDeadline=r.activeDeadline||activeDeadline;
      r.phase=phase;
    }
    r.updatedAt=Date.now();return r;
  }
  async answer({date,hash,revision,runId,round,response}){
    let r=await this.milestone({date,hash,revision,runId,activeRound:round,activeDeadline:null,phase:'play'});
    if(r.responses.length===round){r.responses.push(response);r.phase=r.responses.length===6?'end':'reveal';r.activeRound=null;r.activeDeadline=null}
    if(r.responses.length<round+1)throw Object.assign(new Error('Missing round'),{status:409,code:'ROUND_OUT_OF_ORDER'});
    r.updatedAt=Date.now();return {...r,completed:r.responses.length===6};
  }
  async import({date,hash,revision,runId,responses}){
    const key=this.key(date,hash);if(!this.rows.has(key))this.rows.set(key,{date,hash,revision,runId,responses,phase:responses.length===6?'end':'reveal',activeRound:null,activeDeadline:null,updatedAt:Date.now()});
    return {imported:this.rows.get(key).runId===runId,progress:await this.one(date,hash)};
  }
}
