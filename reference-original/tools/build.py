"""Recreate the exact standalone V8/V9 app from source question JSONs."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def build():
 data={str(i):json.loads((ROOT/'days'/f'day-{i:02}.json').read_text(encoding='utf8')) for i in range(1,8)}
 for d,questions in data.items():
  assert list(questions)==[f'q{i}' for i in range(1,7)],d
 text=(ROOT/'tools/shell-v8.html').read_text(encoding='utf8')
 packed=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
 assert '<script id="pack-data" type="application/json"></script>' in text
 text=text.replace('<script id="pack-data" type="application/json"></script>','<script id="pack-data" type="application/json">'+packed+'</script>',1)
 (ROOT/'CLOSEISH-standalone.html').write_text(text,encoding='utf8')
 (ROOT/'data-pack.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('Built seven days, 42 questions')
if __name__=='__main__':build()
