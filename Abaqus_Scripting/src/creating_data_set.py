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
    i = 0
    data = []
    for a in linspace(0.1, 0.18, 8):
        for h in linspace(0.15, 0.5, 8):
            for a_s in linspace(0.000023, 0.000112, 4):
                for a1 in linspace(0.02, 0.03, 2):
                    for r in linspace(0.030, 0.061, 10):
                        for l in linspace(0, 0.2, 4):
                            i += 1
                            data.append([i, a, h, a_s, a1, r, l])


    #lhs()
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
    #create_data_to_subprocess()
    # call_abdr()
    # delete_files()

    
    """
    test =  lhs(10, 6)
    for i in test:
        print i

        fig = plt.figure()
        fig.add_axes()
        ax = fig.gca()


        ax.scatter(i, range(0,10))
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        plt.title('{}'.format('Nodes before correction'))
        plt.show()"""