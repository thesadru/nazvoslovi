from nazvoslovi import *

tests = """
# oxid
Li2O
P2O5
oxid manganistý
oxid boritý

# sulfid
sulfid sodný
sulfid arseničný
Na2S
Al2S3

# kyselina
HClO
H2SO4
kyselina křemičitá
kyselina sirová

# sůl
NaClO
Ca3(PO4)2
manganistan draselný
jodnan hořečnatý

# hydrogensůl
Al2(H2SiO4)3
PbHAsO4
hydrogenselenan zinečnatý
trihydrogenjodistan sodný

# hydrát soli
CuSO4.5H2O
dihydrát fosforečnanu vápenatého
"""
for test in tests.strip().split('\n'):
    if not test or test.startswith('#'):
        print(test)
    else:
        compound = recognize(test)
        if compound is None:
            print(f'Typ sloučeniny "{test}" nebyl rozpoznán.')
        elif isinstance(compound,NazvosloviException):
            print(compound)
        else:
            print(f'{compound.oxisign} {compound.name} <{compound.typename}>')
