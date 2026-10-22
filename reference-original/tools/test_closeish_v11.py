from playwright.sync_api import sync_playwright
from pathlib import Path
import time
html=Path('/mnt/data/CLOSEISH-V11-bovitett-jatekok-vizesesek-nilus.html').read_text(encoding='utf8')
start=time.time()
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1280,'height':900})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html,wait_until='domcontentloaded',timeout=110000)
 page.locator('[data-modal="archive"]').first.click()
 page.locator('[data-day="5"]').click()
 page.locator('#startBtn').click()
 print('DAY5 ACTIVE',page.locator('.question-title').inner_text(),flush=True)
 for i in range(5):
  page.locator('#skipBtn').click(timeout=20000)
  page.locator('#nextBtn').click(timeout=20000)
 print('NILE PROMPT',page.locator('.question-title').inner_text(),flush=True)
 # type 2026, first enter selects completion, second submits
 page.locator('#guess').fill('2026')
 page.locator('#answerForm').evaluate('(e)=>e.requestSubmit()')
 if page.locator('.question-title').count():
  page.locator('#answerForm').evaluate('(e)=>e.requestSubmit()')
 print('REVEAL',page.locator('body').inner_text()[-900:],flush=True)
 if page.locator('#nextBtn').count():page.locator('#nextBtn').click(timeout=25000)
 print('END SCREEN',page.locator('.end-screen').count(),flush=True)
 if page.locator('.end-screen').count():
  page.locator('[data-open-book="0"]').click(timeout=25000)
  print('GAMES COUNT',page.locator('[data-count="0"]').inner_text(),flush=True)
  page.locator('#bookBack').click()
  page.locator('[data-open-book="1"]').click(timeout=25000)
  print('FALLS COUNT',page.locator('[data-count="1"]').inner_text(),flush=True)
  page.locator('#bookBack').click()
  page.locator('[data-open-book="5"]').click(timeout=25000)
  if page.locator('[data-filter="5:other"]').count():
   page.locator('[data-filter="5:other"]').click()
   print('NILE COUNT',page.locator('[data-count="5"]').inner_text(),flush=True)
   print('NILE ROW',page.locator('[data-rows="5"]').inner_text()[-220:],flush=True)
 print('ERRORS',errors[:5], 'elapsed',round(time.time()-start,1),flush=True)
 b.close()
