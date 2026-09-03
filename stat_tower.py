import os
import sys

from tkinter import Tk
from tkinter import filedialog as fd

from create_scenarios import create_scenarios, get_lcc_nodes, filter_fault_nodes

from functions import check_user_settings, save_user_settings

import time

root = Tk()
root.withdraw()

filetypes = (
        ('ATP Files', "*.atp"),

)

filename = fd.askopenfilename(
                              title='Select .atp Base File',
                              initialdir=os.getcwd(),
                              filetypes=filetypes
           )

results_path = r"C:\Users\Duiristt\Desktop\Results Python\TowerPy"

with open(filename) as f:
    filename_str = os.path.basename(filename).replace('.atp', '')
    f_lines = f.readlines()

    lccs = get_lcc_nodes(f_lines)
    lccs = filter_fault_nodes(lccs, filename_str, results_path)


print(lccs)
