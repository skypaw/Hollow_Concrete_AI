from main import Main
import os
from log import log
import numpy as np

r = 30
h = 150

cDS = Main()

'''Main.modify_model(cDS, 0.100, 0.150, 0.00226, 0.03, 0.03, 0, 0.03)
Main.read_dimensions(cDS)
Main.creating_model(cDS)
Main.read_odb(cDS)
'''

for a in np.linspace(0.100, 0.181, 10):
    for h in np.linspace(0.150, 0.501, 10):
        for r in np.linspace(0.030, 0.061, 10):
            for l in np.linspace(0, 0.39, 5):
                Main.modify_model(cDS, a, h, 0.00226, 0.03, r, l, 0.03)
                Main.read_dimensions(cDS)
                Main.creating_model(cDS)
                Main.read_odb(cDS)

                Main.save_dimensions(cDS)
                Main.save_results(cDS)

Main.save_dimensions(cDS)
Main.save_results(cDS)
