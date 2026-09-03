import os
import sys

from functions import (
    natural_keys, check_user_settings
)

import subprocess as subp
# from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE

def run_dat_files(lccs, atp_solver_path):
    atp_path, results_path, atp_solver, user_data = check_user_settings()

    case_folder = f'{results_path}\\LCCs'

    current_dir = os.getcwd()
    for case_idx, (lcc, values) in enumerate(lccs.items()):
        dat_file_path = values["pch_new_path"].replace(".pch", ".dat")
        dat_file_dir = os.path.dirname(dat_file_path)
        dat_file_name = os.path.basename(dat_file_path)

        code = [atp_solver_path, dat_file_dir, dat_file_name, current_dir]

        atp_run_instance = subp.run(code, capture_output=True)
        
        output = atp_run_instance.stdout

        print(f'Running... {case_idx + 1}/{len(lccs)}', end="\r")

        sys.stdout.flush()

def run_scenarios(filename, results_path, atp_solver_path):
    filename_str = os.path.basename(filename).replace('.atp', '')

    case_folder = f'{results_path}'

    atp_solver = 'C:\\ATPSolvers\\atpmingw\\PyTP Solver.bat'
    atp_solver = atp_solver_path

    case_folders = [folder for folder in os.listdir(case_folder) 
                    if os.path.isdir(f'{case_folder}/{folder}')]

    case_folders = sorted(case_folders, key=natural_keys)

    case_folders_path = [f'{case_folder}/{val}' for val in case_folders]

    for case_idx, case_path in enumerate(case_folders_path):

        inner_folders = [f'{case_path}/{folder}' 
                         for folder in os.listdir(case_path) 
                         if os.path.isdir(f'{case_path}/{folder}')]

        for folder in inner_folders:

            # scenario_name = os.path.splitext(os.path.basename(file))[0]

            # print('Scenario ' + scenario_name + ' Started')

            case_name = os.path.split(os.path.normpath(folder))[-1]

            file = f'{folder}/{case_name}.atp'

            # print(file)

            currentDirectory = os.getcwd()
            atp_file_path = os.path.dirname(file).replace('/', '\\')
            atp_file_name = os.path.basename(file)

            code = [atp_solver, atp_file_path, atp_file_name, currentDirectory]

            # p = Popen(code, stdout=PIPE, stdin=PIPE, shell=False, creationflags=CREATE_NEW_CONSOLE)
            # p = Popen(code, stdout=PIPE, stdin=PIPE, shell=False)
            # output, errors = p.communicate()
            # print(output)

            # print(output)

            # p.wait()

            atp_run_instance = subp.run(code, capture_output=True)
            
            output = atp_run_instance.stdout

            # print(output)
            

            # sys.exit()



        # break

        print(f'Running... {case_idx + 1}/{len(case_folders_path)}', end="\r")

        sys.stdout.flush()

    # for lcc_id, parameters in lccs.items():
