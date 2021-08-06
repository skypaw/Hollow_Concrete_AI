from creating_model.build_model import Model
from log import log
from numpy import genfromtxt


def call_abaqus():
    cDS = Model()

    file = genfromtxt("C:\\temp\\dataToSubprocess.csv", delimiter=",")
    old_dimensions = [0, 0, 0, 0, 0, 0, 0]

    for line in file:
        Model.set_dimensions(cDS, line[0], line[1], line[2], line[3], line[4], line[5], line[6])
        Model.check_dimensions(cDS)

        new_dimensions = Model.get_dimensions(cDS)

        if old_dimensions[1:7] != new_dimensions[1:7]:
            log(new_dimensions)
            Model.create_database(cDS)

        old_dimensions = Model.get_dimensions(cDS)


call_abaqus()
