import pg from 'pg';
export function createPool(env=process.env){
  if(!env.DATABASE_URL)throw new Error('DATABASE_URL is required');
  const max=Number(env.PG_POOL_MAX||10);
  if(!Number.isInteger(max)||max<1||max>100)throw new Error('PG_POOL_MAX must be 1–100');
  if(env.PG_SSL_MODE&&!['disable','verify-full'].includes(env.PG_SSL_MODE))throw new Error('PG_SSL_MODE must be disable or verify-full');
  const pool=new pg.Pool({connectionString:env.DATABASE_URL,max,connectionTimeoutMillis:5000,idleTimeoutMillis:30000,
    statement_timeout:10000,query_timeout:12000,application_name:'closeish-api',
    ...(env.PG_SSL_MODE==='disable'?{ssl:false}:env.PG_SSL_MODE==='verify-full'?{ssl:{rejectUnauthorized:true,...(env.PG_SSL_CA?{ca:env.PG_SSL_CA.replace(/\\n/g,'\n')}:{})}}:{})});
  pool.on('error',error=>console.error(JSON.stringify({event:'postgres_idle_error',code:error.code||'UNKNOWN'})));
  return pool;
}
