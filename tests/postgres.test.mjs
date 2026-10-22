/* Use a disposable database. TEST_DATABASE_URL=... node --test tests/postgres.test.mjs
   Optional local SQL engine: PGLITE_MODULE=/absolute/path/to/@electric-sql/pglite/dist/index.js
   PGlite validates actual SQL but is NOT a network/pool/concurrent PostgreSQL load test. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {randomUUID} from 'node:crypto';
import {createPool} from '../src/database.mjs';
import {migrate} from '../src/migrate.mjs';
import {PgStatsStore,createStatistics} from '../src/statistics.mjs';
const enabled=!!(process.env.TEST_DATABASE_URL||process.env.PGLITE_MODULE);
test('actual PostgreSQL SQL: migrations, atomic counters, uniqueness, rollback, two stores', {skip:!enabled},async()=>{
 let pool;
 if(process.env.PGLITE_MODULE){
  const {PGlite}=await import(process.env.PGLITE_MODULE),db=new PGlite();
  const query=async(sql,args)=>{if(!args&&sql.includes(';')){const results=await db.exec(sql);return results.at(-1)}return db.query(sql,args)};
  pool={query,connect:async()=>({query,release(){}}),end:()=>db.close()};
 }else pool=createPool({...process.env,DATABASE_URL:process.env.TEST_DATABASE_URL});
 try{
  await migrate(pool);await migrate(pool);
  assert.equal(Number((await pool.query('SELECT count(*) FROM schema_migrations')).rows[0].count),1);
  const a=new PgStatsStore(pool),b=new PgStatsStore(pool),stats=createStatistics(a,{cacheMs:0});await a.ready();
  const date='2099-01-01',revision='a'.repeat(24),hash=randomUUID().replaceAll('-','').repeat(2),runId=randomUUID();
  const value={date,revision,playerHash:hash,runId,score:200};
  await Promise.all(Array.from({length:24},(_,i)=>(i%2?a:b).record(value)));
  assert.equal(Number((await a.aggregate(date,revision)).find(x=>Number(x.score)===200).count),1);
  await b.record({...value,score:7200,runId:randomUUID()});assert.equal((await a.find(date,hash)).score,200);
  await b.record({...value,playerHash:'f'.repeat(64),score:0});
  let result=await stats.get(date,revision,hash);assert.equal(result.total,2);assert.equal(result.comparison.betterThanPercent,100);
  // Force the counter insert to fail: the completion insert must roll back with it.
  await pool.query('ALTER TABLE daily_score_counts ADD CONSTRAINT test_reject_400 CHECK(score<>400)');
  const failedHash='e'.repeat(64);
  await assert.rejects(a.record({...value,playerHash:failedHash,score:400}));assert.equal(await a.find(date,failedHash),null);
  await pool.query('ALTER TABLE daily_score_counts DROP CONSTRAINT test_reject_400');
  await assert.rejects(a.record({...value,playerHash:failedHash,score:123}));
  await b.record({...value,playerHash:failedHash,revision:'b'.repeat(24),score:400});
  result=await stats.get(date,revision,hash);assert.equal(result.total,2);
  const audit=await pool.query(`SELECT r.game_date,r.content_revision,r.score FROM
   (SELECT game_date,content_revision,score,count(*)::bigint AS n FROM daily_results GROUP BY 1,2,3) r
   FULL JOIN (SELECT game_date,content_revision,score,sum(player_count)::bigint AS n FROM daily_score_counts GROUP BY 1,2,3) c
   USING(game_date,content_revision,score) WHERE r.n IS DISTINCT FROM c.n`);
  assert.equal(audit.rows.length,0);
  await pool.query('DELETE FROM daily_results WHERE game_date=$1',[date]);await pool.query('DELETE FROM daily_score_counts WHERE game_date=$1',[date]);
 }finally{await pool.end()}
});
