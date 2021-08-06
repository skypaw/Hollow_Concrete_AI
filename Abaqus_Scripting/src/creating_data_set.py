from abdr_processing.save_results import save_to_csv
from abdr_processing.create_abdr import CreateAbdr
from numpy import linspace, genfromtxt
import subprocess
import os
from pyDOE2 import lhs

import matplotlib.pyplot as plt


def delete_files(step, batch_size):
    txt = genfromtxt("C:\\temp\\dataToSubprocess.csv", delimiter=",")
    for line in txt:
        if not int(line[0]) == step - batch_size:
            continue
        elif int(line[0]) >= step - batch_size:
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
                os.remove("C:\\temp\\Job-{}-C_X1.sim".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C_X1.sim".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.log".format(int(line[0])))
                os.remove("C:\\temp\\Job-{}-C.sim".format(int(line[0])))

            except:
                print "Error with removing"
        elif int(line[0]) == step:
            break


def call_abdr():
    txt = genfromtxt("C:\\temp\\dataToSubprocess.csv", delimiter=",")
    savedata = []
    for model_data in txt:
        if os.path.exists("C:\\temp\\Job-{}-C.inp".format(int(model_data[0]))):
            try:
                c = CreateAbdr("Job-{}".format(int(model_data[0])), model_data[1], 3)
                savedata.extend([model_data[1:], CreateAbdr.get_results(c)])
                save_to_csv(savedata, "C:\\temp\\batch_results")
            except:
                print ("Problem with Job-{}".format(int(model_data[0])))

    save_to_csv(savedata, "C:\\temp\\batch_results")


def create_data_to_subprocess():
    data = []
    i = 0

    lhs_list = lhs(6, 12000, criterion='center')

    a_start = 0.1
    a_end = 0.18
    a_interval = a_end - a_start

    h_start = 0.15
    h_end = 0.5
    h_interval = h_end - h_start

    a_s_start = 0.000023
    a_s_end = 0.000112
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
        i += 1

        a = dimensions[0] * a_interval + a_start
        h = dimensions[1] * h_interval + h_start
        a_s = dimensions[2] * a_s_interval + a_s_start
        a1 = dimensions[3] * a1_interval + a1_start
        r = dimensions[4] * r_interval + r_start
        l = dimensions[5] * l_interval + l_start
        data.append([i, a, h, a_s, a1, r, l])

    save_to_csv(data, '..\\resources\\dataToSubprocess')


def calculate(batch_size):
    i = 1
    try:
        subprocess.call("abaqus cae noGUI=abaqus_subprocess.py", shell=True)
        if i % batch_size == 0:
            with open("..\\resources\\temp_step") as step:
                step.write(i)

            call_abdr()
            delete_files(i, 100)



    except:
        print "test"
        with open("..\\resources\\temp_step") as step:
            step.write(i)

    """if i % 1500 == 0:
        save_to_csv(data, 'C:\\temp\\dataToSubprocess')
        

        call_abdr()

        # delete_files()
        data = []
    """


if __name__ == "__main__":
    # calculate()
    create_data_to_subprocess()
    # call_abdr()
    # delete_files()
