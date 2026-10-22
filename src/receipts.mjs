import crypto from 'node:crypto';
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
export const clientError=(message,code='INVALID_RESULT',status=400)=>Object.assign(new Error(message),{status,code});
export function createReceipts({secret,playerSecret,clock=()=>new Date()}) {
  if(!secret||secret.length<32||!playerSecret||playerSecret.length<32)throw new Error('Signing and player hash secrets must each have at least 32 characters');
  const mac=value=>crypto.createHmac('sha256',secret).update(value).digest('base64url');
  function playerHash(id){if(typeof id!=='string'||!uuid.test(id))throw clientError('A random UUID v4 playerId is required');return crypto.createHmac('sha256',playerSecret).update('closeish-player:'+id.toLowerCase()).digest('hex')}
  function run(id){if(typeof id!=='string'||!uuid.test(id))throw clientError('A UUID v4 runId is required');return id.toLowerCase()}
  function issue({playerId,runId,date,revision,questionId,points}) {
    const data={v:1,p:playerHash(playerId),run:run(runId),d:date,r:revision,q:questionId,s:points,exp:clock().getTime()+72*3600000};
    const encoded=Buffer.from(JSON.stringify(data)).toString('base64url');return encoded+'.'+mac(encoded);
  }
  function verify(token){
    if(typeof token!=='string'||token.length>1500)throw clientError('Invalid score receipt');
    const parts=token.split('.');if(parts.length!==2)throw clientError('Invalid score receipt');
    const expected=Buffer.from(mac(parts[0])),actual=Buffer.from(parts[1]);
    if(expected.length!==actual.length||!crypto.timingSafeEqual(expected,actual))throw clientError('Score receipt signature is invalid');
    let value;try{value=JSON.parse(Buffer.from(parts[0],'base64url').toString())}catch{throw clientError('Score receipt is malformed')}
    if(value.v!==1||!Number.isFinite(value.exp)||value.exp<clock().getTime())throw clientError('Score receipt expired','RECEIPT_EXPIRED');
    if(!Number.isInteger(value.s)||value.s<0||value.s>1200||value.s%200)throw clientError('Invalid receipt score');
    return value;
  }
  function completion(input){
    const hash=playerHash(input.playerId),runId=run(input.runId);
    if(!Array.isArray(input.receipts)||input.receipts.length!==6)throw clientError('Exactly six signed receipts are required');
    const receipts=input.receipts.map(verify),first=receipts[0];
    if(new Set(receipts.map(x=>x.q)).size!==6)throw clientError('Repeated question receipt');
    if(receipts.some(x=>x.p!==hash||x.run!==runId||x.d!==first.d||x.r!==first.r))throw clientError('Receipts must belong to the same player, run, day and content revision');
    if(input.date!==first.d||input.revision!==first.r)throw clientError('Result date or revision mismatch');
    return {date:first.d,revision:first.r,playerHash:hash,runId,score:receipts.reduce((sum,x)=>sum+x.s,0),questionIds:receipts.map(x=>x.q)};
  }
  return {issue,completion,playerHash,run};
}
