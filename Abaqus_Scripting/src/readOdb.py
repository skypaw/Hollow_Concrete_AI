from odbAccess import *

print("hello_wolrd")
# https://github.com/liangzulin/abaqus_pycharm

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
