"""Deterministically regenerate the two scheduled, complete Nov 4–5 content banks.
Uses specifically dated, publicly enumerated reference lists; never overwrite played days.
Historical sources and editorial exclusions are explicitly described with each question.
"""
from pathlib import Path
import json,csv,collections,unicodedata
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'days'; SNAP=ROOT/'source-snapshots'
def parse(text):
 rows=[]
 for line in text.strip().splitlines():
  if not line.strip():continue
  fields=[s.strip() for s in line.split('|')]
  rows.append((fields[0],float(fields[1]) if '.' in fields[1] else int(fields[1]),[a.strip() for a in fields[2].split(';')] if len(fields)>2 else []))
 return rows
verdi=parse('''Oberto, conte di San Bonifacio|1839|Oberto
Un giorno di regno|1840
Nabucco|1842|Nabucodonosor
I Lombardi alla prima crociata|1843
Ernani|1844
I due Foscari|1844
Giovanna d'Arco|1845
Alzira|1845
Attila|1846
Macbeth|1847
I masnadieri|1847
Il corsaro|1848
La battaglia di Legnano|1849
Luisa Miller|1849
Stiffelio|1850
Rigoletto|1851
Il trovatore|1853
La traviata|1853
Les vêpres siciliennes|1855|The Sicilian Vespers
Simon Boccanegra|1857
Un ballo in maschera|1859
La forza del destino|1862
Don Carlos|1867|Don Carlo
Aida|1871
Otello|1887
Falstaff|1893''')
peace=parse('''Maria Corina Machado|2025
Nihon Hidankyo|2024
Narges Mohammadi|2023
Ales Bialiatski|2022
Memorial|2022
Center for Civil Liberties|2022|Centre for Civil Liberties
Maria Ressa|2021
Dmitry Muratov|2021
World Food Programme|2020|WFP
Abiy Ahmed Ali|2019|Abiy Ahmed
Denis Mukwege|2018
Nadia Murad|2018
International Campaign to Abolish Nuclear Weapons|2017|ICAN
Juan Manuel Santos|2016
National Dialogue Quartet|2015|Tunisian National Dialogue Quartet
Kailash Satyarthi|2014
Malala Yousafzai|2014
Organisation for the Prohibition of Chemical Weapons|2013|OPCW
European Union|2012|EU
Ellen Johnson Sirleaf|2011
Leymah Gbowee|2011
Tawakkol Karman|2011
Liu Xiaobo|2010
Barack Obama|2009|Barack Hussein Obama
Martti Ahtisaari|2008
Intergovernmental Panel on Climate Change|2007|IPCC
Al Gore|2007|Albert Arnold Gore Jr.
Muhammad Yunus|2006
Grameen Bank|2006
International Atomic Energy Agency|2005|IAEA
Mohamed ElBaradei|2005
Wangari Maathai|2004
Shirin Ebadi|2003
Jimmy Carter|2002|James Earl Carter Jr.
United Nations|2001|UN
Kofi Annan|2001
Kim Dae-jung|2000''')
footballnames='''Rodri
Vinicius Jr.
Jude Bellingham
Dani Carvajal
Erling Haaland
Kylian Mbappé
Lautaro Martínez
Lamine Yamal
Toni Kroos
Harry Kane
Phil Foden
Florian Wirtz
Dani Olmo
Ademola Lookman
Nico Williams
Granit Xhaka
Federico Valverde
Emiliano Martínez
Martin Ødegaard
Hakan Çalhanoğlu
Bukayo Saka
Antonio Rüdiger
Rúben Dias
William Saliba
Cole Palmer
Declan Rice
Vitinha
Alejandro Grimaldo
Mats Hummels
Artem Dovbyk'''.splitlines()
football=[(n,i,[]) for i,n in enumerate(footballnames,1)]
bond=parse('''Dr. No|109|Doctor No
From Russia with Love|116
Goldfinger|109
Thunderball|130
You Only Live Twice|116
On Her Majesty's Secret Service|142
Diamonds Are Forever|119
Live and Let Die|121
The Man with the Golden Gun|125
The Spy Who Loved Me|125
Moonraker|126
For Your Eyes Only|127
Octopussy|131
A View to a Kill|131
The Living Daylights|130
Licence to Kill|133|License to Kill
GoldenEye|130|Golden Eye
Tomorrow Never Dies|119
The World Is Not Enough|128
Die Another Day|132
Casino Royale|144
Quantum of Solace|106
Skyfall|143
Spectre|148
No Time to Die|163''')
fields=parse('''Lars Valerian Ahlfors|1936|Lars Ahlfors
Jesse Douglas|1936
Laurent Schwartz|1950
Atle Selberg|1950
Kunihiko Kodaira|1954
Jean-Pierre Serre|1954
Klaus Friedrich Roth|1958|Klaus Roth
René Thom|1958
Lars Hörmander|1962
John Willard Milnor|1962|John Milnor
Michael Francis Atiyah|1966|Michael Atiyah
Paul Joseph Cohen|1966|Paul Cohen
Alexander Grothendieck|1966
Stephen Smale|1966
Alan Baker|1970
Heisuke Hironaka|1970
Serge Novikov|1970
John Griggs Thompson|1970|John Thompson
Enrico Bombieri|1974
David Bryant Mumford|1974|David Mumford
Pierre René Deligne|1978|Pierre Deligne
Charles Louis Fefferman|1978|Charles Fefferman
Gregori Alexandrovitch Margulis|1978|Grigori Margulis
Daniel G. Quillen|1978|Daniel Quillen
Alain Connes|1982
William P. Thurston|1982|William Thurston
Shing-Tung Yau|1982
Simon K. Donaldson|1986|Simon Donaldson
Gerd Faltings|1986
Michael H. Freedman|1986|Michael Freedman
Vladimir Drinfeld|1990
Vaughan F.R. Jones|1990|Vaughan Jones
Shigefumi Mori|1990
Edward Witten|1990
Jean Bourgain|1994
Pierre-Louis Lions|1994
Jean-Christophe Yoccoz|1994
Efim Zelmanov|1994
Richard E. Borcherds|1998|Richard Borcherds
W. Timothy Gowers|1998|Timothy Gowers
Maxim Kontsevich|1998
Curtis T. McMullen|1998|Curtis McMullen
Laurent Lafforgue|2002
Vladimir Voevodsky|2002
Andrei Okounkov|2006
Grigori Perelman|2006
Terence Tao|2006
Wendelin Werner|2006
Elon Lindenstrauss|2010
Ngô Bảo Châu|2010|Ngo Bao Chau
Stanislav Smirnov|2010
Cédric Villani|2010
Artur Avila|2014
Manjul Bhargava|2014
Martin Hairer|2014
Maryam Mirzakhani|2014
Caucher Birkar|2018
Alessio Figalli|2018
Peter Scholze|2018
Akshay Venkatesh|2018
Hugo Duminil-Copin|2022
June Huh|2022
James Maynard|2022
Maryna Viazovska|2022''')
happiness=parse('''Finland|7.736
Denmark|7.521
Iceland|7.515
Sweden|7.345
Netherlands|7.306
Costa Rica|7.274
Norway|7.262
Israel|7.234
Luxembourg|7.122
Mexico|6.979
Australia|6.974
New Zealand|6.952
Switzerland|6.935
Belgium|6.910
Ireland|6.889
Lithuania|6.829
Austria|6.810
Canada|6.803
Slovenia|6.792
Czechia|6.775|Czech Republic
United Arab Emirates|6.759|UAE
Germany|6.753
United Kingdom|6.728|UK
United States|6.724|USA;United States of America
Belize|6.711
Poland|6.673
Taiwan|6.669
Uruguay|6.661
Kosovo|6.659
Kuwait|6.629''')
monarchs=parse('''Henry VII|1485
Henry VIII|1509
Edward VI|1547
Mary I|1553|Mary Tudor
Elizabeth I|1558
James I|1603|James VI and I
Charles I|1625
Charles II|1660
James II|1685|James VII and II
William III|1689|William of Orange
Mary II|1689
Anne|1702|Queen Anne
George I|1714
George II|1727
George III|1760
George IV|1820
William IV|1830
Victoria|1837|Queen Victoria
Edward VII|1901
George V|1910
Edward VIII|1936
George VI|1936
Elizabeth II|1952
Charles III|2022''')
paralympic=parse('''China|221
Great Britain|124|United Kingdom
United States|105|USA;United States of America
Netherlands|56
Brazil|89
Italy|72
Ukraine|82
France|75
Australia|62
Japan|41
Germany|49
Canada|29
Uzbekistan|26
Iran|25
Switzerland|21
Poland|23
India|29
Colombia|28
Belgium|14
Spain|39
Thailand|30
South Korea|30|Republic of Korea
Türkiye|28|Turkey
Cuba|10
Algeria|11
Hungary|15
Tunisia|11
Azerbaijan|11
Israel|10''')
gamesales=parse('''Tetris|520
Minecraft|425
Grand Theft Auto V|230|GTA V;GTA 5
Red Dead Redemption 2|87|RDR2
Wii Sports|82.9
Mario Kart 8 / Deluxe|79.99|Mario Kart 8 Deluxe;Mario Kart 8
PUBG: Battlegrounds|75|PUBG;PlayerUnknown's Battlegrounds
Terraria|70
The Elder Scrolls V: Skyrim|65|Skyrim
The Witcher 3: Wild Hunt|65|The Witcher 3
Super Mario Bros.|58
Human: Fall Flat|58|Human Fall Flat
Animal Crossing: New Horizons|50.29
The Sims|50
Stardew Valley|50
Overwatch|50
Pokémon Red / Blue / Yellow|47.44|Pokemon Red Blue Yellow
Wii Fit / Plus|43.8|Wii Fit Plus;Wii Fit
Call of Duty: Black Ops III|43|COD Black Ops 3
Call of Duty: Modern Warfare (2019)|41|Call of Duty Modern Warfare 2019
Sonic the Hedgehog (1991)|40|Sonic the Hedgehog 1991
Payday 2|40
Cyberpunk 2077|40
Hogwarts Legacy|40
Super Smash Bros. Ultimate|38.14
Mario Kart Wii|37.38
The Legend of Zelda: Breath of the Wild|35.76|Breath of the Wild
Fallout 4|35
Wii Sports Resort|33.14
Borderlands 2|31
New Super Mario Bros.|30.8
Super Mario Odyssey|30.8''')
# Original 2026-10-29 list reports sales to 2 decimals. Whole million, half up.
gamesales=[(name,int(Decimal(str(value)).quantize(Decimal('1'),rounding=ROUND_HALF_UP)),aliases) for name,value,aliases in gamesales]

stars=parse('''Sirius|-1.44
Canopus|-0.62
Arcturus|-0.05
Alpha Centauri|-0.01|Rigil Kentaurus
Vega|0.03
Capella|0.08
Rigel|0.18
Procyon|0.40
Betelgeuse|0.45
Achernar|0.45
Hadar|0.61|Beta Centauri
Altair|0.76
Acrux|0.77|Alpha Crucis
Aldebaran|0.87
Spica|0.98
Antares|1.06
Pollux|1.16
Fomalhaut|1.17
Deneb|1.25
Mimosa|1.25|Becrux
Regulus|1.36
Adhara|1.50
Castor|1.58
Gacrux|1.59
Shaula|1.62
Bellatrix|1.64
Beta Tauri|1.65|Elnath
Beta Carinae|1.67|Miaplacidus
Alnilam|1.69
Alpha Gruis|1.73|Alnair''')
raw_islands=parse('''Greenland|2108459.47
New Guinea|773751.01
Borneo|723154.07
Madagascar|592521.41
Baffin Island|507204.95
Sumatra|428134.16
Honshu|228296.26|Honshū
Victoria Island|219191.31
Great Britain|218634.50
Ellesmere Island|197790.33
Sulawesi|169981.39
South Island|150683.06|New Zealand South Island
Java|127467.41
North Island|114573.11|New Zealand North Island
Newfoundland|108878.06
Cuba|105468.33
Luzon|104835.31
Iceland|100260.91
Mindanao|94468.78
Ireland|83720.80
Hokkaido|77658.66|Hokkaidō
Hispaniola|74365.90
Sakhalin|74237.11
Banks Island|70191.02
Sri Lanka|65916.13
Tasmania|64333.21
Devon Island|55535.39
Alexander Island|51947.36
Isla Grande de Tierra del Fuego|47271.77|Tierra del Fuego (main island)
Severny Island|45245.73''')
islands=[(n,int(Decimal(str(v/1000)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))*1000,a) for n,v,a in raw_islands]
museumnames='''Louvre Museum
Vatican Museums
British Museum
Metropolitan Museum of Art
Tate Modern
Shanghai Museum East
National Gallery of Art
National Museum of Korea
Musée d'Orsay
National Museum of Anthropology
State Russian Museum
State Hermitage Museum
Victoria and Albert Museum
Museo del Prado
Centre Pompidou
National Gallery
Wawel Royal Castle
Somerset House
Uffizi Gallery
Museum of Modern Art'''.splitlines()
museums=[(n,i,[]) for i,n in enumerate(museumnames,1)]
CONFIG={
'2026-11-04':[
 ('opera-cultural-history','verdi-26-original-opera-premieres','All 26 original operas by Giuseppe Verdi, based on initial opera premiere dates, not later revised or retitled versions.','Original opera premiere year','year',1849,'below',[1,2,3,4,6],['https://en.wikipedia.org/wiki/List_of_compositions_by_Giuseppe_Verdi','https://theopera101.com/composers/verdi/'],'Use the first premiere year; later revisions of the same opera do not create separate entries.',verdi,'Name a Verdi opera that premiered in 1849 or earlier (at most 1849).'),
 ('international-peace','nobel-peace-2000-to-2025-all-laureates','Every named individual and organisation awarded the Nobel Peace Prize from 2000 through 2025, each co-laureate represented separately.','Nobel Peace Prize award year','year',2014,'below',[1,3,5,8,12],['https://www.nobelprize.org/prizes/lists/all-nobel-peace-prizes/all/','https://www.nobelpeaceprize.org/laureates/'],'Annual Nobel committee award year, including all named joint laureates and organizations.',peace,'Name a Nobel Peace Prize laureate (2000–2025) awarded in 2014 or earlier (at most 2014).'),
 ('football-awards','ballondor-mens-2024-ranked-30','All 30 players on the official 2024 men’s Ballon d’Or ranking, using published ordinal position.','Official 2024 men’s Ballon d’Or placement','rank',14,'below',[1,2,4,7,11],['https://ballondor.com/all-rankings?year=2024'],'Use source-published 1–30 ordinal row order (tied placements are displayed differently by some secondary publishers).',football,'Name a player in the 2024 men’s Ballon d’Or top 30 ranked at most 14th.'),
 ('spy-franchise-film','eon-james-bond-25-cinema-runtimes','All 25 Eon Productions official James Bond feature films released through 2021. Other Bond film adaptations are out of scope.','Film runtime in minutes','min',130,'below',[2,4,8,15,22],['https://007magazine.co.uk/factfiles/factfiles_movies1.htm','https://www.bondmovies.com/movies/'],'Use published theatrical film runtime in whole minutes, Eon Productions series only.',bond,'Name an Eon-produced James Bond film lasting at most 130 minutes.'),
 ('mathematical-history','imu-fields-medal-1936-to-2022','All 64 Fields Medal awardees officially listed by the International Mathematical Union for the 1936–2022 ceremonies; includes a named award declined by recipient.','Fields Medal award year','year',1998,'above',[4,8,12,16,24],['https://www.mathunion.org/imu-awards/fields-medal'],'Use IMU listing and year of award, including the 2006 medal declined by Grigori Perelman.',fields,'Name a Fields Medal laureate (1936–2022) awarded in 1998 or later (at least 1998).'),
 ('subjective-wellbeing','whr-2025-ranked-top-30-ladder-scores','Exactly the top 30 ranked countries/territories in the World Happiness Report 2025 ranking. Values are frozen three-decimal life-evaluation scores.','2025 life evaluation score (Cantril ladder 0–10)','ladder points',6.810,'above',[.02,.08,.13,.18,.32],['https://www.happierlivesinstitute.org/2025/03/20/the-top-25-happiest-countries-in-2025-plus-our-four-favourite-findings-from-the-2025-world-happiness-report/','https://worldhappiness.report/ed/2025/'],'Published 2025 three-decimal ladder score; do not round to whole percent.',happiness,'Name a 2025 World Happiness Report top-30 country scoring at least 6.810 out of 10.'),
],
'2026-11-05':[
 ('british-royal-dynasty','british-monarchs-henryvii-to-charlesiii-24','All 24 Tudor-through-Windsor crowned or formally accessioned monarchs from Henry VII to Charles III. Includes William III and Mary II individually; excludes non-monarch protectors and disputed nine-day claimant.','Year of first accession as English or British sovereign','year',1558,'above',[50,90,120,145,165],['https://www.hrp.org.uk/kings-and-queens-of-england-and-britain/'],'First year of reign per Historic Royal Palaces monarch timeline. Co-sovereigns William III and Mary II are separately named.',monarchs,'Name an English or British monarch since Henry VII who began reigning in 1558 or later (at least 1558).'),
 ('paralympic-medals','paris-2024-official-top30-national-medal-totals','All 29 named national delegations (NPCs) occupying published positions 1–30 in official Paris 2024 Paralympic medal table; neutral athletes are not a national delegation and are excluded.','Total 2024 Paris Paralympic medals for a national delegation','medals',30,'below',[1,2,5,10,16],['https://www.paralympic.org/paris-2024-paralympic-games/results/medalstandings'],'Use official national delegation totals in official ranking order at source snapshot; excluding Neutral Paralympic Athletes.',paralympic,'Name a Paris 2024 Paralympic top-30 national delegation with at most 30 medals.'),
 ('video-game-sales','alltime-video-game-2026-top30-ranked-32-games','All 32 ranked game titles in top 30 positions incl ties.','Global copies sold nearest million','million copies',31,'above',[2,5,9,14,25],['https://en.wikipedia.org/wiki/List_of_best-selling_video_games'],'2026-10-29 snapshot, rounded half up.',gamesales,'Name a top-30 bestselling video game with at least 31 million copies sold (nearest million).'),
 ('naked-eye-astronomy','astronomywiki-30-brightest-night-stars-magnitude','All 30 entries in the published brightest-stars table, using its fixed two-decimal apparent magnitude readings, with source typo Formalhaut corrected to Fomalhaut.','Listed apparent visual magnitude (lower is brighter)','mag',1.25,'above',[.12,.27,.34,.39,.46],['https://astronomy.wiki/brightest-stars'],'Use source-reported apparent magnitudes, not brightness rank. Values for variable stars may differ by observation epoch.',stars,'Name one of the 30 brightest night-sky stars with apparent magnitude at least +1.25.'),
 ('physical-island-geography','islands-world-30-largest-nearest-1000km2','All 30 islands in the global largest-islands-by-area ranking, excluding continental landmasses, using source area rounded to nearest 1,000 square kilometres before scoring.','Land area rounded to nearest 1,000 square kilometres','km²',105000,'above',[5000,12000,25000,50000,100000],['https://en.wikipedia.org/wiki/List_of_islands_by_area'],'Freeze area figures in source table and round to nearest 1,000 km² half up, including boundary cases.',islands,'Name one of the 30 largest islands with area at least 105,000 km² (nearest 1,000 km²).'),
 ('art-museum-attendance','world-most-visited-art-museums-2024-first-20','Exactly ranked places 1–20 of the 2024 published most-visited art museums table, not general history museums outside this art-museum ranking.','Position among top 20 most visited art museums for 2024','rank',12,'below',[1,2,4,7,9],['https://www.theartnewspaper.com/2025/04/01/the-worlds-most-visited-museums-2024-','https://wiki.ryanmichaelcurry.com/content/wikipedia_en_all_maxi_2025-08/List_of_most-visited_art_museums'],'Published table row ranking for the 2024 attendance year; this is an attendance ranking, not subjective art quality.',museums,'Name a museum among the 20 most visited art museums in 2024 ranked at most 12th.'),
]}
# Distribute award-year questions: no day contains two award-year mechanisms.
_fields_on_nov05=CONFIG['2026-11-04'][4]
CONFIG['2026-11-04'][4]=(
 'video-game-sales','alltime-video-game-2026-top30-ranked-32-games',
 'Exactly all 32 game titles occupying published top-30 ranks, including ties at first and 30th, in the global best-selling games list on 2026-10-29. Separate games bundled by the source are treated as one combined item; sales values rounded nearest million.',
 'Reported global software sales, rounded to nearest million copies','million copies',31,'above',[2,5,9,14,25],
 ['https://en.wikipedia.org/wiki/List_of_best-selling_video_games'],
 'Use source 2026-10-29 figures rounded to the nearest million, half up; original ranking includes tied positions and combined-version titles. Estimates vary by publisher.',
 gamesales,
 'Name a game in the 2026 all-time bestseller top 30 with at least 31 million sales (nearest million).'
)
CONFIG['2026-11-05'][2]=_fields_on_nov05

TIERS=['RAZOR EDGE','CLOSE CALL','SOLID HIT','IN THE ZONE','ON THE BOARD']

def points(val,limit,side,bands):
 gap=(Decimal(str(limit))-Decimal(str(val))) if side=='below' else (Decimal(str(val))-Decimal(str(limit)))
 if gap<0:return 0,'CROSSED LIMIT'
 if gap==0:return 1200,'PERFECT HIT'
 for edge,p,tier in zip(bands,[1000,800,600,400,200],TIERS):
  if gap<=Decimal(str(edge)):return p,tier
 return 0,'TOO FAR'
for day,definitions in CONFIG.items():
 questions={};dayno=13 if day.endswith('04') else 14
 for index,(topic,family,scope,metric,unit,limit,side,bands,urls,rule,entries,prompt) in enumerate(definitions,1):
  assert len(entries)>=12 and len({n for n,v,a in entries})==len(entries)
  assert len(prompt)<170
  sid=family+'-source';qn=f'q{index}';sourcefile=f'v25-{day}-{qn}-{family}.csv'
  question={'id':f'closeish_{day.replace("-", "")}_{qn}','date':day,'day_number':dayno,'topic':topic,'bank_id':family,'question_family':family,'prompt':prompt,
   'metric':metric,'unit':unit,'limit':limit,'direction':side,'comparison':'at_most' if side=='below' else 'at_least','time_limit_seconds':30,'boundary_inclusive':True,'input_max_length':180,
   'score_bands':[{'max_gap_inclusive':e,'points':p,'tier':t} for e,p,t in zip(bands,[1000,800,600,400,200],TIERS)],
   'scoring_window':{'max_scoring_distance':bands[-1],'units':unit,'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
   'source':urls[0],'source_refs':[sid],'verification_status':'source_list_completely_enumerated','editorial_status':'complete_checked_scheduled',
   'content_revision':'v25-20261029-nov04-nov05-1','metric_provenance':scope,'measurement_snapshot':f'Pinned source list; complete CSV: content/source-snapshots/{sourcefile}',
   'measurement':{'property':metric,'numeric_rule':rule,'unit':unit,'time_dependent':True,'source_urls':urls},
   'answer_scope':{'type':'source_defined_finite_named_universe','coverage':'complete_for_exact_prompt_universe','claimed_exhaustive':True,'entity_scope':scope,'dataset_count':len(entries),'known_unmeasured_count':0,'note':'All qualifying members of the stated bounded list are included, even wrong-side and no-score entries.'},
   'scoring_policy':'Verify membership; compare backend metric to the stated one-sided limit. Unverified submissions score zero.',
   'perfect_tier':{'points':1200,'tier':'PERFECT HIT','rule':'exact metric_value == limit'},
   'approach_rule':{'required_side':'from_above' if side=='above' else 'from_below','operator':'>=' if side=='above' else '<=','exact_target_allowed':True,'wrong_side_points':0,'exact_target_points':1200},'answers':[]}
  for i,(name,val,aliases) in enumerate(entries,1):
   p,tier=points(val,limit,side,bands)
   question['answers'].append({'entity_id':f'{family}-{i:03d}','canonical':name,'aliases':[{'input':alias,'kind':'documented_variant','action':'accept'} for alias in aliases],
     'verified_status':'source_row_or_rounded_source_value','source_refs':[{'source_id':sid,'locator':f'row-{i:03d}'}],
     'metric_value':val,'points':p,'tier':tier,'source_evidence':{'rule':rule}})
  coverage=collections.Counter(a['points'] for a in question['answers']); print(day,qn,topic,len(entries),dict(sorted(coverage.items())))
  assert set(coverage)=={0,200,400,600,800,1000,1200},f'MISSING TIERS {day} {qn} {dict(coverage)}'
  questions[qn]=question
  with (SNAP/sourcefile).open('w',encoding='utf8',newline='') as fh:
   writer=csv.writer(fh);writer.writerow(['entity_id','canonical','metric_value','points','tier','unit','source_url','source_row'])
   for i,a in enumerate(question['answers'],1):writer.writerow([a['entity_id'],a['canonical'],a['metric_value'],a['points'],a['tier'],unit,urls[0],i])
 dayjson={'schema_version':1,'date':day,'day_number':dayno,'revision':'v25-november-04-05-complete-1','publication_status':'scheduled',
    'editorial_note':'V23 six-topic diversity, frozen source-bounded full answer banks, server date gating; previous 12 days untouched.', 'questions':questions}
 (OUT/f'{day}.json').write_text(json.dumps(dayjson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
