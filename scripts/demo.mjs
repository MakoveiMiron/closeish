// Local demo only. All actual scoring remains in the separately running backend.
if(process.env.NODE_ENV==='production')throw new Error('Demo date override is forbidden in production');
process.env.DEV_DATE='2026-10-23';
const {spawn}=await import('node:child_process');
const {fileURLToPath}=await import('node:url');
const root=fileURLToPath(new URL('../',import.meta.url));
const child=spawn(process.execPath,['--env-file-if-exists=.env','src/server.mjs'],{cwd:root,env:process.env,stdio:'inherit'});
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>child.kill(signal));
child.on('exit',code=>{process.exitCode=code??0});
