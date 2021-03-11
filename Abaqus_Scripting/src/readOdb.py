from odbAccess import *
from createCae import *
from readConfig import *
from saveResults import *

SaveResults([[4,3,2,4]])


odb = openOdb("C:/temp/OczytaniePy.odb")
print(odb)

print(odb.steps)

print(odb.parts)

steps = odb.steps["Step-1"]
region = steps.historyRegions['Node PART-1-1.6']

print(region)

u2data = region.historyOutputs['U2']
print(u2data)

for i in u2data.data:
    print(i)
