from creating_model.build_model import Model
from log import log
from numpy import genfromtxt


def call_abaqus():
    cDS = Model()

    file_csv = genfromtxt(
        "D:\\dev\\Masters_Degree\\Abaqus_Scripting\\resources\\dataCircleToSubprocess.csv",
        delimiter=",",
    )
    old_dimensions = [0, 0, 0, 0, 0, 0, 0]

    with open(
        "D:\\dev\\Masters_Degree\\Abaqus_Scripting\\resources\\step.txt", "r"
    ) as file_read:
        data = []
        for line in file_read:
            data.append(float(line))

        step, batch = data

    for line in file_csv:
        if line[0] < step:
            continue
        if line[0] >= step + batch:
            break

        Model.set_dimensions(
            cDS, line[0], line[1], line[2], line[3], line[4], line[5], line[6]
        )
        Model.check_dimensions(cDS)

        new_dimensions = Model.get_dimensions(cDS)

        if old_dimensions[1:7] != new_dimensions[1:7]:
            log(new_dimensions)
            Model.create_database(cDS)

        old_dimensions = Model.get_dimensions(cDS)

    step += batch
    with open(
        "D:\\dev\\Masters_Degree\\Abaqus_Scripting\\resources\\step.txt", "w"
    ) as file_write:
        file_write.write(str(step) + "\n")
        file_write.write(str(batch))


if __name__ == "__main__":
    call_abaqus()
