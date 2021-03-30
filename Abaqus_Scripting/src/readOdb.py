from odbAccess import *
from saveResults import save_to_csv


def read_odb():
    odb = openOdb("D:\dev\Masters_Degree\Abaqus_Scripting\HC-Slab-Job.odb")

    steps = odb.steps["Step-1"]
    region = steps.historyRegions['Node ASSEMBLY.1']

    u2data = region.historyOutputs['RF3']

    save_to_csv(u2data.data)


read_odb()
