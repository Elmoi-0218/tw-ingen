import os

import pandas as pd

from collections import defaultdict

from functions import (
    check_file_existence, check_folder_existence,
    check_user_settings
)

from run_scenarios import run_dat_files

from set_fault_resistance import to_atp_format

from pathlib import Path

from shutil import copytree, copyfile


def update_pch_nodes(lccs):

    for lcc, values in lccs.items():
        pch_path = values["pch_new_path"]

        with open(pch_path, "r") as f:
            lines = f.readlines()

        nodes_in = values["nodes_in"]
        nodes_out = values["nodes_out"]
        connection_ids = values["connection_ids"]

        old_nodes = [
            f"{c_id}IN_{c_id.zfill(3)}OUT{c_id.zfill(3)}"
            for c_id in connection_ids    
        ]
        new_nodes = [
            f"{c_id}{n_in}{n_out}"
            for n_in, n_out, c_id in zip(nodes_in, nodes_out, connection_ids)
        ]

        for idx_line, line in enumerate(lines):

            flag = [i for i, item in enumerate(old_nodes) if item in line]

            if flag:
                old_node = old_nodes[flag[0]]
                new_node = new_nodes[flag[0]]

                lines[idx_line] = lines[idx_line].replace(old_node, new_node)

        with open(pch_path, "w") as f:
            f.writelines(lines)


def update_dat_file(f_lines, resistivity_val, span_len_val):
    for idx_line, line in enumerate(f_lines):
        if "BLANK CARD ENDING CONDUCTOR CARDS" in line:
            flag = idx_line + 1

            resistivity = to_atp_format(resistivity_val, n_chars=8)
            span_len = to_atp_format(span_len_val, n_chars=8)

            f_lines[flag] = f"{resistivity}{f_lines[flag][8:]}"
            f_lines[flag] = f"{f_lines[flag][:44]}{span_len}{f_lines[flag][52:]}"
            
            break

    return f_lines


def create_dat_files(lccs, results_path, excel_dicts):
    # old_pch_paths = [lccs[key]["pch_path"] for key in lccs.keys()]
    # new_pch_paths = [lccs[key]["pch_new_path"] for key in lccs.keys()]
    pch_files_folder = f"{results_path}\\LCCs"

    os.makedirs(pch_files_folder, exist_ok=True)

    # GET FIRST KEY VALUE
    _, first_key_values = next(iter(lccs.items()))

    # COPY ORIGINAL .DAT FILE TEMPORARY 
    dat_file_path = first_key_values["pch_path"]
    dat_file_path = "_".join(dat_file_path.split("_")[:-1]) + ".dat"

    dat_file_dir = os.path.dirname(dat_file_path)

    with open(dat_file_path, "r") as dat_file:
        dat_file_lines = dat_file.readlines()

    for lcc, values in lccs.items():
        new_dat_file_path = values["pch_new_path"].replace(".pch", ".dat")

        resistivity = excel_dicts[1][lcc]
        span_len = excel_dicts[2][lcc]

        f_lines = update_dat_file(
            dat_file_lines.copy(), resistivity, span_len
        )

        with open(new_dat_file_path, "w") as file:
            file.writelines(f_lines)
        

def update_pch_paths(lccs, f_lines, results_path):
    pch_paths = [lccs[key]["pch_path"] for key in lccs.keys()]
    for idx_line, line in enumerate(f_lines):
        if '$INSERT' in line:
            pch_path = [val for val in pch_paths if val in line]

            # line = line.replace("\\", "\\\\")

            lcc_id = f_lines[idx_line - 1][1:-1].strip()
            
            if len(pch_path) == 1:
                old_pch_path = pch_path[0]
                filename = os.path.basename(pch_path[0])

                new_pch_path = f"{results_path}/LCCs/{filename}"
                new_pch_path = os.path.normpath(new_pch_path)

                f_lines[idx_line] = line.replace(old_pch_path, new_pch_path)
                lccs[lcc_id]["pch_new_path"] = new_pch_path

    return lccs, f_lines


def update_resistivity(lccs, f_lines):
    for idx_line, line in enumerate(f_lines):
        if "BLANK CARD ENDING CONDUCTOR CARDS" in line:
            flag = idx_line + 1
            # f_lines[flag] = f_lines[flag][]


def get_resistivities(lccs):
    # resistivities_dic = defaultdict(dict)
    for lcc, values in lccs.items():
        pch_path = values["pch_path"]

        with open(pch_path, "r") as file:
            pch_lines = file.readlines()

        tower_resistivity, span_len = get_resistivity_value(pch_lines)
        lccs[lcc]["tower_resistivity"] = tower_resistivity
        lccs[lcc]["span_len"] = span_len

    # lccs.update(resistivities_dic)

    return lccs


def get_resistivity_value(f_lines):
    for idx_line, line in enumerate(f_lines):
        if "BLANK CARD ENDING CONDUCTOR CARDS"  in line:
            flag = idx_line + 1

            resistivity = float(f_lines[flag][2:10])
            span_len = float(f_lines[flag][46:54])

            break

    return resistivity, span_len
    

def get_resistances_values(lccs, f_lines):
    for idx_line, line in enumerate(f_lines):
        for lcc_id in lccs.keys():
            earth_node = lccs[lcc_id]['earth_nodes'][0]
            val_1 = line[:14] == f'  {earth_node}      '
            val_2 = not 'SE' in f_lines[idx_line - 1]
            if val_1 and val_2:
                # new_f_lines[idx_line] = f'{line[:-2]}1{line[-1:]}' 
                earth_r = f_lines[idx_line][26:32] 
                lccs[lcc_id]['tower_R'] = float(earth_r)

    return lccs


def update_base_case(lccs, f_lines, excelname, results_path):
    results_path = check_folder_existence(results_path)

    new_f_lines = update_resistance_values(lccs, f_lines, excelname)
    lccs, new_f_lines = update_pch_paths(lccs, new_f_lines, results_path)

    lccs = get_resistivities(lccs)

    update_resistivity_values(lccs, excelname, results_path)

    return new_f_lines, results_path

def update_resistivity_values(lccs, excelname, results_path):
    atp_path, results_path, atp_solver, user_data = check_user_settings()
    results_path = check_folder_existence(results_path)

    # READ EXCEL FILE
    excel_df = pd.read_excel(excelname, index_col=0)
    # resistivities_dict = list(excel_df.to_dict().values())[1]

    excel_dicts = list(excel_df.to_dict().values())
    
    create_dat_files(lccs, results_path, excel_dicts)

    run_dat_files(lccs, atp_solver)

    update_pch_nodes(lccs)

def get_resistances_from_excel(lccs, excelname):
    #------------- READ EXCEL FILE -------------
    excel_df = pd.read_excel(excelname, index_col=0)

    resistances_dict = list(excel_df.to_dict().values())[0]

    for lcc_id in lccs.keys():
        tower_R = resistances_dict[lcc_id]
        new_resistance = to_atp_format(tower_R)
        lccs[lcc_id]["tower_R"] = new_resistance

    return lccs

def update_resistance_values(lccs, f_lines, excelname, resistances_dict=None):
    if not resistances_dict:
        #------------- READ EXCEL FILE -------------
        excel_df = pd.read_excel(excelname, index_col=0)

        resistances_dict = list(excel_df.to_dict().values())[0]

    new_f_lines = f_lines.copy()
    for idx_line, line in enumerate(f_lines):
        for lcc_id in lccs.keys():
            earth_node = lccs[lcc_id]['earth_nodes'][0]

            val_1 = line[:14] == f'  {earth_node}      '
            val_2 = not 'SE' in f_lines[idx_line - 1]
            if val_1 and val_2:
                tower_R = resistances_dict[lcc_id]
                new_resistance = to_atp_format(tower_R)
                new_f_lines[idx_line] = f'{line[:26]}{new_resistance}{line[32:]}'

    return new_f_lines


def create_temp_atp_file(filename, results_path):

    results_path = f'{results_path}/{filename_str}'

    new_results_path = check_folder_existence(results_path)
    
    filename_str = os.path.basename(filename).replace('.atp', '')

    #------------- READ ORIGINAL ATP FILE -------------
    with open(filename) as atp_f:
        f_lines = f.readlines()


    #------------- SAVE FAULT CASE -------------
    with open(atp_path, 'w') as f:
        f.writelines(new_f_lines)

def create_excel_file(lccs, f_lines, filename, results_path):
    lccs = get_resistances_values(lccs, f_lines)

    lccs = get_resistivities(lccs)

    parameters = [
        (
            lccs[key]["tower_R"], lccs[key]["tower_resistivity"],
            lccs[key]["span_len"]
         ) 
        for key in lccs.keys()
    ]

    cols = ['Tower Resistance', "Tower Resistivity", "Span Length"]
    excel_d = pd.DataFrame(parameters, columns=cols, index=lccs.keys())

    filename_str = os.path.basename(filename).replace('.atp', '')

    excel_path = f'{results_path}/Electrical Parameters - {filename_str}.xlsx'

    excel_path = check_file_existence(excel_path)

    excel_d.to_excel(excel_path)

def copy_current_result_cases(filename, results_path):
    ignore_func = lambda d, files: [f for f in files if (Path(d) / Path(f)).is_file() and not f.endswith('.atp')] 

    filename_str = os.path.basename(filename).replace('.atp', '')

    results_path = f'{results_path}/{filename_str}'

    new_results_path = check_folder_existence(results_path)

    copytree(results_path, new_results_path, ignore=ignore_func)


    return new_results_path


def update_case(lccs, f_lines, filename):
    for line_node, atp_path in zip(line_nodes['fault_nodes'], line_nodes['atp_paths']):
        earth_node = line_nodes['earth_nodes'][0]

        for idx_line, line in enumerate(new_f_lines):
            val_1 = line[:14] == f'  {earth_node}      '
            val_2 = not 'SE' in new_f_lines[idx_line - 1]
            if val_1 and val_2:
                # print([line[:-2]], [line[-1:]])
                new_f_lines[idx_line] = f'{line[:-2]}1{line[-1:]}' 

            if 'FAULT_LOCATION (DO NOT CHANGE THIS LINE)' in line:
                fault_line_n = idx_line + 1

        #------------- APPLY FAULT -------------
        fault_line = new_f_lines[fault_line_n]
        new_f_lines[fault_line_n] = f'{fault_line[:2]}{line_node}{earth_node}{fault_line[14:]}'

        #------------- SAVE FAULT CASE -------------
        with open(atp_path, 'w') as f:
            f.writelines(new_f_lines)
