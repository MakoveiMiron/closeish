import {loadContent} from './content.mjs';
const days=loadContent();
const questionCount=[...days.values()].reduce((n,d)=>n+d.questions.length,0);
console.log(JSON.stringify({valid:true,days:days.size,questions:questionCount}));
