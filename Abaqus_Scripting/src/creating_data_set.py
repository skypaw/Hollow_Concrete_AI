from abdr_processing.save_results import save_to_csv
from abdr_processing.create_abdr import CreateAbdr
from numpy import genfromtxt
import subprocess
import os
from pyDOE2 import lhs

import matplotlib.pyplot as plt


def delete_files(step, batch_size):
    txt = genfromtxt("..\\resources\\dataToSubprocess.csv", delimiter=",")
    for line in txt:
        if float(line[0]) < step:
            continue
        if float(line[0]) > step + batch_size:
            break

        if float(line[0]) < step + batch_size:
            try:
                os.remove("C:\\temp\\Job-{}.inp".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.inp".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.com".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C_STIF1.mtx".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.sta".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.prt".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.odb".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.msg".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.dat".format(int(line[0])))

            except:
                print ("Error with removing Job-{}".format(int(line[0])))


def call_abdr(step, batch_size):
    txt = genfromtxt("..\\resources\\dataToSubprocess.csv", delimiter=",")

    savedata_mian = []
    create_abdr = CreateAbdr()

    local_step = 1
    for model_data in txt:
        if model_data[0] < step:
            local_step = step
            continue
        if model_data[0] >= step + batch_size:
            break

        if os.path.exists("C:\\temp\\Job-{}-C.inp".format(int(local_step))):

            try:
                savedata = []

                create_abdr.set_data("Job-{}".format(int(local_step)), model_data[1], 3)
                create_abdr.calculate_abdr()

                for datadata in model_data:
                    savedata.append(datadata)

                data2 = CreateAbdr.get_results(create_abdr)
                for datadatadatar in data2:
                    savedata.append(datadatadatar)

                # save_to_csv(savedata, "C:\\temp\\batch_results{}".format(step))
                savedata_mian.append(savedata)
                local_step += 1


            except:
                print("Problem with Job-{}".format(int(step)))

    save_to_csv(savedata_mian, "C:\\temp\\batch_results{}".format(step))


def create_data_to_subprocess():
    data = []
    i = 0

    lhs_list = lhs(6, 35000, criterion='center')

    a_start = 0.1
    a_end = 0.18
    a_interval = a_end - a_start

    h_start = 0.15
    h_end = 0.5
    h_interval = h_end - h_start

    a_s_start = 0.000001
    a_s_end = 0.000644
    a_s_interval = a_s_end - a_s_start

    a1_start = 0.02
    a1_end = 0.03
    a1_interval = a1_end - a1_start

    r_start = 0.03
    r_end = 0.061
    r_interval = r_end - r_start

    l_start = 0
    l_end = 0.2
    l_interval = l_end - l_start

    for dimensions in lhs_list:

        a = dimensions[0] * a_interval + a_start
        h = dimensions[1] * h_interval + h_start
        a_s = dimensions[2] * a_s_interval + a_s_start
        a1 = dimensions[3] * a1_interval + a1_start
        r = dimensions[4] * r_interval + r_start
        l = dimensions[5] * l_interval + l_start

        if 2 * r + 0.02 >= a:
            continue

        if 2 * a1 + r * 2 + l + 0.02 >= h - 2 * a1:
            continue

        if 2 * a1 + 0.01 >= a:
            continue

        if l < 0.005:
            continue

        i += 1

        data.append([i, a, h, a_s, a1, r, l])

    save_to_csv(data, '..\\resources\\dataToSubprocess')


def calculate():
    # todo:move batch size -> batch size for now in step.txt

    file_csv = genfromtxt("D:\\dev\\Masters_Degree\\Abaqus_Scripting\\resources\\dataCircleToSubprocess.csv", delimiter=",")

    with open("D:\\dev\\Masters_Degree\\Abaqus_Scripting\\resources\\step.txt", "r") as file:
        data = []
        for line in file:
            data.append(float(line))

        step, batch = data

        while step in file_csv[:, 0]:
            try:
                subprocess.call("abaqus cae noGUI=abaqus_subprocess.py", shell=True)

                call_abdr(step, data[1])
                delete_files(step, data[1])

                step += batch

            except:
                print("problem with step {}".format(step))

            finally:
                print("corrupted file in step {}".format(step))


if __name__ == "__main__":
    calculate()
    # create_data_to_subprocess()
    # call_abdr()
    # delete_files()
