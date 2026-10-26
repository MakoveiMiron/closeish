"""Rebuild 2026-11-02/03 fixed, fully enumerated question banks and CSVs.
V23: never run this when a production day has already been played. Frozen source editions.
Does not touch any existing day or production code.
"""
from pathlib import Path
import json,csv,re,collections,unicodedata,hashlib
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'days'; SNAP=ROOT/'source-snapshots'

def parse(text,delimiter='|'):
  return [(v[0].strip(),float(v[1]) if '.' in v[1] else int(v[1]),[s.strip() for s in (v[2] if len(v)>2 else '').split(';') if s.strip()]) for line in text.strip().splitlines() if (v:=[p.strip() for p in line.split(delimiter)])]

def fromcsv(f):
  with open(SNAP/f,encoding='utf-8-sig',newline='') as fh:
    return [(r['canonical'],int(r['metric_value']),[]) for r in csv.DictReader(fh)]

# All 37 plays in the Open Source Shakespeare 'plays by number of words' source,
# NOT '38 plays' from a different edition (Two Noble Kinsmen is absent in this source).
shakespeare=parse('''Hamlet|30557
Richard III|29278
Coriolanus|27589
Cymbeline|27565
Othello|26450
King Lear|26145
Henry V|26119
Troilus and Cressida|26089
Henry IV, Part II|25689|Henry IV Part 2
Henry VI, Part II|25439|Henry VI Part 2
The Winter's Tale|24914|Winter's Tale
Antony and Cleopatra|24905
Henry VIII|24629
Henry IV, Part I|24579|Henry IV Part 1
Romeo and Juliet|24545
Henry VI, Part III|24294|Henry VI Part 3
All's Well That Ends Well|23009
Richard II|22423
The Merry Wives of Windsor|21845|Merry Wives of Windsor
Measure for Measure|21780
As You Like It|21690
Henry VI, Part I|21607|Henry VI Part 1
Love's Labour's Lost|21459
The Merchant of Venice|21291|Merchant of Venice
Much Ado About Nothing|21157
The Taming of the Shrew|21055|Taming of the Shrew
King John|20772
Titus Andronicus|20743
Twelfth Night|19837
Julius Caesar|19703
Pericles|18529
Timon of Athens|18216
The Two Gentlemen of Verona|17129|Two Gentlemen of Verona
Macbeth|17121
The Tempest|16633|Tempest
A Midsummer Night's Dream|16511|Midsummer Night's Dream
The Comedy of Errors|14701|Comedy of Errors''')
shakespeare=[(n,int(Decimal(v/1000).quantize(Decimal('1'),rounding=ROUND_HALF_UP))*1000,a) for n,v,a in shakespeare]

# All 21 stages *as actually raced*. Stage 19 was shortened on 24 July 2025
# from the originally announced 129.9 km to 93.1 km; official result uses 93.1.
tour=parse('''Stage 1|184.9|Stage 01
Stage 2|209.1|Stage 02
Stage 3|178.3|Stage 03
Stage 4|174.2|Stage 04
Stage 5|33.0|Stage 05
Stage 6|201.5|Stage 06
Stage 7|197.0|Stage 07
Stage 8|171.4|Stage 08
Stage 9|174.1|Stage 09
Stage 10|165.3
Stage 11|156.8
Stage 12|180.6
Stage 13|10.9
Stage 14|182.6
Stage 15|169.3
Stage 16|171.5
Stage 17|160.4
Stage 18|171.5
Stage 19|93.1
Stage 20|184.2
Stage 21|132.3''')
# Published 712-occupant historical tally; note that alternative reconstructions disagree.
boats=parse('''Lifeboat 1|12|Boat 1
Lifeboat 2|18|Boat 2
Lifeboat 3|32|Boat 3
Lifeboat 4|30|Boat 4
Lifeboat 5|36|Boat 5
Lifeboat 6|24|Boat 6
Lifeboat 7|28|Boat 7
Lifeboat 8|27|Boat 8
Lifeboat 9|40|Boat 9
Lifeboat 10|57|Boat 10
Lifeboat 11|50|Boat 11
Lifeboat 12|41|Boat 12
Lifeboat 13|55|Boat 13
Lifeboat 14|40|Boat 14
Lifeboat 15|66|Boat 15
Lifeboat 16|52|Boat 16
Collapsible A|13|Collapsible Boat A
Collapsible B|28|Collapsible Boat B
Collapsible C|43|Collapsible Boat C
Collapsible D|20|Collapsible Boat D''')
prefix=fromcsv('bipm-24-si-prefixes.csv')
hotels_text='''Capella Bangkok
Passalacqua
Rosewood Hong Kong
Cheval Blanc
The Upper House
Raffles Singapore
Aman Tokyo
Soneva Fushi
Atlantis The Royal
Nihi Sumba
Claridge's
Mandarin Oriental Bangkok
Raffles London at The OWO
Four Seasons Bangkok at Chao Phraya River
Hôtel de Crillon
Chablé Yucatán
Hotel du Cap-Eden-Roc
Maroma
Four Seasons Firenze
Borgo Santandrea
Desa Potato Head
Bulgari Tokyo
The Lana
Rosewood São Paulo
The Calile
The Siam
Park Hyatt Kyoto
Mount Nelson
One&Only Mandarina
The Carlyle
La Mamounia
Four Seasons Madrid
Capella Singapore
Four Seasons at The Surf Club
Hotel Bel-Air
Eden Rock
Aman New York
Royal Mansour
Amangalla
Le Bristol
Gleneagles
Castello di Reschio
Suján Jawai
Singita – Kruger National Park
Six Senses Zighy Bay
The Connaught
The Brando
Hotel Esencia
The Tasman
Kokomo Private Island'''
hotels=[(n.strip(),i,[]) for i,n in enumerate(hotels_text.splitlines(),1)]
moons=parse('''Cordelia|26
Ophelia|30
Bianca|42
Juliet|62
Desdemona|54
Rosalind|84
Portia|108
Cressida|54
Belinda|66
Puck|154
Miranda|472
Ariel|1158
Umbriel|1172
Titania|1580
Oberon|1524''')

buildings=parse('''Burj Khalifa|828
Menara Merdeka Maybank|679|Merdeka 118
Shanghai Tower|632
Makkah Royal Clock Tower|601
Ping An Finance Center|599
Lotte World Tower|555
One World Trade Center|541
Guangzhou CTF Finance Centre|530
Tianjin CTF Finance Centre|530
CITIC Tower|528|China Zun
TAIPEI 101|508|Taipei 101
Shanghai World Financial Center|492
International Commerce Centre|484
Wuhan Greenland Center|476
Central Park Tower|472
Lakhta Center|462
Vincom Landmark 81|461|Landmark 81
The Exchange 106|454
Changsha IFS Tower T1|452
Petronas Twin Tower 1|452|Petronas Tower 1
Petronas Twin Tower 2|452|Petronas Tower 2
Suzhou IFS|450
Zifeng Tower|450
Wuhan Tower|443
Willis Tower|442|Sears Tower
KK100|442
Guangzhou International Finance Center|439
111 West 57th Street|435
One Vanderbilt Avenue|427
432 Park Avenue|426
Marina 101|425
Trump International Hotel & Tower|423|Trump International Hotel and Tower Chicago
Minying International Trade Center T2|423
Jin Mao Tower|421
Princess Tower|413
Al Hamra Tower|413
Two International Finance Centre|412
LCT The Sharp Landmark Tower|412
Guangxi China Resources Tower|403
Guiyang International Financial Center T1|401
Iconic Tower|394
China Resources Tower|393
23 Marina|392
CITIC Plaza|390
CITYMARK CENTRE|388
Shum Yip Upperhills Tower 1|388
30 Hudson Yards|387
PIF Tower|385
Shun Hing Square|384
Eton Place Dalian Tower 1|383''')

films_text='''Shrek
Spirited Away
Finding Nemo
The Incredibles
Wallace & Gromit: The Curse of the Were-Rabbit
Happy Feet
Ratatouille
WALL-E
Up
Toy Story 3
Rango
Brave
Frozen
Big Hero 6
Inside Out
Zootopia
Coco
Spider-Man: Into the Spider-Verse
Toy Story 4
Soul
Encanto
Guillermo del Toro's Pinocchio
The Boy and the Heron
Flow
KPop Demon Hunters'''
films=[(n,y,['Wall·E','Wall E'] if n=='WALL-E' else ['Pinocchio (2022)'] if 'del Toro' in n else []) for y,n in enumerate(films_text.splitlines(),2001)]
# October 2026 TIOBE top 20, rates as printed (2 decimal points).
languages=parse('''Python|19.23
C|11.33
C++|8.87
Java|8.41
C#|3.79
JavaScript|2.77
Visual Basic|2.20
R|2.06
SQL|1.97
Rust|1.44
Go|1.39|Golang
PHP|1.26
Fortran|1.12
Swift|1.03
Scratch|0.97
COBOL|0.89
Perl|0.88
Julia|0.88
Delphi/Object Pascal|0.83|Delphi;Object Pascal
MATLAB|0.83''')
chrom_raw='''1 248956422
2 242193529
3 198295559
4 190214555
5 181538259
6 170805979
7 159345973
8 145138636
9 138394717
10 133797422
11 135086622
12 133275309
13 114364328
14 107043718
15 101991189
16 90338345
17 83257441
18 80373285
19 58617616
20 64444167
21 46709983
22 50818468
X 156040895
Y 57227415'''
chrom=[]
for line in chrom_raw.splitlines():
  n,bp=line.split(); v=int((Decimal(bp)/Decimal('1000000')).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
  chrom.append(('Chromosome '+n,v,['chr'+n,n] if n in 'XY' else ['chr'+n, 'Chromosome '+n]))
# Snapshot top-50 ONLY from year-end 2025 (not weekly year-end mix).
songs_text='''APT.
Die With A Smile
Birds Of A Feather
Ordinary
Beautiful Things
Lose Control
That's So True
Luther
Espresso
Golden
Not Like Us
Timeless
Wildflower
DTMF
A Bar Song (Tipsy)
Sailor Song
Messy
Good Luck, Babe!
Si Antes Te Hubiera Conocido
Taste
Who
Baile Inolvidable
Pink Pony Club
Too Sweet
Please Please Please
I Had Some Help
Bad Dreams
Save Your Tears
Iris
The Door
The Night We Met
TV Off
Abracadabra
Sweater Weather
Back To Friends
No One Noticed
Gata Only
Nuevayol
One Of The Girls
Yellow
All The Stars
Every Breath You Take
Creep
La Plena (W Sound 05)
Tu Boda
We Can't Be Friends (Wait For Your Love)
Cruel Summer
Perfect
like JENNIE
Viva La Vida'''
songs=[(n,i,['APT'] if i==1 else ['TV Off (feat. Lefty Gunplay)'] if n=='TV Off' else []) for i,n in enumerate(songs_text.splitlines(),1)]
# Frozen 30-entry table, from 2021 Journeyz ranking. Depths have variation among survey sources;
# only this cited 30-entry edition/metric is represented, never all worldwide lakes.
lakes=parse('''Lake Baikal|1642|Baikal
Lake Tanganyika|1470|Tanganyika
Caspian Sea|1025|Caspian
Lake Vostok|1000|Vostok
O'Higgins Lake|836|O'Higgins/San Martín Lake;Lago O'Higgins;San Martin Lake
Lake Malawi|706|Lake Nyasa;Nyasa
Issyk-Kul|668|Issyk Kul
Great Slave Lake|614
Crater Lake|594
Lake Matano|590
General Carrera Lake|586|Lake General Carrera;Buenos Aires Lake
Hornindalsvatnet|514
Quesnel Lake|511
Lake Toba|505|Toba
Sarez Lake|505
Lake Tahoe|501
Lake Argentino|500
Lake Kivu|480
Salvatnet|464|Salsvatnet
Lake Nahuel Huapi|464|Nahuel Huapi
Lake Hauroko|462
Cochrane/Pueyrredón Lake|460|Lake Cochrane;Lake Pueyrredon
Lake Tinn|460|Tinnsjå
Adams Lake|457
Lake Chelan|453
Lake Van|451
Lake Poso|450
Lake Fagnano|449|Fagnano Lake
Great Bear Lake|446
Lake Manapouri|444''')

# Per entry: topic, family, full scope, metric, unit, limit, direction, ascending 5 gap limits,
# source URLs, source transformation description, natural complete source list.
CONFIG={
 '2026-11-02':[
  ('world-literature-text','oss-37-shakespeare-play-spoken-words','All 37 plays with word counts in the Open Source Shakespeare 37-play table. The Two Noble Kinsmen is not in this edition.','Words per play, rounded to nearest 1,000','words',24000,'below',[1000,2000,3000,4000,5000],['https://www.opensourceshakespeare.org/views/plays/plays_numwords.php','https://www.folger.edu/explore/shakespeares-works/frequently-asked-questions/'],'Use Open Source Shakespeare fixed play word count, nearest thousand (half up) before scoring.',shakespeare,'Name a Shakespeare play with at most 24,000 words (rounded to the nearest 1,000).'),
  ('road-cycling','tour-de-france-2025-21-raced-stage-distances','All 21 numbered 2025 Tour de France stages, as actually ridden; stage 19 is the shortened 93.1 km route.','Actual raced stage length in kilometres','km',184.9,'below',[1,3,5,7,11],['https://en.wikipedia.org/wiki/2025_Tour_de_France','https://www.procyclingstats.com/race/tour-de-france/2025/route/stage-profiles'],'Use completed race as ridden: stage 19 officially shortened to 93.1 km, not pre-race projected 129.9 km.',tour,'Name a 2025 Tour de France stage at most 184.9 km long (as raced).'),
  ('maritime-history','titanic-20-lifeboats-historical-aboard-tally','All 20 Titanic lifeboats 1–16 and collapsibles A–D, using the 712-person recorded tally. Alternative historical reconstructions can differ.','Recorded occupants assigned to lifeboat, 712-person historical reconstruction','people',40,'below',[4,8,12,16,22],['https://en.wikipedia.org/wiki/Lifeboats_of_the_Titanic','https://www.titanicinquiry.org/BOTInq/BOTReport/BOTRepBoats.php'],'Freeze the published 712-person lifeboat tally (not seating capacity); collapse boat tallies include swimmers recovered after launching. Historical estimates differ.',boats,'Name a Titanic lifeboat recorded with at most 40 occupants in the 712-person historical tally.'),
  ('scientific-metrology','bipm-24-current-si-prefix-exponents','All 24 decimal SI prefixes recognized by the BIPM as of the 2022 SI revisions.','Base-10 exponent in the SI prefix multiplying factor','exponent',3,'below',[1,2,4,6,9],['https://www.bipm.org/en/measurement-units/si-prefixes','https://www.nist.gov/pml/owm/metric-si-prefixes'],'The metric is signed n in 10^n for the 24 officially adopted prefixes, not the multiplier itself.',prefix,'Name an SI prefix whose base-10 exponent is at most +3.'),
  ('global-hospitality','50-best-hotels-2024-ranked-50','Exactly the 50 hotels with ranks 1–50 on the original 2024 The World’s 50 Best Hotels list, frozen in 2024.','Position on the 2024 global hotels ranking','rank',30,'below',[2,5,10,17,27],['https://www.the50.com/hotels/best-in-the-world/previous-list/2023','https://mma.prnewswire.com/media/2506830/50_Best_Hotels_2024_PDF.pdf'],'Use the official 2024 positions, not a 2025/2026 ranking. Lower position number is better.',hotels,'Name a hotel in the 2024 world top 50 ranked 30th or better (rank ≤ 30).'),
  ('planetary-astronomy','voyager-uranus-15-moons-diameters','The 15 pre-1997 Uranus satellites listed with single-kilometre diameters in the historic NASA Voyager fact sheet; newer discovered moons intentionally outside scope.','Diameter reported by the NASA Voyager fact sheet in kilometres','km',84,'above',[24,70,400,1100,1500],['https://science.nasa.gov/mission/voyager/fact-sheet/'],'Use only the 15 historical Uranus-moon records in NASA Voyager fact-sheet table; diameters are rounded to integer km.',moons,'Name a Uranian moon known by 1986 with a diameter of at least 84 km.'),
 ],
 '2026-11-03':[
  ('world-architecture','ctbuh-2024-world-50-tallest-buildings','Exactly the first 50 entries of the CTBUH historical 2024 tallest completed buildings list; twin towers count separately.','Architectural height in metres of a ranked completed building in 2024','m',450,'above',[4,14,40,95,195],['https://www.skyscrapercenter.com/buildings/?function=all&location=world&material=all&status=completed&year=2024'],'Architectural CTBUH height (spire included, antenna excluded), reported to nearest metre in published list.',buildings,'Name one of the 50 tallest completed buildings in 2024 standing at least 450 m tall.'),
  ('animation-cinema','oscars-animated-feature-winners-film-years-2001-2025','All 25 Academy Award Best Animated Feature winners for film years 2001–2025; excludes other animation categories and nominees.','Film year recognized for the Academy Award for Best Animated Feature','year',2014,'above',[2,4,6,8,11],['https://awardsdatabase.oscars.org/','https://www.atogt.com/askoscar/winners-only-by-category.php?cat=animated&origin=winners-by-cat&yr=1'],'Use award film year, not next-calendar-year Oscars ceremony date; as of March 2026, include 2025 KPop Demon Hunters.',films,'Name a Best Animated Feature Oscar-winning film with a film year of at least 2014.'),
  ('computer-language-culture','tiobe-october-2026-20-ratings','All 20 named languages in the October 2026 TIOBE published top 20, including tied decimal ratings.','October 2026 TIOBE ranking rate in percent, rounded to two decimals','%',0.97,'above',[0.07,0.16,0.32,0.50,1.50],['https://www.tiobe.com/tiobe-index/','https://safeguard.sh/resources/blog/programming-language-market-share-every-index-compared'],'Use exactly the October 2026 snapshot percentages, 2 decimal places. Percentage scorer rounds to nearest integer in backend: DO NOT use % unit for fractional percent! Use pp instead.',languages,'Name a top-20 programming language in October 2026 with a popularity score of at least 0.97 percentage points.'),
  ('human-genomics','grch38-24-nuclear-chromosome-sizes','All 24 primary human nuclear chromosome reference sequences 1–22, X and Y in GRCh38, excluding mitochondrial DNA and unplaced scaffolds.','Reference nuclear chromosome sequence length, rounded to nearest million base pairs','million bp',156,'above',[4,17,27,43,95],['https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh38','https://github.com/ENCODE-DCC/encValData/blob/master/GRCh38/GRCh38.chrom.sizes'],'Use total chromosome length in NCBI GRCh38 assembly 1–22,X,Y, before nearest-million-half-up rounding.',chrom,'Name a human nuclear chromosome at least 156 million base pairs long (GRCh38, nearest million).'),
  ('recorded-popular-music','billboard-2025-global-yearend-first-50','Exactly ranks 1–50 of the published 2025 year-end Billboard Global 200 songs listing, not the weekly chart.','2025 Global 200 year-end placement','rank',18,'below',[2,5,9,13,17],['https://chartsdatabase.me/global200?view=yearend','https://www.billboard.com/charts/year-end/2025/billboard-global-200/'],'Use positions 1–50 from 2025 year-end chart. Distinct tracks; submission is song title (avoid artist-only aliases).',songs,'Name a song from the 2025 year-end Global 200 top 50 ranked 18th or better (rank ≤ 18).'),
  ('lake-hydrology','journeyz-2021-thirty-deepest-lakes','All 30 listed lakes in the 2021 Journeyz 30-deepest-lakes editorial table, including the Caspian Sea and subglacial Lake Vostok.','Maximum cited lake depth in metres from frozen editorial ranking','m',594,'below',[10,85,95,133,151],['https://journeyz.co/deepest-lakes-in-the-world-depth/','https://www.macrodiscovery.com/deepest-lakes/'],'Pinned list-specific bathymetric approximations; competing published surveys disagree for individual depths.',lakes,'Name one of the world’s 30 deepest lakes with a reported maximum depth of at most 594 m.'),
 ]}
# Never make programming percent be unit '%' as Core.score rounds % input to whole number.
# percentage-point notation is semantically correct and preserves source 2-decimal measurement.
TIERS=['RAZOR EDGE','CLOSE CALL','SOLID HIT','IN THE ZONE','ON THE BOARD']

def points(v,lim,side,bands):
 gap=(lim-v) if side=='below' else (v-lim)
 if gap<0:return (0,'CROSSED LIMIT')
 if gap==0:return (1200,'PERFECT HIT')
 for band,pts,tier in zip(bands,[1000,800,600,400,200],TIERS):
  if gap <= band+1e-8:return pts,tier
 return (0,'TOO FAR')

for date, configs in CONFIG.items():
 dayno=11 if date.endswith('02') else 12
 questions={}
 for i,(topic,family,scope,metric,unit,lim,side,bands,urls,rule,entries,prompt) in enumerate(configs,1):
  if unit=='%':unit='percentage points'
  assert len(entries)>=12 and len(set(n.casefold() for n,v,a in entries))==len(entries),f'{date} q{i} count/duplicate'
  qn=f'q{i}'; sid=f'{family}-source'; source_file=f'v24-{date}-{qn}-{family}.csv'
  qq={
   'id':f'closeish_{date.replace("-", "")}_{qn}', 'date':date, 'day_number':dayno,'topic':topic,'bank_id':family,'question_family':family,
   'prompt':prompt,'metric':metric,'unit':unit,'limit':lim,'direction':side,'comparison':'at_most' if side=='below' else 'at_least',
   'time_limit_seconds':30,'boundary_inclusive':True,'input_max_length':180,
   'score_bands':[{'max_gap_inclusive':edge,'points':p,'tier':t} for edge,p,t in zip(bands,[1000,800,600,400,200],TIERS)],
   'scoring_window':{'max_scoring_distance':bands[-1],'units':unit,'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
   'source':urls[0], 'source_refs':[sid], 'verification_status':'source_list_completely_enumerated','editorial_status':'complete_checked_scheduled',
   'content_revision':'v24-20261026-nov02-nov03-1', 'metric_provenance':scope,'measurement_snapshot':f'Pinned source list; complete CSV: content/source-snapshots/{source_file}',
   'measurement':{'property':metric,'numeric_rule':rule,'unit':unit,'time_dependent':family not in ['oss-37-shakespeare-play-spoken-words','bipm-24-current-si-prefix-exponents','voyager-uranus-15-moons-diameters','grch38-24-nuclear-chromosome-sizes'],'source_urls':urls},
   'answer_scope':{'type':'source_defined_finite_named_universe','coverage':'complete_for_exact_prompt_universe','claimed_exhaustive':True,'entity_scope':scope,'dataset_count':len(entries),'known_unmeasured_count':0,'note':'Every member of the explicitly bounded source list is included, including wrong-side and zero-point entries. No examples-only selection.'},
   'scoring_policy':'Category membership verified first; then measured value and one-sided backend bands. Wrong side and beyond window return zero.',
   'perfect_tier':{'points':1200,'tier':'PERFECT HIT','rule':'exact metric_value == limit'},
   'approach_rule':{'required_side':'from_above' if side=='above' else 'from_below','operator':'>=' if side=='above' else '<=','exact_target_allowed':True,'wrong_side_points':0,'exact_target_points':1200},'answers':[]}
  for idx,(name,val,aliases) in enumerate(entries,1):
   score,tier=points(val,lim,side,bands)
   qq['answers'].append({'entity_id':f'{family}-{idx:03d}','canonical':name,
     'aliases':[{'input':a,'kind':'documented_variant','action':'accept'} for a in aliases],
     'verified_status':'source_row_or_rounded_source_value','source_refs':[{'source_id':sid,'locator':f'row-{idx:03d}'}],
     'metric_value':val,'points':score,'tier':tier,'source_evidence':{'rule':rule}})
  coverage=collections.Counter(a['points'] for a in qq['answers'])
  assert set(coverage)=={0,200,400,600,800,1000,1200},f'{date} {qn} tier holes {coverage}'
  assert len(prompt)<=165,(date,qn,len(prompt))
  canonical_norm=lambda s:''.join(ch for ch in unicodedata.normalize('NFKD',s.lower()) if ch.isalnum())
  seen={}
  for a in qq['answers']:
    for alias in [a['canonical']]+[x['input'] for x in a['aliases']]:
      n=canonical_norm(alias.replace('++','plusplus').replace('#','sharp')); assert not n in seen or seen[n]==a['canonical'],f'Alias collision: {date} {qn} {alias} with {seen[n]}'
      seen[n]=a['canonical']
  questions[qn]=qq
  with open(SNAP/source_file,'w',encoding='utf-8',newline='') as fh:
   writer=csv.writer(fh);writer.writerow(['entity_id','canonical','metric_value','points','tier','unit','source_url','source_row'])
   for idx,a in enumerate(qq['answers'],1):writer.writerow([a['entity_id'],a['canonical'],a['metric_value'],a['points'],a['tier'],unit,urls[0],idx])
  print(date,qn,topic, len(entries), dict(sorted(coverage.items())),len(prompt))
 day={'schema_version':1,'date':date,'day_number':dayno,'revision':'v24-november-02-03-complete-1','publication_status':'scheduled',
  'editorial_note':'V23 diversity requirements + complete, source-scoped member banks; 2026-10-23 through 2026-11-01 days are unchanged. Future date remains API-gated.', 'questions':questions}
 (OUT/f'{date}.json').write_text(json.dumps(day,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
