from odbAccess import *
from log import log


def read_odb(i):
    odb = openOdb("C:\\temp\\HC-Slab-Job-{}.odb".format(i))

    steps = odb.steps["Step-1"]
    region = steps.historyRegions['Node ASSEMBLY.1']

    u2data = region.historyOutputs['RF3']
    tuple_data = u2data.data[1]

    log(i)
    log(tuple_data)

    return tuple_data[1]
