import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createPool} from './database.mjs';
export async function migrate(pool){
  const client=await pool.connect();
  try{
    await client.query("SET lock_timeout='15s'");
    await client.query('SELECT pg_advisory_lock(817062214)');
    await client.query('CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY, sha256 text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())');
    const directory=new URL('../migrations/',import.meta.url);
    for(const file of fs.readdirSync(directory).filter(x=>x.endsWith('.sql')).sort()){
      const sql=fs.readFileSync(new URL(file,directory),'utf8'),hash=crypto.createHash('sha256').update(sql).digest('hex');
      const found=await client.query('SELECT sha256 FROM schema_migrations WHERE name=$1',[file]);
      if(found.rows.length){if(found.rows[0].sha256!==hash)throw new Error('Applied migration was modified: '+file);continue}
      await client.query('BEGIN');
      try{await client.query(sql);await client.query('INSERT INTO schema_migrations(name,sha256) VALUES($1,$2)',[file,hash]);await client.query('COMMIT');console.log('Applied migration '+file)}
      catch(error){await client.query('ROLLBACK');throw error}
    }
  }finally{try{await client.query('SELECT pg_advisory_unlock(817062214)')}finally{client.release()}}
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
  const pool=createPool();
  try{await migrate(pool)}catch(error){console.error('Migration failed:',error.code||error.message);process.exitCode=1}finally{await pool.end()}
}
