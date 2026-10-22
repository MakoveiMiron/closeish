# Day 4: new source-backed candidate questions

q1: cinema | Name a film in the frozen IMDb top-100 selection with a runtime of at least 119 minutes. | 102 records | {'1200': 2, '1000': 5, '800': 1, '600': 7, '400': 12, '200': 17, '0': 58} | scope=full_explicit_selection

q2: maritime-history | Name a Titanic passenger whose recorded ticket fare was at least £55. | 891 records | {'1200': 2, '1000': 10, '800': 2, '600': 15, '400': 25, '200': 38, '0': 799} | scope=partial_frozen_source

q3: music | Name a song in the frozen Spotify 2023 top-100 streams list with no more than 1814 million recorded streams. | 100 records | {'1200': 2, '1000': 2, '800': 4, '600': 6, '400': 9, '200': 16, '0': 61} | scope=full_explicit_selection

q4: motorsport | Name a Formula One driver from the archived driver selection who was born in 1958 or later. | 155 records | {'1200': 2, '1000': 6, '800': 12, '600': 14, '400': 22, '200': 41, '0': 58} | scope=partial_frozen_source

q5: travel | Name a city within 4792 km of Budapest, by great-circle distance. | 971 records | {'1200': 2, '1000': 11, '800': 24, '600': 42, '400': 66, '200': 109, '0': 717} | scope=partial_frozen_source

q6: timekeeping | Name an IANA city time zone whose UTC offset on 15 January 2026 was at most +390 minutes. | 386 records | {'1200': 2, '1000': 10, '800': 27, '600': 63, '400': 47, '200': 99, '0': 138} | scope=full_explicit_selection

**Warning:** Source subsets are not globally exhaustive, and days 5–6 still await replacement. This is not a final release.
