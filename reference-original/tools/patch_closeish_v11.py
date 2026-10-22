from pathlib import Path
from collections import Counter
import json,csv,zipfile,shutil,re,hashlib,math

SRC=Path('/mnt/data/CLOSEISH-V10-4-6-nap-javitott-projekt.zip')
WORK=Path('/mnt/data/closeish_v11_work')
if WORK.exists():shutil.rmtree(WORK)
WORK.mkdir()
with zipfile.ZipFile(SRC) as z:z.extractall(WORK)
ROOT=WORK/'CLOSEISH'
pack=json.loads((ROOT/'data-pack.json').read_text(encoding='utf-8'))
base_checksum=hashlib.sha256(json.dumps({k:pack[k] for k in ['1','2','3','4','6','7']},sort_keys=True,ensure_ascii=False).encode()).hexdigest()

# NEW RECORDS: copied from the source's shard 2/3/10/18; not fabricated.
# THIS IS AN EXPLICIT ADDITIONAL SUBSET, NOT THE FULL VGCHARTZ CATALOGUE.
GAME_INPUT={
2:'''Ratchet & Clank: Up Your Arsenal~2.57|Madden NFL 08~2.57|Clubhouse Games~3.45|NBA 2K14~2.57|Ratchet & Clank Future: Tools of Destruction~2.57|Hot Shots Golf~2.56|Dragon Age: Origins~2.56|FIFA 16~2.55|Pokémon Stadium 2~2.73|Madden NFL 09~2.54|Space Invaders~2.53|Crazy Taxi~2.52|Perfect Dark~2.52|Tomb Raider (2013)~2.51|Midnight Club: Los Angeles~2.5|PES 2009: Pro Evolution Soccer~2.5|Marvel: Ultimate Alliance~2.5|Black & White~0.04|Crisis Core: Final Fantasy VII~3.19|Dance Central~3.18|Diablo~1.59|Dragon Ball Z: Budokai 3~1.94|Dragon Quest II~2.56|Far Cry~0.05|Final Fantasy Tactics~2.45|Forza Horizon 3~3.93|Warcraft III: The Frozen Throne~1.54|Rise of the Tomb Raider~0.15|Rockstar Games Double Pack: Grand Theft Auto III & Grand Theft Auto Vice City~2.49|NBA 2K15~2.49|Game Party~2.49|Mortal Kombat: Deadly Alliance~2.49|Dungeon Defenders~0.02|Dark Souls III~2.42|Mario Party 2~2.5|Saints Row: The Third~2.48|Tomb Raider: The Last Revelation~2.48|Assassin's Creed Origins~2.47|Pure~2.47|Rock Band~2.47|Minecraft~2.47|Battlefield 1942~0.03|Paper Mario: Sticker Star~2.41|WarioWare Touched!~2.3|Resistance 2~2.47|Batman: Arkham City~0.52|Madden NFL 16~2.47|Mario Party 4~2.47|Dying Light~2.45|LEGO Harry Potter: Years 1-4~2.45|uDraw Studio~2.44|Madden NFL 17~2.44|Twisted Metal 2~2.44|The Sims: Bustin' Out~2.43|Need for Speed Carbon: Own the City~2.42|Ice Hockey~2.42|Sonic Adventure~2.42|Tom Clancy's Rainbow Six: Vegas 2~2.42|God of War Collection~2.6|Kinect: Disneyland Adventures~2.41|Pro Evolution Soccer 2011~2.41|ATV Offroad Fury~2.41|Pokémon Colosseum~2.54|NBA 2K16~2.41|Halo: Combat Evolved Anniversary~2.41|Need for Speed: ProStreet~2.41|Tetris Plus~2.4|Forza Motorsport 5~2.4|Midnight Club: Los Angeles~2.4|Command & Conquer: Tiberian Sun~1.55|Dino Crisis~2.41|Final Fantasy V~2.45|Monster Hunter Freedom 2~2.58|Naruto Shippuden: Ultimate Ninja Storm 4~1.54|Pro Wrestling~2.4|Theme Hospital~2.4|Madden NFL 11~2.4|Batman: Arkham Origins~2.4|Frogger's Adventures: Temple of the Frog~2.39|Zumba Fitness~2.39''',
3:'''Shadow The Hedgehog~0.6|FIFA Soccer 08~1.35|The Simpsons: Hit & Run~1.35|FIFA Soccer 09~1.35|Watch Dogs 2~1.35|SingStar Party~1.35|FIFA Soccer 08~1.35|Test Drive~1.34|Tom Clancy's Rainbow Six: Vegas 2~1.34|Devil May Cry 4~1.34|F1 2010~1.34|Mortal Kombat 3~1.34|The Legend of Zelda: Tri Force Heroes~1.24|Doom 3~1.34|The ICO & Shadow of the Colossus Collection~1.34|Donkey Kong Jungle Beat~1.34|Need for Speed Carbon~1.34|Battlefield: Bad Company~1.34|Command & Conquer: Red Alert 2~1.34|Max Payne 2: The Fall of Max Payne~1.34|MVP Baseball 2004~1.34|Ratchet & Clank: Up Your Arsenal (Weekly american sales)~1.33|WWE 2K18~1.33|Crysis 2~1.33|Saints Row IV~1.33|Alan Wake~1.33|Spider-Man: The Movie~1.33|Ni no Kuni: Wrath of the White Witch~1.54|Tales of Xillia~1.25|The Sims: Bustin' Out~1.33|Tony Hawk's Pro Skater~1.33|WWF War Zone~1.33|Triple Play 2001~1.33|Corvette~1.33|Grand Theft Auto: Chinatown Wars~1.33|WWE SmackDown vs Raw 2008~1.33|Skylanders Giants~1.32|UFC Undisputed 2010~1.32|Fallout 76~1.32|Need for Speed Underground Rivals~1.32|Gyromite~1.32|TOCA 2 Touring Car Championship~1.32|Petz Wild Animals: Dolphinz~1.32|MAG: Massive Action Game~1.32|NFL 2K3~1.32|Fighting Force~1.32|Resident Evil 6~0.04|Madden NFL 97~1.32|Rage~1.32|The LEGO Movie Videogame~1.32|TNN Motor Sports Hardcore 4x4~1.31|FIFA 14~1.31|Thief~0.11|IHRA Drag Racing 2~1.31|Lego Star Wars: The Force Awakens~1.31|Nintendo Labo: Toy-Con 01 Variety Kit~1.12|Madagascar~1.31|Rugrats Studio Tour~1.31|LEGO Batman: The Videogame~1.31|Pitfall II: Lost Caverns~1.31|[Prototype]~1.31|Turok: Evolution~1.31|The Beatles: Rock Band~1.31|EA Sports UFC 2~1.31|Burnout 3: Takedown~1.31|Adventure~1.3|Yu-Gi-Oh! The Sacred Cards~1.3|NBA Live 07~1.3|SingStar '80s~1.3|LEGO Batman: The Videogame~1.3|Devil May Cry 3: Dante's Awakening~2.09|Dragon Quest IV: Michibikareshi Monotachi~1.21|Final Fantasy X / X-2 HD Remaster~1.3|Final Fantasy: Crystal Chronicles~1.49|Kingdom Hearts 3D: Dream Drop Distance~1.6|Kingdom Hearts HD II.8 Final Chapter Prologue~1.2|Monster Hunter Freedom~1.34|Resident Evil: The Umbrella Chronicles~1.52|Romancing SaGa 3~1.3|SaGa Frontier~1.35''',
10:'''Tiger Woods PGA Tour~0.21|NHL 2K3~0.21|Yarudora Series Vol. 2: Kisetsu wo Dakishimete~0.21|Heisei Kyouiku linkai DS~0.21|Discovery Kids: Pony Paradise~0.21|SpongeBob SquarePants: Game Boy Advance Video Volume 3~0.21|Pro Yakyuu Spirits 2010~0.21|Final Fight One~0.21|Gallop Racer 2003: A New Breed~0.21|BeyBlade VForce: Super Tournament Battle~0.21|Outlaw Golf 2~0.21|LBX: Little Battlers eXperience~0.21|Bugs Bunny & Taz: Time Busters~0.21|Dragon Ball Z: Sagas~0.21|Jikkyou Powerful Pro Yakyuu 2012~0.21|Wedding Dash~0.21|X2: Wolverine's Revenge~0.21|Power Rangers: Wild Force~0.21|Dragon Quest Monsters: Joker 3 - Professional~0.2|Mary-Kate and Ashley: Girls Night Out~0.2|The King of Fighters '95~0.2|Castlevania: Lords of Shadow 2~0.2|LEGO Harry Potter: Years 5-7~0.2|Kingdom Hearts: The Story So Far~0.2|Beyblade G-Revolution~0.2|Jillian Michaels' Fitness Adventure~0.2|Disney Art Academy~0.2|Trade & Battle: Card Hero~0.2|EVE Online~0.2|World Championship Cards~0.2|Code of Princess~0.2|Capcom Fighting Evolution~0.2|Mobile Suit Gundam: Crossfire~0.2|Godzilla (2015)~0.2|SD Gundam GNext~0.2|Backyard NFL Football 2006~0.2|Thrillville~0.2|NASCAR Heat 2002~0.2|Sloane to MacHale no Nazo no Monogatari~0.2|Sengoku Basara 2 Heroes~0.2|Buzz! The Schools Quiz~0.2|Suikoden Tactics~0.2|NCAA March Madness 06~0.2|Pillars of Eternity II: Deadfire~0.0|Phantasy Star Online~0.2|Crazy Taxi 3: High Roller~0.2|Midnight Club 3: DUB Edition Remix~0.2|International Superstar Soccer 2000~0.2|CandyLand / Chutes & Ladders / Memory~0.2|Kung Fu Rider~0.2|The Amazing Spider-Man (2012)~0.2|The Bible Game~0.2|Major League Baseball 2K11~0.2|Drift King Shutokou Battle '94~0.2|Shining Blade~0.2|Need for Speed Carbon: Own the City~0.2|The Ultimate Red Ball Challenge~0.2|PBR: Out of the Chute~0.2|The King of Fighters Collection: The Orochi Saga~0.2|Jikkyou Powerful Pro Yakyuu 10 Chou Ketteiban: 2003 Memorial~0.2|Port Royale 3~0.01|We Sing Robbie Williams~0.2|Enchanted Arms~0.2|Major League Baseball 2K12~0.2|Saturday Night Speedway~0.2|CSI: Deadly Intent~0.2|Bratz: Rock Angelz~0.2|Langrisser III~0.2|MLB SlugFest 20-03~0.2|Samurai Spirits (CD)~0.2|Eagle Flight~0.2|Pitfall: The Lost Expedition~0.2|Deal or No Deal: The Banker is Back!~0.2|From TV Animation One Piece: Grand Battle! 3~0.2|Rocket Power: Zero Gravity Zone~0.2|Le Mans 24 Hours~0.2|ESPN MLB Baseball~0.2|Shrek: Forever After~0.2|All Star Pro-Wrestling~0.2|Dragon Ball Z: Harukanaru Densetsu~0.2''',
18:'''Disney's Hide & Sneak~0.03|Nobunaga no Yabou: Kakushin with Power-Up Kit~0.03|Super Robot Taisen OG Saga: Masou Kishin III - Pride of Justice~0.03|Farming 2017 - The Simulation~0.03|Raw Danger!~0.03|Legend of the Dragon~0.03|Monster Rancher Hop-A-Bout~0.03|Custom Beat Battle: Draglade 2~0.03|de Blob 2~0.03|Gotouchi Kenkei DS~0.03|Astonishia Story~0.03|Transformers: Devastation~0.03|BikkuriMan Daijiten~0.03|Bikkuriman Daijiten~0.03|Accel World: Ginyoku no Kakusei~0.03|Elf Bowling 1 & 2~0.03|NBA 2K17~0.03|Maximum Racing: GP Classic Racing~0.03|GunGriffon: Allied Strike~0.03|WRC 5: FIA World Rally Championship~0.03|Stacked with Daniel Negreanu~0.03|Vitamin X Evolution~0.03|Mahjong 300~0.03|Saru! Get You! SaruSaru Daisakusen~0.03|Sea Park Tycoon~0.03|Arthur and the Invisibles~0.03|Dynasty Warriors: Godseekers~0.03|Black Mirror~0.03|PopCap Arcade Vol 2~0.03|The Flintstones: Big Trouble in Bedrock~0.03|SUPERBEAT: XONiC~0.03|Sorcery Saga: Curse of the Great Curry God~0.03|Beastly~0.03|Sekai no Hate Made Itte Q! Chinjuu Hunter Mono no Daibouken~0.03|Smart Girl's Winter Wonderland~0.03|Majesty 2: The Fantasy Kingdom Sim~0.03|Silverlicious~0.03|Zoo Tycoon~0.03|BeatMania IIDX 14 Gold~0.03|Pure Farming 2018~0.03|Railway Empire~0.03|Trials Fusion~0.03|Big Ichigeki! Pachi-Slot Taikouryku Universal Museum~0.03|Toriko: Ultimate Survival~0.03|Vegas Casino~0.03|Madou Monogatari~0.03|River City Super Sports Challenge~0.03|Flipper Critters~0.03|Onna no Ko to Misshitsu ni Itara **shichau Kamoshirenai~0.03|Togainu no Chi: True Blood~0.03|Tork: Prehistoric Punk~0.03|Call of Juarez: Bound in Blood~0.03|Chicken Shoot 2~0.03|Shin Hayarigami 2~0.03|Prince of Persia: The Forgotten Sands~0.03|Summer Athletics 2009~0.03|Apache: Air Assault~0.03|Underground Pool~0.03|Infinite Stratos 2: Ignition Hearts~0.03|Pachinko Kamen Rider: Shocker Zenmetsu Daisakusen~0.03|Accel World: Ginyoku no Kakusei~0.03|Classic Dungeon: Fuyoku no Masoujin~0.03|Crazy Machines~0.03|Mystery Case Files: Ravenhearst~0.03|Rampo~0.03|The Sims 2: Glamour Life Stuff~0.03|Super Heroine Chronicle~0.03|My Pet Shop (JP sales)~0.03|Toy Shop~0.03|Darkest Dungeon~0.03|Exstetra~0.03|Kung Fu Panda: Showdown of Legendary Legends~0.03|Dodge Racing: Charger vs Challenger~0.03|Gokujou!! Mecha Mote Iinchou: MM My Best Friend!~0.03|Biker Mice From Mars~0.03|Jig-A-Pix: Wild World~0.03|Winning Post 8 2016~0.03|IDOLiSH7 Twelve Fantasia!~0.03|Hiiro no Kakera 2: Hisui no Shizuku~0.03|Rugby World Cup 2015~0.03'''
}
# Distinct waterfall names & heights, cited Cascadyas entries, merged into the historic 41-row list.
FALLS='''Victoria Falls|108;Niagara Falls|57;Iguaçu Falls|82;Dettifoss|44;Rhine Falls|23;Kaieteur Falls|226;Jog Falls|253;Gullfoss|32;Khone Phapheng Falls|21;Augrabies Falls|56;Krimml Waterfalls|380;Murchison Falls|43;Goðafoss|12;Kegon Falls|97;Seljalandsfoss|65;Blue Nile Falls|42;Kalandula Falls|105;Skógafoss|62;Huangguoshu Waterfall|78;Ouzoud Falls|110;Ruacana Falls|120;Svartifoss|20;Selfoss|44;Glymur|190;Epupa Falls|20;Shivanasamudra Falls|98;Kalambo Falls|235;Seven Sisters waterfall|410;Nachi Falls|133;Horsetail Fall|650;Jägala Waterfall|8;Ban Gioc–Detian Falls|30;Vøringfossen|184;Maletsunyane Falls|192;Aldeyjarfoss|20;Horseshoe Falls|51;Kravica|28;Multnomah Falls|165;Kjeragfossen|715'''

TIERS={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD',0:'TOO FAR'}
def scored(q,v):
 gap=(v-q['limit'] if q['direction']=='above' else q['limit']-v)
 if gap<0:return 0,'CROSSED LIMIT'
 if gap==0:return 1200,'PERFECT HIT'
 for b in q['score_bands']:
  if gap<=b['max_gap_inclusive']:return b['points'],b['tier']
 return 0,'TOO FAR'

def sample_counts(q):return Counter(int(a['points']) for a in q['answers'])

q=pack['5']['q1']
# preserve all existing real records; avoid recomputing a platform maximum when the full multi-platform source isn't available
names={re.sub(r'\s+',' ',a['canonical'].strip()).casefold():a for a in q['answers']}
newgames=0
for shard,raw in GAME_INPUT.items():
 for item in raw.split('|'):
  name,nums=item.rsplit('~',1);name=name.strip();v=int(round(float(nums)*1000000));k=re.sub(r'\s+',' ',name).casefold()
  if not k or v<=0 or 'weekly' in k or 'american sales' in k or 'jp sales' in k:continue
  if k in names:continue
  # These are real source-listed game titles; the observation is one platform, not verified best across all platforms.
  a={'entity_id':'vgchartz-slice-'+hashlib.sha1(name.encode()).hexdigest()[:14], 'canonical':name,
     'aliases':[],'verified_status':'platform_snapshot_partial','source_refs':[{'source_id':'vgchartz2020-shard-'+str(shard),'locator':f'https://github.com/sayuen0/vggames-scraping/blob/master/data/20201003-012640/vgsales_{shard}.csv'}],
     'metric_value':v, 'points':0,'tier':'CROSSED LIMIT',
     'measurement_note':'At least one platform observation; complete best-platform comparison not established'}
  a['points'],a['tier']=scored(q,v)
  q['answers'].append(a);names[k]=a;newgames+=1
# old question's wording implies best platform; not verified for newly added observations so wording clarifies that source derives snapshot measurements.
q['prompt']='Name a video game that sold at least 14,640,000 copies on one gaming platform.'
q['source']='https://github.com/sayuen0/vggames-scraping/tree/master/data/20201003-012640'
q['metric']='Historical VGChartz platform-level sales estimates, copies, rounded to 10,000; partial import of documented games'
q['metric_provenance']='VGChartz-derived historical platform sales estimates; combined original 40 examples and documented 2020 shard excerpts; NOT a complete source or all platforms for all games.'
q['answer_scope']['claimed_exhaustive']=False
q['answer_scope']['coverage']='documented_sample_only_not_exhaustive'
q['answer_scope']['dataset_count']=len(q['answers'])
q['content_revision']='v11-day5-games-expanded-observations'
q['editorial_status']='RESEARCH_PREVIEW_NOT_COMPLETE'
q['score_distribution_audit']={str(p):sample_counts(q).get(p,0) for p in (1200,1000,800,600,400,200,0)}
q['verified_answer_count']=len(q['answers'])
q['catalogued_answer_count']=len(q['answers'])
q['recognized_category_candidate_count']=0

# Add verified Cascadyas waterfall measurements to existing 41 values.
fq=pack['5']['q2']
falls={x['canonical'].casefold():x for x in fq['answers']}
newfalls=0
for item in FALLS.split(';'):
 name,val=item.rsplit('|',1);name=name.strip();height=int(val)
 if name.casefold() in falls:continue
 a={'entity_id':'cascadyas-'+hashlib.sha1(name.encode()).hexdigest()[:14], 'canonical':name,'aliases':[],
  'verified_status':'source_snapshot','source_refs':[{'source_id':'cascadyas-falls-2026','locator':'https://www.cascadyas.com/find/'}],
  'metric_value':height}
 a['points'],a['tier']=scored(fq,height)
 fq['answers'].append(a);falls[name.casefold()]=a;newfalls+=1
fq['source']='https://www.cascadyas.com/find/'
fq['metric_provenance']='Named waterfall total heights (metres) from original tall-waterfall list and Cascadyas public 2026 atlas; not comprehensive worldwide.'
fq['answer_scope']['dataset_count']=len(fq['answers'])
fq['answer_scope']['claimed_exhaustive']=False
fq['answer_scope']['coverage']='two_documented_source_samples_only'
fq['editorial_status']='RESEARCH_PREVIEW_NOT_COMPLETE'
fq['content_revision']='v11-day5-waterfalls-expanded-source-measurements'
fq['score_distribution_audit']={str(p):sample_counts(fq).get(p,0) for p in (1200,1000,800,600,400,200,0)}
fq['verified_answer_count']=len(fq['answers'])
fq['catalogued_answer_count']=len(fq['answers'])

# Nile 1971–2026 as valid year identities but 0 GAME POINTS for no verified historical flow.
# It would be a serious scientific error to backfill missing annual discharge with zero flow.
nq=pack['5']['q6']
base_years={x['canonical'] for x in nq['answers']}
newyears=0
for year in range(1971,2027):
 if str(year) in base_years:continue
 nq.setdefault('recognized_category_candidates',[]).append({
  'entity_id':'nile-year-unverified-'+str(year),'canonical':str(year),'aliases':[],
  'membership_status':'eligible_calendar_year_without_verified_measurement',
  'verified_status':'year_exists_measurement_missing',
  'metric_value':None,'points':0,'tier':'NO VERIFIED DATA',
  'source_refs':[{'source_id':'nile-statsmodels-1871-1970','locator':'https://www.statsmodels.org/stable/datasets/generated/nile.html'}]})
 newyears+=1
nq['allow_unverified_year_zero']=True
nq['question_year_range']=[1871,2026]
nq['recognized_category_candidate_count']=len(nq['recognized_category_candidates'])
nq['catalogued_answer_count']=len(nq['answers'])+len(nq['recognized_category_candidates'])
nq['answer_scope']['claimed_exhaustive']=False
nq['answer_scope']['coverage']='1871_1970_measured_1971_2026_unmeasured_zero_game_points'
nq['measurement']['time_dependent']=True
nq['metric_provenance']='Measured annual flow from original Aswan 1871–1970 series. Years 1971–2026 are valid calendar entries, but no comparable verified value is present in the installed series; they earn 0 game points without implying zero discharge.'
nq['content_revision']='v11-day5-nile-extend-calendar-years-2026'
nq['editorial_status']='RESEARCH_PREVIEW_NOT_COMPLETE'

# Update audit counts/TSV, keep every earlier day unchanged, build standalone from V10 original shell.
for key,newname in [('q1','games'),('q2','falls')]:
 question=pack['5'][key]
 question['verified_answer_count']=len(question['answers'])
 question['catalogued_answer_count']=len(question['answers'])+len(question.get('recognized_category_candidates',[]))
 target=ROOT/'datasets'/('new-day5-'+newname+'.tsv')
 with target.open('w',encoding='utf8') as f:
  f.write('canonical\tmetric_value\tpoints\tstatus\n')
  for a in question['answers']:f.write(f"{a['canonical']}\t{a['metric_value']}\t{a['points']}\t{a['verified_status']}\n")
with (ROOT/'datasets'/'new-day5-nile.tsv').open('w',encoding='utf8') as f:
 f.write('year\tmetric_value\tgame_points\tstatus\n')
 for a in nq['answers']:f.write(f"{a['canonical']}\t{a['metric_value']}\t{a['points']}\tmeasured\n")
 for a in nq['recognized_category_candidates']:f.write(f"{a['canonical']}\tNA\t0\tUNVERIFIED_YEAR\n")

assert base_checksum==hashlib.sha256(json.dumps({k:pack[k] for k in ['1','2','3','4','6','7']},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
for key in ('q1','q2','q6'):
 question=pack['5'][key]
 for a in question['answers']:
  pp,tt=scored(question,a['metric_value'])
  assert (a['points'],a['tier'])==(pp,tt),(key,a['canonical'],a['points'],pp)
 counts=sample_counts(question)
 assert all(counts[k] for k in (1200,1000,800,600,400,200,0)),(key,counts)
 assert len({a['canonical'].casefold() for a in question['answers']})==len(question['answers'])

(ROOT/'days'/'day-05.json').write_text(json.dumps(pack['5'],ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'data-pack.json').write_text(json.dumps(pack,ensure_ascii=False,separators=(',',':')),encoding='utf8')
old=(ROOT/'CLOSEISH-standalone.html').read_text(encoding='utf8')
m=re.search(r'(<script id="pack-data" type="application/json">)(.*?)(</script>)',old,re.S)
assert m

# Surgical point-0 exception for a real calendar year without a scientifically verified discharge.
if "a.membership_status==='recognized_entity_unverified_measurement'||!Number.isFinite(a.metric_value)" in old:
 old=old.replace("if(a.membership_status==='recognized_entity_unverified_measurement'||!Number.isFinite(a.metric_value)){",
  "if(currentQ().allow_unverified_year_zero && a.membership_status==='eligible_calendar_year_without_verified_measurement'){\\n  finalize({raw,canonical:a.canonical,points:0,tier:'NO VERIFIED DATA',kind:'unverified',metric_value:null,reason:'No comparable Aswan annual flow measurement is available for this year; 0 game points, not zero river flow.',autoLocked:automatic});return;\\n }\\n if(a.membership_status==='recognized_entity_unverified_measurement'||!Number.isFinite(a.metric_value)){")
 old=old.replace('\\n','\n') if False else old
 # above explicit newline escape sequences, limited safe fix to JS just-inserted segment
 old=old.replace("{\\n  finalize({raw,canonical:a.canonical,points:0,tier:'NO VERIFIED DATA'", "{\n  finalize({raw,canonical:a.canonical,points:0,tier:'NO VERIFIED DATA'")
 old=old.replace("autoLocked:automatic});return;\\n }\\n if(a.membership_status", "autoLocked:automatic});return;\n }\n if(a.membership_status")
else:raise RuntimeError('Could not locate source measurement guard')
# show zero-point/no-data distinctly from a wrong answer
old=old.replace("invalid:'INELIGIBLE'};", "invalid:'INELIGIBLE',unverified:'NO VERIFIED DATA'};")
old=old.replace("r.kind==='review'?'PENDING REVIEW':", "r.kind==='review'?'PENDING REVIEW':r.kind==='unverified'?'NO VERIFIED DATA':")
old=old.replace("r.kind==='review'?'NEEDS REVIEW':", "r.kind==='review'?'NEEDS REVIEW':r.kind==='unverified'?'UNVERIFIED YEAR':")
# Keep unverified Nile calendar years in ALL and 0-point catalogue views.
old=old.replace("const pool=isOther?[...(q.recognized_category_candidates||[])]:[...sortedCatalog(q).filter(a=>(filter==='all'||String(a.points)===filter)),...(filter==='all'&&query?[...(q.recognized_category_candidates||[])]:[])];",
 "const pool=isOther?[...(q.recognized_category_candidates||[])]:[...sortedCatalog(q).filter(a=>(filter==='all'||String(a.points)===filter)),...(q.allow_unverified_year_zero&&(filter==='all'||filter==='0')?[...(q.recognized_category_candidates||[])]:(!q.allow_unverified_year_zero&&filter==='all'&&query?[...(q.recognized_category_candidates||[])]:[]))];")
# make no data displayed as a legitimate catalogue alternative, with 0 pt and explicit unavailable measurement
old=old.replace("${Number.isFinite(a.metric_value)?displayMeasure(q,a.metric_value)+' '+escapeHTML(unitLabel(q)):'NOT MEASURED'}", "${Number.isFinite(a.metric_value)?displayMeasure(q,a.metric_value)+' '+escapeHTML(unitLabel(q)):'NO VERIFIED DATA'}")
old=old.replace("${Number.isFinite(a.metric_value)?a.points:'—'}", "${a.membership_status==='eligible_calendar_year_without_verified_measurement'?'0':(Number.isFinite(a.metric_value)?a.points:'—')}")
# More precise no-data status in catalogue
old=old.replace("${(isOther||!Number.isFinite(a.metric_value))?`<small class=\"ab-eligibility\">MEASUREMENT PENDING</small>`:''}",
    "${(isOther||!Number.isFinite(a.metric_value))?`<small class=\"ab-eligibility\">${a.membership_status==='eligible_calendar_year_without_verified_measurement'?'NO VERIFIED ANNUAL FLOW · 0 PTS':'MEASUREMENT PENDING'}</small>`:''}")
# replace pack inline, preserve CSS and previous V10 UI
m=re.search(r'(<script id="pack-data" type="application/json">)(.*?)(</script>)',old,re.S)
payload=json.dumps(pack,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
html=old[:m.start(2)]+payload+old[m.end(2):]
assert "allow_unverified_year_zero" in html and "unverified:'NO VERIFIED DATA'" in html
outfile=Path('/mnt/data/CLOSEISH-V11-bovitett-jatekok-vizesesek-nilus.html')
outfile.write_text(html,encoding='utf8')
(ROOT/'CLOSEISH-standalone.html').write_text(html,encoding='utf8')
# rebuild script shell with the new JS, not previous V8 feature loss
m=re.search(r'(<script id="pack-data" type="application/json">)(.*?)(</script>)',html,re.S)
(ROOT/'tools'/'shell-v8.html').write_text(html[:m.start(2)]+html[m.end(2):],encoding='utf8')

summary={'version':'V11','video_games':{'before':40,'new':newgames,'now':len(q['answers']),'full_corpus':False},'waterfalls':{'before':41,'new':newfalls,'now':len(fq['answers']),'full_corpus':False},'nile':{'measured':len(nq['answers']),'unverified_years_new':newyears,'total_identified_years':len(nq['answers'])+newyears,'coverage':'1871–1970 actually measured; 1971–2026 no verified comparable measurement; 0 game points'}}
report='''# CLOSEISH V11 — a 5. nap három adatbankjának bővítése

**Fontos: NEM teljes, publikálásra kész adatlefedettség.** Az importált valós részhalmazt bővítettem, nem állítom, hogy a 11 ezer+ videojátékot vagy az összes vízesést beimportáltam.

## Rekordok

- Videojátékok: {before_g} → {after_g} ellenőrizhetően forrásban szereplő cím (új: {new_g}).
- Vízesések: {before_f} → {after_f} név és mért magasság (új: {new_f}).
- Nílus: 100 dokumentált év (1871–1970) + 56 későbbi év (1971–2026) felismerhető. Az utóbbiak teljes éves, összehasonlítható mérési adata NINCS a telepített sorozatban. Ha ilyen év a válasz, 0 játékpontot ad, „NO VERIFIED DATA” jelzéssel. Nem tulajdonít a Nílusnak nulla tényleges vízhozamot.

## Módszertani figyelmeztetések

A videojátékoknál a különböző platformokon kiadott játékok teljes összevetéséhez a VGChartz teljes, történeti platformadatbázisának importja szükséges. Az egyes importált platformos adatok ezért részmérések lehetnek. A 2020-as adatok nem a 2026-os aktuális eladásokat jelzik. A vízesések magassága az atlaszokban eltérhet a mérési módszer miatt; a játék kiinduló 41-es adatbankját és a Cascadyas online atlaszának további, ténylegesen dokumentált sorait egyesítettem. Az Aszuán 1871–1970-es adatsorához más mérőállomás modern mérését nem keverem.

## Források

- https://github.com/sayuen0/vggames-scraping/tree/master/data/20201003-012640
- https://www.cascadyas.com/find/
- https://www.statsmodels.org/stable/datasets/generated/nile.html

## Megőrzött tartalom

Az 1–4., 6. és 7. nap kérdés- és válaszadatbankjának JSON-ja változatlan. A módosított 5. napi források offline is be vannak ágyazva a HTML-be.
'''.format(before_g=40,after_g=len(q['answers']),new_g=newgames,before_f=41,after_f=len(fq['answers']),new_f=newfalls)
report_path=Path('/mnt/data/CLOSEISH-V11-adatlefedettseg-es-audit.md');report_path.write_text(report,encoding='utf8')
(ROOT/'docs'/'V11-LEFEDETTSEG.md').write_text(report,encoding='utf8')
(ROOT/'RELEASE-STATUS-2026-10-22.json').write_text(json.dumps({'build':'V11','modified_day':5,'publishable':False,'full_category_coverage':False,**summary},indent=2,ensure_ascii=False),encoding='utf8')
(ROOT/'docs'/'V11-ADATDARABSZAMOK.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(Path(__file__),ROOT/'tools'/'patch_closeish_v11.py')
shutil.copy2(Path('/mnt/data/test_closeish_v11.py'),ROOT/'tools'/'test_closeish_v11.py')
zippath=Path('/mnt/data/CLOSEISH-V11-bovitett-jatekok-vizesesek-nilus-projekt.zip')
with zipfile.ZipFile(zippath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,arcname='CLOSEISH/'+str(p.relative_to(ROOT)))
print(json.dumps(summary,ensure_ascii=False,indent=2))
print(outfile, outfile.stat().st_size, zippath, zippath.stat().st_size)
