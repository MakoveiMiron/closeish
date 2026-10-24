import json, pathlib, collections, re, math, unicodedata
from decimal import Decimal,ROUND_HALF_UP
ROOT=pathlib.Path(__file__).resolve().parents[1]
DAY='2026-11-01';N=10
snap=ROOT/'source-snapshots'
snap.mkdir(exist_ok=True)

def A(name, val, aliases=None, id=None, locator=None):
    return dict(canonical=name,value=val,aliases=aliases or [],entity_id=id or re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-'),locator=locator or name)

# Source 1: ISO-16 A4 = 440Hz + twelve equal-tempered semitone equation, MIDI keys 21..108
notes=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
sharpflat={'C#':'Db','D#':'Eb','F#':'Gb','G#':'Ab','A#':'Bb'}
piano=[]
for midi in range(21,109):
    note=notes[midi%12]; octv=midi//12-1
    freq=Decimal(str(440*2**((midi-69)/12))).quantize(Decimal('1'),rounding=ROUND_HALF_UP)
    aliases=[]
    if note in sharpflat:
        aliases += [sharpflat[note]+str(octv),note.replace('#','♯')+str(octv),sharpflat[note].replace('b','♭')+str(octv)]
        aliases += [note.replace('#',' sharp ')+str(octv),sharpflat[note].replace('b',' flat ')+str(octv)]
    piano.append(A(note+str(octv),int(freq),aliases,id='midi-'+str(midi),locator='MIDI-'+str(midi)))

# Source 2: NOAA NHC official 2024 named storm max 1-min sustained wind kt, 18 named (exclude unnamed PTC Eight)
storms_raw='''Alberto 45
Beryl 145
Chris 40
Debby 70
Ernesto 85
Francine 90
Gordon 40
Helene 120
Isaac 90
Joyce 45
Kirk 130
Leslie 90
Milton 155
Nadine 50
Oscar 75
Patty 55
Rafael 105
Sara 45'''
storms=[]
for line in storms_raw.splitlines():
    n,kt=line.split();kt=int(kt)
    # physical metric: nearest whole km/h, 1 knot=1.852 km/h (exact)
    kmh=int((Decimal(kt)*Decimal('1.852')).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    storms.append(A(n,kmh,id='atlantic-2024-'+n.lower(), locator=n))

# Source 3: FIA 2025 24 circuits; length km from 2025 race season source f1-data.com numeric 3 decimal places converted to m
circuits_raw='''Albert Park Grand Prix Circuit|5278|Albert Park;Albert Park Circuit;Melbourne
Shanghai International Circuit|5451|Shanghai Circuit;Shanghai
Suzuka International Racing Course|5807|Suzuka;Suzuka Circuit
Bahrain International Circuit|5412|Bahrain Circuit;Sakhir
Jeddah Corniche Circuit|6174|Jeddah
Miami International Autodrome|5412|Miami International;Miami Circuit;Miami
Autodromo Enzo e Dino Ferrari|4909|Imola;Imola Circuit
Circuit de Monaco|3337|Monaco Circuit;Monte Carlo Circuit;Monte Carlo
Circuit de Barcelona-Catalunya|4675|Barcelona-Catalunya;Barcelona Catalunya Circuit;Barcelona
Circuit Gilles Villeneuve|4361|Montreal Circuit;Gilles Villeneuve
Red Bull Ring|4326|Spielberg Circuit
Silverstone Circuit|5891|Silverstone
Circuit de Spa-Francorchamps|7004|Spa;Spa-Francorchamps
Hungaroring|4381|Hungary Circuit
Circuit Zandvoort|4259|Zandvoort
Autodromo Nazionale Monza|5793|Monza;Monza Circuit
Baku City Circuit|6003|Baku
Marina Bay Street Circuit|4927|Singapore Circuit;Marina Bay Circuit
Circuit of the Americas|5513|COTA;Austin Circuit
Autodromo Hermanos Rodriguez|4304|Hermanos Rodriguez;Mexico City Circuit
Autodromo Jose Carlos Pace|4309|Interlagos;Sao Paulo Circuit
Las Vegas Strip Circuit|6201|Las Vegas Circuit
Lusail International Circuit|5419|Losail;Lusail Circuit
Yas Marina Circuit|5281|Yas Marina;Abu Dhabi Circuit'''
circuits=[]
for i,line in enumerate(circuits_raw.splitlines(),1):
    name,m,ali=line.split('|')
    circuits.append(A(name,int(m),ali.split(';'),id='f1-2025-r%02d'%i,locator='round-'+str(i)))

# Source 4: UIAA 14 and heights 8000ers.com + mountaineering 14 peak list, metres
mountain_raw='''Mount Everest|8849|Everest;Sagarmatha;Chomolungma
K2|8611|Mount Godwin-Austen
Kangchenjunga|8586|Kanchenjunga
Lhotse|8516|
Makalu|8485|Mount Makalu
Cho Oyu|8188|
Dhaulagiri I|8167|Dhaulagiri
Manaslu|8163|
Nanga Parbat|8125|
Annapurna I|8091|Annapurna
Gasherbrum I|8080|Hidden Peak
Broad Peak|8051|
Gasherbrum II|8034|
Shishapangma|8027|Shisha Pangma;Xixabangma'''
mountains=[]
for i,line in enumerate(mountain_raw.splitlines(),1):
    name,ele,alias=line.split('|'); mountains.append(A(name,int(ele),list(filter(None,alias.split(';'))),id='eight-thousander-%02d'%i,locator=name))

# Source 5: ESA, Space Shuttle missions: 135 launches, listed days and hours, using COMPLETED WHOLE DAYS (not rounded).
# For STS-135 ESA displays '13 days' rounded, NASA primary 12 d 18h 28m 50s => 12 whole days. STS-51L 73s => 0.
shuttle_text='''STS-1 2 6
STS-2 2 6
STS-3 8 0
STS-4 7 1
STS-5 5 2
STS-6 5 0
STS-7 6 2
STS-8 6 1
STS-9 10 7
STS-41B 7 23
STS-41C 6 23
STS-41D 6 0
STS-41G 8 5
STS-51A 7 23
STS-51C 3 1
STS-51D 6 23
STS-51B 7 0
STS-51G 7 1
STS-51F 7 22
STS-51I 7 2
STS-51J 4 1
STS-61A 7 0
STS-61B 6 21
STS-61C 6 2
STS-51L 0 0
STS-26 4 1
STS-27 4 9
STS-29 4 23
STS-30 4 0
STS-28 5 1
STS-34 4 23
STS-33 5 0
STS-32 10 21
STS-36 4 10
STS-31 5 1
STS-41 4 2
STS-38 4 21
STS-35 8 23
STS-37 5 23
STS-39 8 7
STS-40 9 2
STS-43 8 21
STS-48 5 8
STS-44 6 22
STS-42 8 1
STS-45 8 22
STS-49 8 21
STS-50 13 19
STS-46 7 23
STS-47 7 22
STS-52 9 20
STS-53 7 7
STS-54 5 23
STS-56 9 6
STS-55 9 23
STS-57 9 23
STS-51 9 20
STS-58 14 0
STS-61 10 19
STS-60 7 6
STS-62 13 23
STS-59 11 5
STS-65 14 17
STS-64 10 22
STS-68 11 5
STS-66 10 22
STS-63 8 6
STS-67 16 15
STS-71 9 19
STS-70 8 22
STS-69 10 20
STS-73 15 21
STS-74 8 4
STS-72 8 22
STS-75 15 17
STS-76 9 5
STS-77 10 0
STS-78 16 21
STS-79 10 3
STS-80 17 15
STS-81 10 4
STS-82 9 23
STS-83 3 23
STS-84 9 5
STS-94 15 16
STS-85 11 20
STS-86 10 19
STS-87 15 16
STS-89 8 19
STS-90 15 21
STS-91 9 19
STS-95 8 21
STS-88 11 19
STS-96 9 19
STS-93 4 22
STS-103 7 23
STS-99 11 5
STS-101 9 21
STS-106 11 19
STS-92 12 21
STS-97 10 19
STS-98 12 21
STS-102 12 19
STS-100 11 21
STS-104 12 18
STS-105 11 21
STS-108 11 19
STS-109 10 22
STS-110 10 19
STS-111 13 20
STS-112 10 19
STS-113 13 18
STS-107 15 22
STS-114 13 21
STS-121 12 18
STS-115 11 19
STS-116 12 21
STS-117 13 20
STS-118 12 18
STS-120 15 2
STS-122 12 18
STS-123 15 18
STS-124 13 18
STS-126 15 20
STS-119 12 19
STS-125 12 21
STS-127 15 16
STS-128 13 21
STS-129 10 19
STS-130 13 18
STS-131 15 3
STS-132 11 18
STS-133 12 19
STS-134 15 18
STS-135 12 18'''
shuttles=[]
for i,line in enumerate(shuttle_text.splitlines(),1):
    name,d,h=line.split();assert int(h)<24
    shuttles.append(A(name,int(d),id='shuttle-%03d'%i,locator=name))

# Source 6: Publisher official 41 Discworld books order, publication years verified with Pratchett estate chronology + academic bibliography
books_text='''The Colour of Magic|1983
The Light Fantastic|1986
Equal Rites|1987
Mort|1987
Sourcery|1988
Wyrd Sisters|1988
Pyramids|1989
Guards! Guards!|1989
Eric|1990
Moving Pictures|1990
Reaper Man|1991
Witches Abroad|1991
Small Gods|1992
Lords and Ladies|1992
Men at Arms|1993
Soul Music|1994
Interesting Times|1994
Maskerade|1995
Feet of Clay|1996
Hogfather|1996
Jingo|1997
The Last Continent|1998
Carpe Jugulum|1998
The Fifth Elephant|1999
The Truth|2000
Thief of Time|2001
The Last Hero|2001
The Amazing Maurice and his Educated Rodents|2001
Night Watch|2002
The Wee Free Men|2003
Monstrous Regiment|2003
A Hat Full of Sky|2004
Going Postal|2004
Thud!|2005
Wintersmith|2006
Making Money|2007
Unseen Academicals|2009
I Shall Wear Midnight|2010
Snuff|2011
Raising Steam|2013
The Shepherd's Crown|2015'''
books=[]
for i,line in enumerate(books_text.splitlines(),1):
    n,y=line.split('|'); aliases=[]
    if n=='The Amazing Maurice and his Educated Rodents':aliases=['The Amazing Maurice and His Educated Rodents']
    books.append(A(n,int(y),aliases,id='discworld-%02d'%i,locator='book-%02d'%i))

assert [len(x) for x in [piano,storms,circuits,mountains,shuttles,books]]==[88,18,24,14,135,41],list(map(len,[piano,storms,circuits,mountains,shuttles,books]))

CONFIG=[
  ('q1','music-acoustics','standard-piano-key-pitch','Name a key on a standard 88-key piano whose fundamental frequency is at least 440 Hz. (Rounded to the nearest hertz.)','Fundamental frequency in 12-tone equal temperament, A4=440 Hz','Hz',440,'above',[45,95,200,400,900],piano,'iso-piano-88',
   ['https://committee.iso.org/standard/3601.html','https://piano.org/theory/how-many-notes-on-a-piano/'],
   'All 88 keys A0–C8, MIDI notes 21–108, modern scientific pitch notation; standard equal temperament at A4=440 Hz. Frequency computed for all, nearest integer hertz with half-up rounding.',
   'ISO 16 tuning reference 440 Hz, twelve equal-tempered semitones f=440*2^((midi-69)/12); 88-key note names and sharp/flat spellings.'),
  ('q2','meteorology','2024-atlantic-named-storm-maximum-wind',
   'Name a named Atlantic storm from 2024 whose peak sustained wind speed was at most 167 km/h. (Rounded to the nearest km/h.)',
   '2024 North Atlantic tropical cyclone peak 1-minute sustained wind','km/h',167,'below',[10,29,48,66,82],storms,'nhc-atlantic-2024-18',
   ['https://www.nhc.noaa.gov/data/tcr/index.php?season=2024'],
   'Exactly 18 named tropical storms/hurricanes in the NHC 2024 North Atlantic summary; unnamed Potential Tropical Cyclone Eight is not eligible. All named storm peaks are included.',
   'NHC final seasonal best track summary max winds in knots; convert to km/h by exact factor 1 knot=1.852 km/h and round half-up to integer BEFORE scoring.'),
  ('q3','motorsport-engineering','2025-f1-grand-prix-circuit-length',
   'Name a circuit used for a 2025 Formula One Grand Prix that was at least 5,412 metres long per lap.',
   'Race lap length for 2025 F1 Grand Prix circuit layout','m',5412,'above',[50,150,400,500,800],circuits,'fia-f1-2025-24',
   ['https://www.formula1.com/en/latest/article/fia-and-formula-1-announces-calendar-for-2025.48ii9hOMGxuOJnjLgpA5qS','https://www.formula1.com/en/racing/2025/las-vegas','https://www.formula1.com/en/racing/2025/australia','https://www.formula1.com/en/racing/2025/qatar','https://www.formula1.com/en/racing/2025/singapore','https://www.formula1.com/en/racing/2025/mexico','https://www.formula1.com/en/racing/2025/austria','https://f1-data.com/script/db/race/list.php?year=2025'],
   'All 24 2025 Formula 1 World Championship Grand Prix circuits, counted once by race round; includes street circuits and two Italian events.',
   'Race lap lengths in metres, checked against the official Formula 1 2025 round event pages, including corrections where an unaffiliated race listing used race-distance per lap or outdated track length (Austria, Singapore, Mexico, Las Vegas, Qatar). Not 2026 layout changes.'),
  ('q4','mountaineering-geography','fourteen-eight-thousanders-elevation',
   'Name one of the world’s 14 recognised eight-thousanders with a summit elevation of at most 8,611 metres.',
   'Summit elevation among fourteen traditional eight-thousanders','m',8611,'below',[30,100,150,450,560],mountains,'uiaa-14-eight-thousanders',
   ['https://www.theuiaa.org/uiaa-position-on-8000m-peaks/','https://sevensummittreks.com/expedition/8000ers.html'],
   'All 14 traditional main peaks above 8,000m recognised as the fourteen eight-thousanders; no subsidiary peaks even when above 8,000m.',
   'Metre altitude values from Seven Summit Treks 8000er peak table / 8000ers.com altitude source; Everest 8848.86 m rounded to 8849m; disputed/re-measured altitudes are frozen to listed source vintage.'),
  ('q5','spaceflight-history','135-shuttle-flights-complete-days',
   'Name a NASA Space Shuttle mission lasting at most 12 complete days in flight.',
   'Number of full elapsed 24-hour periods during a shuttle flight','days',12,'below',[1,2,3,4,6],shuttles,'esa-135-sts-missions',
   ['https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Space_Shuttle/Space_Shuttle_missions','https://www.nasa.gov/space-shuttle/','https://www.nasa.gov/mission/sts-135/'],
   'All 135 flight designators of the Space Shuttle program, including the launches STS-51L and STS-107, and STS-135. Enterprise free-flight tests excluded.',
   'Take the integer whole days part (floor) of ESA listed elapsed d and h. STS-51L lasted only 73 seconds => zero complete days; STS-135 NASA exact 12d18h28m50s => 12 complete days, overriding rounded ESA 13 days.'),
  ('q6','fantasy-literature','terry-pratchett-discworld-novels-first-published',
   'Name a Discworld novel first published in 2005 or earlier.',
   'First publication year for the 41 Terry Pratchett Discworld novels','year',2005,'below',[2,5,9,13,20],books,'discworld-41-chronological',
   ['https://www.terrypratchettbooks.com/book-series/discworld/','https://terrypratchett.com/terry-pratchett/','https://academic.oup.com/view-large/396874599'],
   'All 41 main-series Discworld novels in official publisher reading order, including Tiffany Aching sub-series; short stories and companion books excluded.',
   'Use first publication YEAR from Pratchett estate timeline and series list; not a later paperback, US edition, revised printing, game, or short-story date.'),
]

TIERS=['RAZOR EDGE','CLOSE CALL','SOLID HIT','IN THE ZONE','ON THE BOARD']

def encode_points(val,lim,dire,bands):
    gap=(lim-val) if dire=='below' else (val-lim)
    if gap<0:return 0,'CROSSED LIMIT'
    if gap==0:return 1200,'PERFECT HIT'
    for x,pt,tier in zip(bands,[1000,800,600,400,200],TIERS):
        if gap<=x:return pt,tier
    return 0,'TOO FAR'

questions={}
for qid,topic,bank_id,prompt,metric,unit,lim,dire,bands,entries,source_id,urls,scope,meas in CONFIG:
    q=dict(id=f'closeish_20261101_{qid}',date=DAY,day_number=N,topic=topic,bank_id=bank_id,question_family=bank_id,prompt=prompt,metric=metric,unit=unit,limit=lim,comparison='at_most' if dire=='below' else 'at_least',time_limit_seconds=30,direction=dire,boundary_inclusive=True,
      score_bands=[{'max_gap_inclusive':v,'points':pt,'tier':t} for v,pt,t in zip(bands,[1000,800,600,400,200],TIERS)],
      source=urls[0],source_refs=[source_id],verification_status='verified_exhaustive_fixed_source_universe',editorial_status='complete_verified_scheduled',content_revision='2026-10-24-complete-v1',
      metric_provenance=scope,measurement_snapshot='Pinned 2026-10-24 web source review; see local content/source-snapshots/closeish-2026-11-01-*.csv',
      measurement={'property':metric,'numeric_rule':meas,'unit':unit,'time_dependent':qid in ['q2','q3','q5','q6'], 'source_urls':urls},
      answer_scope={'type':'finite_exhaustive_named_universe','coverage':'complete_for_exact_prompt_universe','claimed_exhaustive':True,'entity_scope':scope,'dataset_count':len(entries),'known_unmeasured_count':0,'note':'All eligible named source records enumerated; wrong-side and out-of-scoring-window records included.'},
      scoring_policy='Category eligibility checked first; exact boundary 1200, wrong side and too far zero; unit consistently metric.',
      perfect_tier={'points':1200,'tier':'PERFECT HIT','rule':'exact metric_value == limit'},
      approach_rule={'required_side':'from_below' if dire=='below' else 'from_above','operator':'<=' if dire=='below' else '>=','exact_target_allowed':True,'wrong_side_points':0,'exact_target_points':1200},
      scoring_window={'max_scoring_distance':bands[-1],'units':unit,'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},input_max_length=180,
      answers=[])
    for e in entries:
        pt,tier=encode_points(e['value'],lim,dire,bands)
        q['answers'].append({'entity_id':e['entity_id'],'canonical':e['canonical'],
           'aliases':[{'input':s,'kind':'documented_variant','action':'accept'} for s in e['aliases']],
           'verified_status':'source_record_or_exact_derivation',
           'source_refs':[{'source_id':source_id,'locator':e['locator']}],
           'metric_value':e['value'],'points':pt,'tier':tier,'source_evidence':{'rule':meas}})
    questions[qid]=q
    assert any(a['points']==1200 for a in q['answers']),qid
    # Save independently inspectable, real sourced universe, not a partial bank
    import csv
    with (snap/('closeish-2026-11-01-'+qid+'-full.csv')).open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['entity_id','canonical','metric_value','unit','source_record_locator']); w.writerows([a['entity_id'],a['canonical'],a['metric_value'],unit,a['source_refs'][0]['locator']] for a in q['answers'])

day={'schema_version':1,'date':DAY,'day_number':N,'revision':'v19-2026-11-01-complete-v1','publication_status':'scheduled','editorial_note':'Final six-question content package. Entire six source-defined answer universes included. Full Hungarian editorial and validation audit in content/reference-rules/AUDIT-2026-11-01-COMPLETE-HU.md; no known intentionally missing eligible answers. Scheduled; not public before 2026-11-01 local server release date.', 'questions':questions}
path=ROOT/'days'/f'{DAY}.json'
path.write_text(json.dumps(day,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(path,path.stat().st_size)
for k,q in questions.items():
    print(k,len(q['answers']),collections.Counter(a['points'] for a in q['answers']))
