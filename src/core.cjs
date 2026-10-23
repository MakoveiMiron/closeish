/* EDGE data rules. No network calls, rendering, timers or stored scores. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.CLOSEISHCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const TIERS={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'};
  const START='2026-10-23',END='2026-10-29',DAY_MS=86400000;
  const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/ß/g,'ss').replace(/œ/g,'oe').replace(/ð/g,'d').replace(/þ/g,'th').replace(/đ/g,'d').replace(/ı/g,'i').replace(/ø/g,'o').replace(/ł/g,'l').replace(/æ/g,'ae').replace(/&/g,' and ').replace(/c\+\+/g,' cplusplus ').replace(/c#/g,' csharp ').replace(/f#/g,' fsharp ').replace(/[^a-z0-9]+/g,' ').trim();
  // Decimal comparison avoids floating-point boundary drift (e.g. 0.3 - 0.1).
  function decimal(n){
    if(typeof n!=='number'||!Number.isFinite(n))throw new TypeError('Expected a finite number');
    const [s,e='0']=String(n).toLowerCase().split('e');
    const places=(s.split('.')[1]||'').length;
    return {n:BigInt(s.replace('.','')),scale:places-Number(e)};
  }
  function align(values){
    const parts=values.map(decimal),scale=Math.max(...parts.map(x=>x.scale));
    return parts.map(x=>x.n*10n**BigInt(scale-x.scale));
  }
  function score(q,value){
    if(!Number.isFinite(value))return {points:0,tier:'UNVERIFIED',kind:'review'};
    if(!['above','below'].includes(q.direction))throw new Error('Invalid direction');
    // Whole-% questions compare the rounded percent, never a hidden decimal.
    if(q.unit==='%')value=Math.floor(value+0.5);
    const bands=q.score_bands;
    if(q.unit==='%'&&!Number.isInteger(q.limit))throw new Error('Percent scoring target must be an integer');
    if(!Number.isFinite(q.limit)||!Array.isArray(bands)||bands.length!==5||bands.some((b,i)=>!Number.isFinite(b.max_gap_inclusive)||b.max_gap_inclusive<=0||b.points!==[1000,800,600,400,200][i]||(i>0&&b.max_gap_inclusive<=bands[i-1].max_gap_inclusive)))throw new Error('Invalid score bands');
    const [limit,v,...edges]=align([q.limit,value,...bands.map(x=>x.max_gap_inclusive)]);
    const gap=q.direction==='above'?v-limit:limit-v;
    if(gap<0n)return {points:0,tier:'CROSSED LIMIT',kind:'over'};
    if(gap===0n)return {points:1200,tier:TIERS[1200],kind:'scored'};
    const i=edges.findIndex(edge=>gap<=edge);
    return i<0?{points:0,tier:'TOO FAR',kind:'far'}:{points:bands[i].points,tier:TIERS[bands[i].points],kind:'scored'};
  }
  const indexes=new WeakMap();
  function index(q){
    if(indexes.has(q))return indexes.get(q);
    const result=new Map();
    for(const ent of [...q.answers,...(q.recognized_category_candidates||[])]){
      const id=ent.entity_id||ent.canonical;
      for(const [s,isAlias]of [[ent.canonical,false],...(ent.aliases||[]).map(a=>[a.input,true])]){
        const key=norm(s);if(!key)continue;
        const rows=result.get(key)||[];
        if(!rows.some(row=>(row.ent.entity_id||row.ent.canonical)===id))rows.push({ent,isAlias});
        result.set(key,rows);
      }
    }
    indexes.set(q,result);return result;
  }
  function invalidate(q){indexes.delete(q)}
  function exact(q,raw){
    const hits=index(q).get(norm(raw))||[];
    return hits.length===1?{status:'found',match:{...hits[0],match:'exact'}}:{status:hits.length?'ambiguous':'unknown'};
  }
  // Only eligible entities enter the answer index. Known outside-scope entities
  // are recognized solely to reject an exact submission with a clear reason.
  function excludedExact(q,raw){
    const key=norm(raw);
    if(!key)return {status:'unknown'};
    const hits=(q.excluded_answers||[]).filter(ent=>
      norm(ent.canonical)===key||(ent.aliases||[]).some(alias=>norm(alias.input)===key));
    return hits.length===1?{status:'ineligible',ent:hits[0]}:
      hits.length>1?{status:'ambiguous'}:{status:'unknown'};
  }
  function isoTime(iso){
    if(typeof iso!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(iso))throw new Error('Expected YYYY-MM-DD');
    const ms=Date.parse(iso+'T00:00:00Z');
    if(!Number.isFinite(ms)||new Date(ms).toISOString().slice(0,10)!==iso)throw new Error('Invalid calendar date');
    return ms;
  }
  function dayNumber(iso){return Math.floor((isoTime(iso)-isoTime(START))/DAY_MS)+1;}
  function dateForDay(n){if(!Number.isInteger(n)||(n<1||n>7))throw new Error('Available days are 1–7');return new Date(isoTime(START)+(n-1)*DAY_MS).toISOString().slice(0,10);}
  function questions(day){return day?Array.from({length:6},(_,i)=>day['q'+(i+1)]):[];}
  function progressKey(data,n){
    const revisions=questions(data[String(n)]).filter(Boolean).filter(q=>q.content_revision).map(q=>q.id+':'+q.content_revision);
    return String(n)+(revisions.length?'@'+revisions.join('|'):'');
  }
  return {TIERS,START,END,norm,score,index,invalidate,exact,excludedExact,dayNumber,dateForDay,questions,progressKey};
});
