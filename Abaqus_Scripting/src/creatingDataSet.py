from saveResults import save_to_csv
# from model import Model
from log import log
from numpy import linspace
import subprocess


def delete_files():
    pass


def call_abdr():
    pass


i = 0
data = []

for a in linspace(0.1, 0.18, 8):
    for h in linspace(0.15, 0.5, 10):
        for a_s in linspace(0.000023, 0.000112, 10):
            for a1 in linspace(0.02, 0.03, 10):
                for r in linspace(0.030, 0.061, 10):
                    for l in linspace(0, 0.2, 5):

                        i += 1
                        data.append([i, a, h, a_s, a1, r, l])

                        if i % 50 == 0:
                            save_to_csv(data, 'dataToSubprocess')
                            subprocess.call("abaqus cae noGUI=abaqusProcess.py", shell=True)

                            delete_files()

                            call_abdr()

                            data = []
