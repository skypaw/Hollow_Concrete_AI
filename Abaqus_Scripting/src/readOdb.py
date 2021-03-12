from odbAccess import *


def read_odb():
    odb = openOdb("C:/temp/OczytaniePy.odb")

    steps = odb.steps["Step-1"]
    region = steps.historyRegions['Node PART-1-1.6']

    u2data = region.historyOutputs['U2']
    print(u2data)

    i = 0

    for i in u2data.data:
        print(i)

    return i
