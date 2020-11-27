"""
This program was made to help memorize something in chemistry class.

Since this is about naming in czech, a lot of variables will be in czech.
I'm sorry to anyone who hates this, but it's neccessary to make sense.
"""
import json
import re
from typing import List, Optional, Set, Tuple, Union

SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = str.maketrans("0123456789","¹²³⁴⁵⁶⁷⁸⁹⁰")
OXIDATION = ['^','ᶦ','ᶦᶦ','ᶦᶦᶦ','ᶦᵛ','ᵛ','ᵛᶦ','ᵛᶦᶦ']
NOR = str.maketrans("₀₁₂₃₄₅₆₇₈₉"+"¹²³⁴⁵⁶⁷⁸⁹⁰", "0123456789"*2)
RE_SIGN = r"^(\(?[A-Z][a-z]?\d{0,2} ?\)?)*$"
RE_NAME = r"^[^0-9]*$"

class NazvosloviException(Exception): pass
class IncorrectFormat(NazvosloviException): pass
class UnknownElement(NazvosloviException): pass
class WrongOxidation(NazvosloviException): pass

with open('tables/table.json', 'r') as file:
    table = json.load(file)
with open('tables/oxidation.json', 'r') as file:
    oxidation_table = json.load(file)
with open('tables/amount.json', 'r') as file:
    amount_table = json.load(file)

def is_compound_name(s: str, doraise: bool=True) -> bool:
    """
    Returns wheter a string is compound.
    True if matches `RE_NAME`, False if matches `RE_SIGN`.
    Raises `IncorrectFormat`, or returns None.
    """
    if re.match(RE_SIGN,s):
        return False
    elif re.match(RE_NAME,s):
        return True
    elif doraise:
        raise IncorrectFormat(f'Sloučenina "{s}" je v nesprávném formátu.')
    else:
        return None

def _get_possible_naming(naming: Optional[str]) -> Set[str]:
    """
    Takes an alement's naming attribute and returns all possible naming.
    This is for elements that remove a vowel.
    """
    if naming is None:
        return ()

    possible = {naming}
    possible.add(naming.replace('hel','hl'))
    
    return possible

def _load_oxidation(oxidation: str, tablekey='element') -> str:
    """
    Takes in an oxidation připona.
    Returns the oxidation number. 
    """
    for i,o in enumerate(oxidation_table[tablekey]):
        if oxidation == o:
            return i
    if 'ečn' in oxidation:
        return 5
    raise WrongOxidation(f'Nebyla rozpoznána koncovka oxidace "{oxidation}".')

def load_name(name: str, tablekey='element') -> Tuple[dict, int]:
    """
    Takes in an elements name, returns its data and oxidation.
    """
    for k, data in table.items():
        for naming in _get_possible_naming(data['naming']):
            if naming and name.startswith(naming):
                oxidation = name.replace(naming, '')
                data['naming'] = naming
                return (
                    data,
                    _load_oxidation(oxidation,tablekey)
                )
    
    raise UnknownElement('Nebyl rozpoznán prvek "{name}"')

def parse_element_sign(s: str) -> Tuple[str,int]:
    """
    Takes an element sign and returns the name and the amount.
    """
    if len(s)==1:
        return s,1
    else:
        if s[1].isdigit():
            return s[0], int(s[1:]) if s[1:] else 1
        else:
            return s[:2], int(s[2:]) if s[2:] else 1

def subscript(s: str, o: int=None) -> str:
    s = str(s).translate(SUB)
    if o is not None:
        if o>=0:
            return OXIDATION[o]+s
        else:
            return '⁻'+OXIDATION[-o]+s
    else:
        return s

class BaseCompound:
    """
    Base chemical compound.
    Has oxidation and amount.
    """
    typename: str = 'neznámá sloučenina'
    re_sign: re.Pattern = re.compile("")
    re_name: re.Pattern = re.compile("")
    oxidation: int = 0
    amount: int = 1
    def __init__(self, sign: str, name: bool=None):
        return
    def __repr__(self):
        """
        Returns the representation of the Compound.
        """
        return f'Compound<"{self.__str__()}" {self.oxidation}>'
    def tosign(self, oxidation: bool=False) -> str:
        """
        Returns the sign of the Compound.
        """
        s = self._tosign(oxidation)
        if self.amount!=1 or (oxidation and self.oxidation!=0):
            return '('+s+')'+subscript(self.amount if self.amount!=1 else '', self.oxidation if oxidation else None)
        else:
            return s
    def _tosign(self, oxidation: bool=False) -> str:
        """
        Returns the sign of the Compound without any brackets.
        """
        return 'CompoundSign'
    def toname(self) -> str:
        """
        Returns the name of the Compound.
        """
        return 'CompoundName'
    def __str__(self) -> str:
        """
        Returns the sign of the Compound.
        """
        return self.tosign()
    
    @property
    def name(self):
        return self.toname()
    @property
    def sign(self):
        return self.tosign(False)
    @property
    def oxisign(self):
        return self.tosign(True)

class Element(BaseCompound):
    """
    A default chemical Element.
    Has oxidation and amount.
    
    Oxidation may be None=unknown
    """
    typename = 'prvek'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2}$")
    re_name = re.compile(r"^[^ 0-9]*$")

    def __init__(self, sign: str, name: bool=None, tablekey='element', *, amount: int=None, oxidation: int=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        You can specify if the name is and acid-like or a salt-like.
        Amount and oxiditaion can be set specially.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # simply load the name
            self._data, self.oxidation = load_name(sign.lower(),tablekey)
        else:
            # parse sign
            sign,self.amount = parse_element_sign(sign)
            # set data and set oxidation as unknown
            self._data = table[sign.title()]
            self.oxidation = None
        
        # set the special variables
        if oxidation is not None:
            self.oxidation = oxidation
        if amount is not None:
            self.amount = amount
    
    def get_oxidation(self):
        """
        Returns amount*oxidation.
        """
        return self.oxidation*self.amount
    
    def __repr__(self):
        return f'Element<"{self._data["sign"]}{self.amount}" {self.oxidation}>'

    def tosign(self, oxidation: bool=False):
        return self._data['sign']+subscript(self.amount if self.amount!=1 else '',self.oxidation if oxidation else None)
    
    def toname(self,tablekey='element'):
        if self.oxidation is not None and self.oxidation>0:
            oxidation_name = oxidation_table[tablekey][self.oxidation]
            return self._data['naming']+oxidation_name
        else:
            return self._data['name']

class SingleElementCompound(BaseCompound):
    """
    Base compound for oxids, sulfids, etc.
    """
    typename = 'neznámá dvouprvková sloučenina'
    main_sign = ''
    main_name = ''
    main_oxidation = 0
    def __init__(self, sign: str, name=None):
        if name is None:
            name = is_compound_name(sign)
        if name:
            main,alt = sign.split()
            self.main = Element(self.main_sign,False)
            self.alt = Element(alt,True)
            self.main.oxidation = self.main_oxidation
            self.main.amount,self.alt.amount = self.alt.oxidation,-self.main.oxidation
        else:
            alt,main = sign.split()
            self.main = Element(main,oxidation=self.main_oxidation)
            self.alt = Element(alt)
            self.alt.oxidation = -self.main.get_oxidation() // self.alt.amount
    
    def tosign(self, oxidation: bool=False):
        return self.alt.tosign(oxidation)+self.main.tosign(oxidation)
    def toname(self):
        return self.main_name+' '+self.alt.toname()
    

class Oxid(SingleElementCompound):
    """
    An Oxid+Element chemical Compound.
    """
    typename = 'oxid'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?O\d{0,2}$") # `element_sign`+oxid sign
    re_name = re.compile(r"^oxid [^ 0-9]*$") # "oxid "+`element_name`
    main_sign = 'O'
    main_name = 'oxid'
    main_oxidation = -2
class Sulfid(SingleElementCompound):
    """
    An Oxid+Element chemical Compound.
    """
    typename = 'sulfid'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?S\d{0,2}$") # `element_sign`+sulfid sign
    re_name = re.compile(r"^sulfid [^ 0-9]*$") # "oxid "+`element_name`
    main_sign = 'S'
    main_name = 'sulfid'
    main_oxidation = -2

class Acid(BaseCompound):
    typename = 'kyselina'
    re_sign = re.compile(r"^H\d{0,2} ?[A-Z][a-z]?\d{0,2} ?O\d{0,2}$") # Hx+Xx+Ox
    re_name = re.compile(r"^kyselina ([a-z]{2,6}hydrogen )?[^ 0-9]*$") # 'kyselina'+hydrogen+`element_name`
    def __init__(self, sign, name: bool=None):
        if name is None:
            name = is_compound_name(sign)
        if name:
            if 'hydrogen' in sign:
                acid,hydrogen,element = sign.split()
                hydrogen = amount_table.index(hydrogen[:-len('hydrogen')])
                self.element = Element(element,True,tablekey='acid')
            else:
                acid,element = sign.split()
                self.element = Element(element,True,tablekey='acid')
                if self.element.get_oxidation() %2 == 0:
                    hydrogen = 2
                else:
                    hydrogen = 1
            self.hydrogen = Element(f'H',amount=hydrogen, oxidation=1)
            self.oxygen = Element(f'O',amount=(self.hydrogen.get_oxidation()+self.element.get_oxidation())//2,oxidation=-2)
        else:
            hydrogen,element,oxygen = sign.split()
            self.hydrogen = Element(hydrogen, oxidation=1)
            self.oxygen = Element(oxygen, oxidation=-2)
            self.element = Element(element, oxidation=-(self.oxygen.get_oxidation()+self.hydrogen.get_oxidation()))
    
    def tosign(self, oxidation: bool=False):
        return self.hydrogen.tosign(oxidation)+self.element.tosign(oxidation)+self.oxygen.tosign(oxidation)
    
    def toname(self, dohydrogen=True):
        return 'kyselina '+(
            amount_table[self.hydrogen.amount]+'hydrogen ' if dohydrogen and self.hydrogen.amount>2 else ''
            )+self.element.toname('acid')

class SaltAcid(BaseCompound):
    typename = 'kyselina soli'
    def __init__(self, sign: str, name: bool=None, oxidation: int=...):
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            self.element = Element(sign,True,'salt')
            if self.element.get_oxidation() %2 == 0:
                self.oxidation = -2
            else:
                self.oxidation = -1
            self.oxygen = Element(f'O',amount=(self.element.get_oxidation()-self.oxidation)//2,oxidation=-2)
        else:
            if '(' in sign:
                sign,amount = sign[1:].split(')')
                self.amount = int(amount)
            else:
                self.amount = 1
            element,oxygen = sign.split()
            self.element = Element(element)
            self.oxygen = Element(oxygen,oxidation=-2)
            self.element.oxidation = -(self.oxygen.get_oxidation()-oxidation)
            self.oxidation = oxidation
    
    def _tosign(self, oxidation: bool=False):
        return self.element.tosign(oxidation)+self.oxygen.tosign(oxidation)
    
    def toname(self):
        return self.element.toname('salt')

class Salt(BaseCompound):
    typename = 'sůl'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?\(?[A-Z][a-z]?\d{0,2} ?O\d{0,2}\)?\d{0,2}?$") # `element_sign`+('(')+`element_sign`+'O'x+(')')
    re_name = re.compile(r"^(?![a-z]*hydrogen)[^ 0-9]*an [^ 0-9]*$") # `element_name`+'an'+`element_name`
    def __init__(self, sign: str, name: bool=None):
        if name is None:
            name = is_compound_name(sign)
        if name:
            acid,element = sign.split()
            self.element = Element(element,True)
            self.acid = SaltAcid(acid,True)
            self.element.oxidation,self.acid.amount = self.acid.amount,self.element.oxidation
        else:
            element,acid = sign.split(maxsplit=1)
            
            self.element = Element(element)
            self.acid = SaltAcid(acid,False,oxidation=-self.element.amount)
            self.element.oxidation = self.acid.amount
    
    def tosign(self, oxidation):
        return self.element.tosign(oxidation)+self.acid.tosign(oxidation)
    
    def toname(self):
        return self.acid.toname()+' '+self.element.toname()

class HydrogenAcid(BaseCompound):
    typename = 'kyselina hydrogensoli'
    amount = 1
    def __init__(self, sign: str, name: bool=None, oxidation: int=...):
        if name is None:
            name = is_compound_name(sign)
        if name:
            expected_hydrogen,element = sign.split('hydrogen')
            # get the amount of hydrogens that will stay in acid
            if expected_hydrogen:
                expected_hydrogen = amount_table.index(expected_hydrogen)
            else:
                expected_hydrogen = 1
            
            # make acid
            self.element = Element(element,True,tablekey='salt')
            if self.element.get_oxidation() %2 == 0:
                hydrogens = 2
            else:
                hydrogens = 1
            
            if hydrogens <= expected_hydrogen:
                missing_hydrogens = expected_hydrogen-hydrogens+1
                missing_hydrogens += missing_hydrogens%2
                hydrogens += missing_hydrogens
            
            self.hydrogen = Element('H',amount=hydrogens,oxidation=1)
            self.oxygen = Element('O',amount=(self.hydrogen.get_oxidation()+self.element.get_oxidation())//2,oxidation=-2)
            
            # take out hydrogens
            self.oxidation = expected_hydrogen-self.hydrogen.amount
            self.hydrogen.amount = expected_hydrogen
            
        else:
            if '(' in sign:
                sign,amount = sign[1:].split(')')
                self.amount = int(amount)
            else:
                self.amount = 1
            expected_hydrogen,element,oxygen = sign.split()
            self.hydrogen = Element(expected_hydrogen,oxidation=1)
            self.oxygen = Element(oxygen,oxidation=-2)
            self.element = Element(element,oxidation=-(self.oxygen.get_oxidation()+self.hydrogen.get_oxidation()-oxidation))
            self.oxidation = oxidation
    
    def _tosign(self, oxidation: bool=False):
        return self.hydrogen.tosign(oxidation)+self.element.tosign(oxidation)+self.oxygen.tosign(oxidation)
    
    def toname(self, dohydrogen=True):
        return (amount_table[self.hydrogen.amount] if self.hydrogen.amount!=1 else '')+'hydrogen'+self.element.toname('salt')

class HydrogenSalt(BaseCompound):
    typename = 'hydrogensůl'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?\(?H\d{0,2} ?[A-Z][a-z]?\d{0,2} ?O\d{0,2}\)?\d{0,2}?$") # `element_sign`+('(')+'H'x+`element_sign`+'O'x+(')')
    re_name = re.compile(r"^([a-z]{2,6})?hydrogen[^ 0-9]*an [^ 0-9]*$") # hydrogen+`element_name`an+`element_name`
    def __init__(self, sign: str, name: bool=None):
        if name is None:
            name = is_compound_name(sign)
        if name:
            acid,element = sign.split()
            self.acid = HydrogenAcid(acid,True)
            self.element = Element(element,True,amount=-self.acid.oxidation)
            self.acid.amount = self.element.oxidation
        else:
            element,acid = sign.split(maxsplit=1)
            self.element = Element(element)
            self.acid = HydrogenAcid(acid,False,-self.element.amount)
            self.element.oxidation = self.acid.amount
    
    def tosign(self, oxidation):
        return self.element.tosign(oxidation)+self.acid.tosign(oxidation)
    def toname(self):
        return self.acid.toname()+' '+self.element.toname()

class SaltHydrate(BaseCompound):
    typename = 'hydrát soli'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?\(?[A-Z][a-z]?\d{0,2} ?O\d{0,2}\)?\d{0,2}? . \d{1,2} H2 O$") # `element_sign`+('(')+`element_sign`+'O'x+(')')+'.'+X'H20'
    re_name = re.compile(r"^[a-z]{2,6}hydrát [^ 0-9]*anu [^ 0-9]*ého$") # X`hydrate`+`element_name`+'an'+`element_name`
    def __init__(self, sign: str, name: bool=None):
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            hydrate,salt_acid,salt_element = sign.split()
            self.hydrate = amount_table.index(hydrate[:-6])
            salt_acid = salt_acid[:-1] # uhličitan[u]
            salt_element = salt_element[:-3]+'ý' # měďnat[ého]ý
            self.salt = Salt(salt_acid+' '+salt_element,True)
        else:
            salt,hydrate = sign.split('.')
            self.salt = Salt(salt.strip(),False)
            self.hydrate = int(hydrate.replace(' ','')[:-3])

    def tosign(self, oxidation):
        hydrate_s = 'H'+subscript(2, 1 if oxidation else None)+'O'+subscript('', -2 if oxidation else None)
        return self.salt.tosign(oxidation)+' . '+str(self.hydrate)+hydrate_s
    
    def toname(self):
        salt_acid,salt_element = self.salt.toname().split()
        return amount_table[self.hydrate]+'hydrát '+salt_acid+'u '+salt_element[:-1]+'ého'


COMPOUNDS: List[BaseCompound] = [Oxid,Sulfid,Acid,Salt,HydrogenSalt,SaltHydrate]
pstring = """
-- {entry}
typ sloučeniny: {typename}
název: {name}
vzoreček: {sign}
vzoreček s oxi.: {oxisign}
""".strip()

def fix_Compound_sign(s: str) -> str:
    """
    Takes in a sign and adds a space after every element.
    """
    s = s.translate(NOR)
    out = ''
    for i in s:
        if out and i not in ' ' and (i.isupper() or i in '(.' or out[-1] in '.') and out[-1] not in '( ':
            out += ' '+i
        else:
            out += i
    return out
    

def recognize(s: str) -> Union[BaseCompound,None,NazvosloviException]:
    """
    Recognizes a regural experession and returns a Compound class.
    """
    name = s
    sign = fix_Compound_sign(s)
    try:
        for compound in COMPOUNDS:
            if compound.re_name.match(name):
                return compound(name, True)
            elif compound.re_sign.match(sign):
                return compound(sign, False)
    except NazvosloviException as e:
        return e
    else:
        return None

def pprint(compound: BaseCompound, entry: str='neznámé') -> str:
    return pstring.format(
        entry=entry,
        typename=compound.typename,
        name=compound.name,
        sign=compound.sign,
        oxisign=compound.oxisign
    )
