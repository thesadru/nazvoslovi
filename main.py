from nazvoslovi import pprint, recognize
import sys

if len(sys.argv)==1:
    entries = [input('napiš sloučeninu: ')]
else:
    entries = sys.argv[1:]

for entry in entries:
    compound = recognize(entry)
    if compound is None:
        print(f'sloučenina "{entry}" nebyla rozpoznána')
    else:
        print('\n'+pprint(compound,entry))
