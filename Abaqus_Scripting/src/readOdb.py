from odbAccess import *


def read_odb():
    odb = openOdb("D:\dev\Masters_Degree\Abaqus_Scripting\HC-Slab-Job.odb")

    steps = odb.steps["Step-1"]
    region = steps.historyRegions['Node ASSEMBLY.1']

    u2data = region.historyOutputs['RF3']
    tuple_data = u2data.data[1]

    return tuple_data[1]
