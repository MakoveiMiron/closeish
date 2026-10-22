// Dependency-free ZIP writer (standard DEFLATE, UTF-8 paths, CRC32).
import fs from 'node:fs';
import path from 'node:path';
import {deflateRawSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {loadContent} from '../src/content.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),content=path.join(root,'content');
const days=loadContent();
const index=[...days.values()].flatMap(({day,questions})=>questions.map(({q})=>({date:day.date,id:q.id,topic:q.topic,prompt:q.prompt,direction:q.direction,limit:q.limit,unit:q.unit,answers:q.answers.length,content_revision:q.content_revision})));
fs.writeFileSync(path.join(content,'question-index.json'),JSON.stringify(index,null,2)+'\n');
const table=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0});
function crc32(buffer){let crc=0xffffffff;for(const byte of buffer)crc=table[(crc^byte)&255]^(crc>>>8);return (crc^0xffffffff)>>>0}
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):e.isFile()?[path.join(dir,e.name)]:[])}
const local=[],central=[];let offset=0;
for(const file of files(content)) {
 const name=Buffer.from('content/'+path.relative(content,file).split(path.sep).join('/'));
 const raw=fs.readFileSync(file),compressed=deflateRawSync(raw,{level:9}),crc=crc32(raw);
 const header=Buffer.alloc(30);header.writeUInt32LE(0x04034b50);header.writeUInt16LE(20,4);header.writeUInt16LE(0x800,6);header.writeUInt16LE(8,8);header.writeUInt16LE(0x21,12);header.writeUInt32LE(crc,14);header.writeUInt32LE(compressed.length,18);header.writeUInt32LE(raw.length,22);header.writeUInt16LE(name.length,26);
 const entry=Buffer.alloc(46);entry.writeUInt32LE(0x02014b50);entry.writeUInt16LE(20,4);entry.writeUInt16LE(20,6);entry.writeUInt16LE(0x800,8);entry.writeUInt16LE(8,10);entry.writeUInt16LE(0x21,14);entry.writeUInt32LE(crc,16);entry.writeUInt32LE(compressed.length,20);entry.writeUInt32LE(raw.length,24);entry.writeUInt16LE(name.length,28);entry.writeUInt32LE(offset,42);
 local.push(header,name,compressed);central.push(entry,name);offset+=header.length+name.length+compressed.length;
}
const directory=Buffer.concat(central),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50);end.writeUInt16LE(central.length/2,8);end.writeUInt16LE(central.length/2,10);end.writeUInt32LE(directory.length,12);end.writeUInt32LE(offset,16);
const destination=path.join(root,'CLOSEISH-kerdescsomag-AI.zip');fs.writeFileSync(destination,Buffer.concat([...local,directory,end]));
console.log(`Created ${destination} (${fs.statSync(destination).size} bytes, ${index.length} questions)`);
