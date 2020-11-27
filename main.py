from nazvoslovi import pprint, recognize
import sys

if len(sys.argv)==1:
    entry = input('napiš sloučeninu: ')
else:
    entry = sys.argv[1]

compound = recognize(entry)
if compound is None:
    print(f'sloučenina "{entry}" nebyla rozpoznána')
else:
    print('\n'+pprint(compound,entry))
