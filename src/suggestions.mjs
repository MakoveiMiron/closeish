/** Anonymous question-idea inbox. Public interface is WRITE ONLY. */
export function validateSuggestion(input){
  if(!input||typeof input!=='object'||Array.isArray(input))return null;
  if(Object.keys(input).some(key=>!['question','direction'].includes(key)))return null;
  if(typeof input.question!=='string'||typeof input.direction!=='string')return null;
  const question=input.question.trim().replace(/\r\n?/g,'\n');
  if(question.length<8||question.length>350||/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(question))return null;
  if(!['below','above'].includes(input.direction))return null;
  return {question,direction:input.direction};
}
export class PgSuggestionStore {
  constructor(pool){this.pool=pool;this.mode='postgres'}
  async create({question,direction}){
    await this.pool.query('INSERT INTO question_suggestions (question, direction) VALUES ($1,$2)',[question,direction]);
  }
  async ready(){await this.pool.query('SELECT 1 FROM question_suggestions LIMIT 0')}
}
/** Test-only store: never use as durable production storage. */
export class MemorySuggestionStore {
  constructor(){this.mode='memory';this.items=[]}
  async create(item){this.items.push({...item})}
  async ready(){}
}
