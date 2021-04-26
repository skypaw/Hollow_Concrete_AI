from main import Main
import os
from log import log
import numpy as np

cDS = Main()

Main.modify_model(cDS, 0.2,0.25, 0.00226, 0.03, 0.08, 0.02, 0.03)
Main.read_dimensions(cDS)
Main.creating_model(cDS)
Main.read_odb(cDS)
Main.save_results(cDS)
Main.save_dimensions(cDS)


'''
for a in np.linspace(0.1, 0.18, 8):
    for h in np.linspace(0.15, 0.5, 10):
        for r in np.linspace(0.030, 0.061, 10):
            for l in np.linspace(0, 0.2, 2):
                Main.modify_model(cDS, a, h, 0.00226, 0.03, r, l, 0.03)
                Main.read_dimensions(cDS)
                Main.creating_model(cDS)
                Main.read_odb(cDS)
                Main.save_results(cDS)
                Main.save_dimensions(cDS)
'''