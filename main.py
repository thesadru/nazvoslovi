from nazvoslovi import pprint, recognize, NazvosloviException, COMPOUNDS
import sys
import json

if len(sys.argv)==1:
    entry = input('napiš sloučeninu: ')
    do_json = False
else:
    if sys.argv[1] == 'help':
        print('známé sloučeniny: '+', '.join(c.typename for c in COMPOUNDS))
        quit()
    do_json = '--json' in sys.argv
    entry = sys.argv[1]

compound = recognize(entry)
if compound is None:
    print(f'sloučenina "{entry}" nebyla rozpoznána')
elif isinstance(compound,NazvosloviException):
    print(compound)
else:
    if do_json:
        print(json.dumps(compound.todict()))
    else:
        print('\n'+pprint(compound,entry))
