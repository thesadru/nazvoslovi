"""
This program was made to help memorize naming of chemical compound in czech.
Since czech is very... unique,  this was more complicated than expected.

I can't be bothered to make czech comments, I just kept english ones.
People who speak english will be reading this anyway, so it doesn't matter.
"""
import json
import re
from typing import List, Optional, Set, Tuple, Union
from math import gcd

# constants for detection and formatting of compounds
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = str.maketrans("0123456789","⁰¹²³⁴⁵⁶⁷⁸⁹")
OXIDATION = ['^','ᶦ','ᶦᶦ','ᶦᶦᶦ','ᶦᵛ','ᵛ','ᵛᶦ','ᵛᶦᶦ']
NOR = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
RE_SIGN = r"^(\(?[A-Z][a-z]?\d{0,2} ?\)?)*$"
RE_NAME = r"^[^0-9]*$"

# Exceptions
class NazvosloviException(Exception): pass
class IncorrectFormat(NazvosloviException): pass
class UnknownElement(NazvosloviException): pass
class WrongOxidation(NazvosloviException): pass

# load tables
with open('tables/table.json', 'r') as file:
    table = json.load(file)
with open('tables/oxidation.json', 'r') as file:
    oxidation_table = json.load(file)
with open('tables/amount.json', 'r') as file:
    amount_table = json.load(file)

# functions for creating compounds
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
    
    raise UnknownElement(f'Nebyl rozpoznán prvek "{name}"')

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

def subscript(amount: int, oxidation: int=None) -> str:
    """
    Takes an amount and optional oxidation.
    Creates subscript for amount and roman superscript for oxidation.
    Used to prettify the info.
    """
    amount = str(amount).translate(SUB)
    if oxidation is not None:
        if oxidation>=0:
            return OXIDATION[oxidation]+amount
        else:
            return '⁻'+OXIDATION[-oxidation]+amount
    else:
        return amount

def factor(x,y) -> Tuple[int,int]:
    """
    Takes in two integers and divides tham by their greatest common denominator.
    """
    g = gcd(x,y)
    return x//g,y//g

def cross_rule(x,y) -> Tuple[int,int]:
    """
    Takes in a tuple of amounts or oxidation, returns their output of cross rule.
    If amount is given, y will be the negative one.
    If oxidation is given, it's expected y is the negative one.
    
    ```
    x.oxidation,y.oxidation = cross_rule(x.amount,y.amount)
    ```
    """
    x,y = factor(x,y)
    # this is simply for simplicity outside the function
    if y>=0:
        return y,-x
    else:
        return -y,x

# =============================================================================
# Compounds

class BaseCompound:
    """
    Base chemical compound.
    Every compound has a typename.
    Has oxidation and amount.
    
    Contains a regex for sign and name for automatically recognizing compounds.
    """
    typename: str = 'neznámá sloučenina'
    re_sign: re.Pattern = re.compile("")
    re_name: re.Pattern = re.compile("")
    oxidation: int = 0
    amount: int = 1
    
    def __init__(self, sign: str, name: bool=None, **special_kwargs):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        """
        return
    
    def __repr__(self):
        """Returns the representation of the Compound."""
        return self.__class__.__name__+f'<"{self.__str__()}" {self.oxidation}>'
    
    def tosign(self, oxidation: bool=False) -> str:
        """Returns the sign of the Compound."""
        s = self._tosign(oxidation)
        if self.amount!=1 or (oxidation and self.oxidation!=0):
            return '('+s+')'+subscript(self.amount if self.amount!=1 else '', self.oxidation if oxidation else None)
        else:
            return s
    
    def _tosign(self, oxidation: bool=False) -> str:
        """Returns the sign of the Compound without any brackets."""
        return 'CompoundSign'
    
    def toname(self) -> str:
        """Returns the name of the Compound."""
        return 'CompoundName'
    
    def __str__(self) -> str:
        """Returns the sign of the Compound."""
        return self.tosign()
    
    @property
    def name(self) -> str:
        """Name of compound."""
        return self.toname()
    @property
    def sign(self) -> str:
        """Sign of compound."""
        return self.tosign(False)
    @property
    def oxisign(self) -> str:
        """Sign of compound with oxidation."""
        return self.tosign(True)

class Element(BaseCompound):
    """
    A default chemical Element.
    Has oxidation and amount.
    
    Oxidation may be None (unknown).
    """
    typename = 'prvek'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2}$")
    re_name = re.compile(r"^[^ 0-9]*$")

    def __init__(self, sign: str, name: bool=None, *, tablekey='element', amount: int=None, oxidation: int=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        
        You can specify if the name is element-like, acid-like or a salt-like.
        Amount and oxiditaion can be set specially, should be used for compounds.
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
    
    def get_oxidation(self) -> int:
        """Returns amount*oxidation."""
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
    
    For inheretance, you must set a `main_sign`, `main_name` and `main_oxidation`.
    """
    typename = 'neznámá dvouprvková sloučenina'
    main_sign = ''
    main_name = ''
    main_oxidation = 0
    
    def __init__(self, sign: str, name=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # take out the name of main element out of sign
            main,alt = sign.split()
            # create elements
            self.main = Element(self.main_sign, False, oxidation=self.main_oxidation)
            self.alt = Element(alt,True)
            # do cross rule to complete
            self.main.amount,self.alt.amount = cross_rule(self.main.oxidation,self.alt.oxidation)
        else:
            # take out the sign of main element out of sign
            alt,main = sign.split()
            # create elements
            self.main = Element(main, oxidation=self.main_oxidation)
            self.alt = Element(alt)
            self.alt.oxidation = -self.main.get_oxidation()//self.alt.amount
            self.main.amount,self.alt.amount = factor(self.main.amount,self.alt.amount) # somewhere in the code an errror was caused
    
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
    """
    An Acid compound containg hydrogen, an element and oxygen.
    
    Only oxidized acids are allowed.
    """
    typename = 'kyselina'
    re_sign = re.compile(r"^H\d{0,2} ?[A-Z][a-z]?\d{0,2} ?O\d{0,2}$") # Hx+Xx+Ox
    re_name = re.compile(r"^kyselina ([a-z]{2,6}hydrogen )?[^ 0-9]*$") # 'kyselina'+hydrogen+`element_name`
    
    def __init__(self, sign, name: bool=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # acid is only a literal "kyselina"
            if 'hydrogen' in sign:
                # take out hydrogen and element
                acid,element = sign.split()
                hydrogen,element = element.split('hydrogen')
                # figure out the number of hydrogens
                hydrogen = amount_table.index(hydrogen)
                # create the element with the acid
                self.element = Element(element,True,tablekey='acid')
            else:
                # take out an element
                acid,element = sign.split()
                # create the element with the acid
                self.element = Element(element,True,tablekey='acid')
                # figure out the number of hydrogens
                hydrogen = 2 if self.element.get_oxidation()%2 == 0 else 0
            
            # create the hydrogens
            self.hydrogen = Element(f'H',amount=hydrogen, oxidation=1)
            # create the oxygen by completing oxidation so it's 0
            self.oxygen = Element(f'O',amount=(self.hydrogen.get_oxidation()+self.element.get_oxidation())//2,oxidation=-2)
        else:
            # take out hydrogen, element and oxygen
            hydrogen,element,oxygen = sign.split()
            # create obvious hydrogen and oxygen
            self.hydrogen = Element(hydrogen, oxidation=1)
            self.oxygen = Element(oxygen, oxidation=-2)
            # figure out the element by completing oxidation so it's 0
            self.element = Element(element, oxidation=-(self.oxygen.get_oxidation()+self.hydrogen.get_oxidation()))
    
    def tosign(self, oxidation: bool=False):
        return self.hydrogen.tosign(oxidation)+self.element.tosign(oxidation)+self.oxygen.tosign(oxidation)
    
    def toname(self, dohydrogen=True):
        """Returns the name of the Compound. Can remove the "hydrogen" part"""
        return 'kyselina '+(
            amount_table[self.hydrogen.amount]+'hydrogen ' if dohydrogen and self.hydrogen.amount>2 else ''
            )+self.element.toname('acid')

class SaltAcid(BaseCompound):
    """
    An acid without any hydrogen.
    
    Used as the acid part for salt.
    """
    typename = 'kyselina soli'
    
    def __init__(self, sign: str, name: bool=None, amount: int=..., oxidation: int=...):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        
        You must set an oxidation and amount if giving a sign.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # create the element from the name
            self.element = Element(sign,True,tablekey='salt')
            # complete oxidation
            self.oxidation = -2 if self.element.get_oxidation()%2 == 0 else -1
            # figure out the oxygen by completing oxidation so it's `self.oxidation`
            self.oxygen = Element(f'O',amount=(self.element.get_oxidation()-self.oxidation)//2,oxidation=-2)
            
        else:
            # save oxidation and amount
            self.oxidation = oxidation
            self.amount = amount
            # take out element and oxygen
            element,oxygen = sign.split()
            # create element and oxygen
            self.oxygen = Element(oxygen,oxidation=-2)
            # figure out the oxygen by completing oxidation so it's `self.oxidation`
            self.element = Element(element,oxidation=-(self.oxygen.get_oxidation()-self.oxidation))
    
    def _tosign(self, oxidation: bool=False):
        return self.element.tosign(oxidation)+self.oxygen.tosign(oxidation)
    
    def toname(self):
        return self.element.toname('salt')

class Salt(BaseCompound):
    """
    A salt, containing an element and a salt without hydrogen.
    """
    typename = 'sůl'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?\(?[A-Z][a-z]?\d{0,2} ?O\d{0,2}\)?\d{0,2}?$") # `element_sign`+('(')+`element_sign`+'O'x+(')')
    re_name = re.compile(r"^(?![a-z]*hydrogen)[^ 0-9]*an [^ 0-9]*$") # `element_name`+'an'+`element_name`
    
    def __init__(self, sign: str, name: bool=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # take out acid and element
            acid,element = sign.split()
            # create element and acid
            self.element = Element(element,True)
            self.acid = SaltAcid(acid,True)
            # use cross rule
            self.element.amount,self.acid.amount = cross_rule(self.element.oxidation,self.acid.oxidation)
        else:
            # take out element and acid
            element,acid = sign.split(maxsplit=1)
            # figure out the acid amount in case it is set, otherwise 1
            if '(' in acid:
                acid,acid_amount = acid[1:].split(')')
                acid_amount = int(acid_amount)
            else:
                acid_amount = 1
            # create element and acid
            self.element = Element(element)
            # use cross rule
            self.element.oxidation,acid_oxidation = cross_rule(self.element.amount,acid_amount)
            self.acid = SaltAcid(acid,False,amount=acid_amount,oxidation=acid_oxidation)
    
    def tosign(self, oxidation: bool=False):
        return self.element.tosign(oxidation)+self.acid.tosign(oxidation)
    
    def toname(self):
        return self.acid.toname()+' '+self.element.toname()

class HydrogenAcid(BaseCompound):
    """
    An acid with only some hydrogen.
    
    Used in hydrogen salt.
    """
    typename = 'kyselina hydrogensoli'
    amount = 1
    
    def __init__(self, sign: str, name: bool=None, amount: int=..., oxidation: int=...):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        
        You must set an amount and oxidation if giving a sign.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # take out the wanted hydrogens and element
            expected_hydrogen,element = sign.split('hydrogen')
            # get the amount of hydrogens that will stay in acid
            if expected_hydrogen:
                expected_hydrogen = amount_table.index(expected_hydrogen)
            else:
                expected_hydrogen = 1
            # make acid
            self.element = Element(element,True,tablekey='salt')
            # figure out hydrogens
            hydrogens = 2 if self.element.get_oxidation()%2 == 0 else 1
            # complete the missing hydrogens so there's no negative hydrogens
            if hydrogens <= expected_hydrogen:
                missing_hydrogens = expected_hydrogen-hydrogens+1
                # add missing hydrogens, must be even
                hydrogens += missing_hydrogens+(missing_hydrogens%2)
            # create hydrogen and oxygen
            self.hydrogen = Element('H',amount=hydrogens,oxidation=1)
            # figure out the oxygen by completing oxidation so it's 0
            self.oxygen = Element('O',amount=(self.hydrogen.get_oxidation()+self.element.get_oxidation())//2,oxidation=-2)
            # take out hydrogens
            self.oxidation = expected_hydrogen-self.hydrogen.amount
            self.hydrogen.amount = expected_hydrogen
            
        else:
            # save oxidation and amount
            self.oxidation = oxidation
            self.amount = amount
            
            # take out expected hydrogen, element and oxygen
            expected_hydrogen,element,oxygen = sign.split()
            # create hydrogen, oxygen and element
            self.hydrogen = Element(expected_hydrogen,oxidation=1)
            self.oxygen = Element(oxygen,oxidation=-2)
            # figure out the oxygen by completing oxidation so it's 0
            self.element = Element(element,oxidation=-(self.oxygen.get_oxidation()+self.hydrogen.get_oxidation()-self.oxidation))
    
    def _tosign(self, oxidation: bool=False):
        return self.hydrogen.tosign(oxidation)+self.element.tosign(oxidation)+self.oxygen.tosign(oxidation)
    
    def toname(self, dohydrogen=True):
        return (amount_table[self.hydrogen.amount] if self.hydrogen.amount!=1 else '')+'hydrogen'+self.element.toname('salt')

class HydrogenSalt(BaseCompound):
    """
    A salt with and acid that has hydrogens.
    """
    typename = 'hydrogensůl'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?\(?H\d{0,2} ?[A-Z][a-z]?\d{0,2} ?O\d{0,2}\)?\d{0,2}?$") # `element_sign`+('(')+'H'x+`element_sign`+'O'x+(')')
    re_name = re.compile(r"^([a-z]{2,6})?hydrogen[^ 0-9]*an [^ 0-9]*$") # hydrogen+`element_name`an+`element_name`
    def __init__(self, sign: str, name: bool=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # take out acid and element
            acid,element = sign.split()
            # create acid and element
            self.acid = HydrogenAcid(acid,True)
            self.element = Element(element,True)
            # use cross rule
            self.element.amount,self.acid.amount = cross_rule(self.element.oxidation,self.acid.oxidation)
        else:
            # take out element and acid
            element,acid = sign.split(maxsplit=1)
            # figure out the acid amount in case it is set, otherwise 1
            if '(' in acid:
                acid,acid_amount = acid[1:].split(')')
                acid_amount = int(acid_amount)
            else:
                acid_amount = 1
            # create acid and element
            self.element = Element(element)
            # use cross rule
            
            self.element.oxidation,acid_oxidation = cross_rule(self.element.amount,acid_amount)
            self.acid = HydrogenAcid(acid,False, amount=acid_amount,oxidation=acid_oxidation)
    
    def tosign(self, oxidation: bool=False):
        return self.element.tosign(oxidation)+self.acid.tosign(oxidation)
    
    def toname(self):
        return self.acid.toname()+' '+self.element.toname()

class SaltHydrate(BaseCompound):
    """
    A salt with attached water.
    """
    typename = 'hydrát soli'
    re_sign = re.compile(r"^[A-Z][a-z]?\d{0,2} ?\(?[A-Z][a-z]?\d{0,2} ?O\d{0,2}\)?\d{0,2}? . \d{1,2} H2 O$") # `element_sign`+('(')+`element_sign`+'O'x+(')')+'.'+X'H20'
    re_name = re.compile(r"^[a-z]{2,6}hydrát [^ 0-9]*anu [^ 0-9]*ého$") # X`hydrate`+`element_name`+'an'+`element_name`
    def __init__(self, sign: str, name: bool=None):
        """
        Takes in a sign and creates an element with it.
        You can specify wheter the element is a name or a sign with `name`.
        If not set, it is automatically figured out with regex.
        """
        if name is None:
            name = is_compound_name(sign)
        
        if name:
            # take out hydrate and salt
            hydrate,salt_acid,salt_element = sign.split()
            # figure out the hydrate
            self.hydrate = amount_table.index(hydrate[:-6])
            # turn salt into a correct form and create it
            # for example: uhličitan[u] měďnat[ého]ý
            self.salt = Salt(salt_acid[:-1]+' '+salt_element[:-3]+'ý',True)
        else:
            # take out salt and hydrate
            salt,hydrate = sign.split('.')
            # create salt and figure out hydrate
            self.salt = Salt(salt.strip(),False)
            self.hydrate = int(hydrate.replace(' ','')[:-3])

    def tosign(self, oxidation: bool=False):
        hydrate_s = 'H'+subscript(2, 1 if oxidation else None)+'O'+subscript('', -2 if oxidation else None)
        return self.salt.tosign(oxidation)+' . '+str(self.hydrate)+hydrate_s
    
    def toname(self):
        salt_acid,salt_element = self.salt.toname().split()
        return amount_table[self.hydrate]+'hydrát '+salt_acid+'u '+salt_element[:-1]+'ého'

# Used for interactive commands
COMPOUNDS: List[BaseCompound] = [Oxid,Sulfid,Acid,Salt,HydrogenSalt,SaltHydrate]
pstring = """
-- {entry}
typ sloučeniny: {typename}
název: {name}
vzoreček: {sign}
vzoreček s oxi.: {oxisign}
""".strip()

def fix_compound_sign(s: str) -> str:
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
    sign = fix_compound_sign(s.translate(NOR))
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
