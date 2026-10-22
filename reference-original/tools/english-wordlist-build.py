#!/usr/bin/env python3
"""Build a deduplicated English headword corpus from local cmudict 1.1.3
and SCOWL-derived en_US Hunspell sources, including valid inflections.
Only A-Z spellings are eligible for the A1Z26 quiz. Source provenance is retained.
"""
from __future__ import annotations
import cmudict
import re
from collections import Counter
from pathlib import Path

OUT=Path('/mnt/data/closeish-english-headwords.tsv')
AFF=Path('/usr/share/hunspell/en_US.aff')
DIC=Path('/usr/share/hunspell/en_US.dic')
RULES={}
CROSS={}
for line in AFF.read_text('utf-8').splitlines():
    a=line.split()
    if len(a)==4 and a[0] in {'PFX','SFX'} and a[2] in {'Y','N'} and a[3].isdigit():
        kind,flag,yn,_=a
        RULES[(kind,flag)]=[]
        CROSS[(kind,flag)]=yn=='Y'
    elif len(a)>=5 and a[0] in {'PFX','SFX'}:
        kind,flag,strip,add,condition=a[:5]
        if (kind,flag) not in RULES: continue
        try:regex=re.compile(('^' if kind=='PFX' else '')+condition+('$' if kind=='SFX' else ''))
        except re.error:continue
        RULES[(kind,flag)].append((str() if strip=='0' else strip, str() if add=='0' else add, regex))

def apply(word,kind,rules):
    ans=[]
    for strip,add,condition in rules:
        if not condition.search(word):continue
        if strip and (not word.startswith(strip) if kind=='PFX' else not word.endswith(strip)):
            continue
        if kind=='PFX': new=add+(word[len(strip):] if strip else word)
        else: new=(word[:-len(strip)] if strip else word)+add
        if new.isascii() and new.isalpha():ans.append(new.lower())
    return ans

words={}
for w in cmudict.words():
    w=w.lower()
    if w.isascii() and w.isalpha():words[w]=1
ncmu=len(words)
root_count=0
for line in DIC.read_text('utf-8').splitlines()[1:]:
    raw=line.strip().split(None,1)[0]
    if not raw:continue
    if '/' in raw: word,flags=raw.rsplit('/',1)
    else: word,flags=raw,''
    if not word.isascii() or not word.isalpha():continue
    root_count+=1
    word=word.lower()
    words[word]=words.get(word,0)|2
    prefix_flags=[flag for flag in flags if ('PFX',flag) in RULES]
    suffix_flags=[flag for flag in flags if ('SFX',flag) in RULES]
    prefixes=[]
    suffixes=[]
    for f in prefix_flags:
        prefixes.extend((f,w) for w in apply(word,'PFX',RULES[('PFX',f)]))
    for f in suffix_flags:
        suffixes.extend((f,w) for w in apply(word,'SFX',RULES[('SFX',f)]))
    for _,w in prefixes+suffixes: words[w]=words.get(w,0)|2
    # Hunspell cross-products only if BOTH rules are explicitly cross-productable.
    for fp,pref in prefixes:
        if not CROSS[('PFX',fp)]:continue
        for fs in suffix_flags:
            if not CROSS[('SFX',fs)]:continue
            for w in apply(pref,'SFX',RULES[('SFX',fs)]):words[w]=words.get(w,0)|2

with OUT.open('w',encoding='utf-8',newline='\n') as f:
    for word in sorted(words):f.write(f'{word}\t{words[word]}\n')

stats=Counter(words.values())
print('cmu alphabetic unique:',ncmu)
print('Hunspell alphabetic root entries:',root_count)
print('Union words (CMU + Hunspell stems and inflections):',len(words))
print('provenance flags 1 cmu, 2 hunspell, 3 both:',dict(stats))
print('out:',OUT,'bytes',OUT.stat().st_size)
