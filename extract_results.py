import os
import sys

import numpy as np
import pandas as pd

from collections import OrderedDict

from functions import natural_keys

# ---------- IMPORT PL4-CSV FUNCTIONS ----------
from lib_readPL4_py3 import readPL4
from lib_readPL4_py3 import convertType
from lib_readPL4_py3 import getVarData


def extract_tower_current():
    pass


def extract_results(filename, results_path, lccs):

    # filename_str = os.path.basename(filename).replace('.atp', '')

    case_folder = f'{results_path}'

    # atp_solver = 'C:\\ATPSolvers\\atpmingw\\PyTP Solver.bat'

    case_folders = [folder for folder in os.listdir(case_folder)
                    if os.path.isdir(f'{case_folder}/{folder}')]

    if "LCCs" in case_folders:
        case_folders.remove("LCCs")

    case_folders = sorted(case_folders, key=natural_keys)

    case_folders_path = [f'{case_folder}/{val}' for val in case_folders]

    results_df = pd.DataFrame(index=case_folders, columns=case_folders)

    for case_idx, case_path in enumerate(case_folders_path):

        inner_folders = [f'{case_path}/{folder}'
                         for folder in os.listdir(case_path)
                         if os.path.isdir(f'{case_path}/{folder}')]

        # max_current = 0
        row_data = OrderedDict([(key, 0) for key in case_folders])
        for folder in inner_folders:
            case_name = os.path.split(os.path.normpath(folder))[-1]

            pl4file = f'{folder}/{case_name}.pl4'

            print(pl4file)

            dfHEAD, data, miscData = readPL4(pl4file)

            convertType(dfHEAD)

            header_1 = dfHEAD.iloc[:, 0].to_list()
            header_2 = dfHEAD.iloc[:, 1].to_list()
            header_3 = dfHEAD.iloc[:, 2].to_list()

            header_1.insert(0, 'time'.ljust(6))
            header_2.insert(0, ''.ljust(6))
            header_3.insert(0, ''.ljust(6))

            header = pd.MultiIndex.from_arrays([header_1, header_2, header_3])
            data = pd.DataFrame(data, columns=header)

            #------------- GET FAULT CURRENT -------------
            # EMPTY = ''.ljust(6)
            # filter_1 = data.iloc[:, data.columns.isin(['I-bran'], level=0)]
            # filter_2 = filter_1.iloc[:, ~filter_1.columns.isin([EMPTY], level=2)]
            #
            # # print(filter_2)
            #
            # Ifault = filter_1.to_numpy()
            #
            # max_val_If = np.max(np.abs(Ifault)) 

            #------------- GET EARTH CURRENTS -------------
            for key, values in lccs.items():
                EMPTY = ''.ljust(6)

                if values["earth_nodes"]:
                    earth_node = values["earth_nodes"][0].ljust(6)

                else:
                    earth_node = "EARTH_"

                filter_1 = data.iloc[:, data.columns.isin(['I-bran'], level=0)]
                filter_2 = filter_1.iloc[:, filter_1.columns.isin([earth_node], level=1)]
                filter_3 = filter_2.iloc[:, filter_2.columns.isin([EMPTY], level=2)]

                Iearth = filter_3.to_numpy()

                max_val_Ie = np.max(np.abs(Iearth)) 

                if row_data[key] < max_val_Ie:
                    row_data[key] = max_val_Ie

                # row_data.append(max_val_Ie)

                # results_df.loc[key] = max_val_Ie


            # if '1VN' in case_name:
            #     print(filter_2.columns)
            #     print(filter_2.shape)
            #
            #     break

            # print(filter_2)

            # print(max_val_Ie)

            # index_case = case_folders[case_idx]

            # phase = case_name.split('_')[-1]

            # results_df.loc[index_case, f'Earth Current - Phase {phase} [A]'] = max_val_Ie

            # break

        # break

        results_df[case_folders[case_idx]] = row_data.values()

        print(f'Running... {case_idx + 1}/{len(case_folders_path)}', end='\r')

    results_folder = os.path.split(os.path.normpath(results_path))[-1]
    excel_path = f'{results_path}/Currents Summary - {results_folder}.xlsx'
    results_df.to_excel(excel_path)

    print(results_df)
