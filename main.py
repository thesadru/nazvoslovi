from nazvoslovi import BaseCompound, pprint, recognize, NazvosloviException, COMPOUNDS
import sys
import json

if len(sys.argv)==1:
    entry = input('napiš sloučeninu: ')
    do_json = False
else:
    if sys.argv[1] == 'help':
        quit(print('známé sloučeniny: '+', '.join(c.typename for c in COMPOUNDS)))
    do_json = '--json' in sys.argv
    entry = sys.argv[1]

compound = recognize(entry)
if isinstance(compound,NazvosloviException):
    quit(print(compound))

if do_json:
    print(json.dumps(compound.todict() if compound is BaseCompound else None))
else:
    if compound is None:
        print(f'sloučenina "{entry}" nebyla rozpoznána')
    else:
        print('\n'+pprint(compound,entry))
