import os
import sys

from tkinter import Tk
from tkinter import filedialog as fd

from functions import (
    check_user_settings, save_user_settings,
    check_folder_existence, shorten_path
)

from create_scenarios import (
    create_scenarios, get_lcc_nodes, filter_fault_nodes,
    create_statistical_scenarios
)

from run_scenarios import run_scenarios

from extract_results import extract_results

from update_base_case import (
    create_excel_file, update_resistance_values,
    update_base_case
)

#from alarp_functions import calculate_alarp

import time

root = Tk()
root.withdraw()

filename = 'C:/ATPDraw/ATP/P1378_A.atp'

results_path = 'C:/Users/Duiristt/Desktop/Results Python/ISES/TowerPy/Cases'
results_path = 'C:/ATPDraw/TowerPy/Cases'

results_path = os.getcwd() + '/Results'

cwd = os.getcwd()


def statistical_menu(filename):
    options = [
        "Create Scenarios",
        "Create Custom Scenarios (From Excel File)",
        "Run Scenarios",
        "Extract Results",
        "Create Electrical Parameters' Excel File",
        "Calculate ALARP",
        "Go Back"

    ]

    while True:
        os.system("cls")

        user_data = check_user_settings()

        atp_path = user_data['ATP_FILE_PATH']
        results_path = user_data['RESULTS_PATH']
        atp_solver = user_data['ATP_SOLVER_PATH']
        earthing_data_path = user_data['EARTHING_DATA_FILE_PATH']

        if not os.path.isdir(results_path):
            results_path = cwd + '/Results'

        print(f'Current .atp file path: "{shorten_path(atp_path)}"')
        print(f'Current results path: "{shorten_path(results_path)}"')
        print(f'Current ATP solver: "{shorten_path(atp_solver)}"')
        print(f'Earthing Data Excel: {shorten_path(earthing_data_path)}')

        print_menu(options)
        choice = get_choice(len(options))
        if choice == 1:
            print("CREATING STATISTICAL SCENARIOS...")
            with open(filename) as f:
                f_lines = f.readlines()

            filename_str = os.path.basename(filename).replace('.atp', '')
            create_statistical_scenarios(f_lines, filename_str, results_path)

        if choice == 2:
            filename_str = os.path.basename(filename).replace('.atp', '')

            with open(filename) as f:
                f_lines = f.readlines()

            lccs = get_lcc_nodes(f_lines)
            lccs = filter_fault_nodes(lccs, filename_str, results_path)

            # ------------- READ EXEL FILE WITH NEW RESISTANCES -------------
            filetypes = (
                    ('Excel Files', "*.xlsx"),

            )

            msg_title = "Select excel file with new resistances"
            excelname = fd.askopenfilename(
                                          title=msg_title,
                                          initialdir=os.getcwd(),
                                          filetypes=filetypes
                       )

            print('CREATING CUSTOM SCENARIOS...')

            temp_f_lines, results_path = update_base_case(
                                                        lccs, f_lines,
                                                        excelname, results_path
            )
            
            user_data['RESULTS_PATH'] = results_path

            save_user_settings(user_data)

            # ------------- CREATE NEW CASES -------------
            print('CREATING CUSTOM FAULT SCENARIOS...')
            create_statistical_scenarios(temp_f_lines, filename_str, results_path)
            print('DONE')

            time.sleep(1)

        if choice == 3:
            print('RUNNING FAULT SCENARIOS...')
            run_scenarios(filename, results_path, atp_solver)
            print('\nDONE')

            time.sleep(1)

        if choice == 4:
            print('EXTRACTING RESULTS...')

            filename_str = os.path.basename(filename).replace('.atp', '')

            with open(filename) as f:
                f_lines = f.readlines()

            lccs = get_lcc_nodes(f_lines)
            lccs = filter_fault_nodes(lccs, filename_str, results_path)

            extract_results(filename, results_path, lccs)
            print('DONE')

            time.sleep(1)

        if choice == 5:
            print('CREATING EXCEL BASE FILE')

            filename_str = os.path.basename(filename).replace('.atp', '')

            with open(filename) as f:
                f_lines = f.readlines()

            lccs = get_lcc_nodes(f_lines)
            lccs = filter_fault_nodes(lccs, filename_str, results_path)

            create_excel_file(lccs, f_lines, filename, results_path)
            print('DONE')

            time.sleep(1)

        if choice == 6:
            # READ EXCEL FILE WITH INPUT DATA
            filetypes = (
                    ('Excel Files', "*.xlsx"),

            )

            msg_title = "Select excel file with ALARP input data"
            excelname = fd.askopenfilename(
                                          title=msg_title,
                                          initialdir=os.getcwd(),
                                          filetypes=filetypes
                       )

            calculate_alarp(excelname) # type: ignore

        if choice == 7:
            break


def deterministic_menu(filename):
    options = [
        "Create Scenarios",
        "Create Custom Scenarios",
        "Create Custom Scenarios (Without Earth Wires)",
        "Run Scenarios",
        "Extract Results",
        "Create Earth Resistances' Excel File",
        "Go Back"
    ]

    while True:
        os.system("cls")
        user_data = check_user_settings()

        atp_path = user_data['ATP_FILE_PATH']
        results_path = user_data['RESULTS_PATH']
        atp_solver = user_data['ATP_SOLVER_PATH']
        earthing_data_path = user_data['EARTHING_DATA_FILE_PATH']

        if not os.path.isdir(results_path):
            results_path = cwd + '/Results'

        print(f'Current .atp file path: "{shorten_path(atp_path)}"')
        print(f'Current results path: "{shorten_path(results_path)}"')
        print(f'Current ATP solver: "{shorten_path(atp_solver)}"')
        print(f'Earthing Data Excel: {shorten_path(earthing_data_path)}')


        print_menu(options)
        choice = get_choice(len(options))

        if choice == 1:
            print('CREATING FAULT SCENARIOS...')

            with open(filename) as f:
                f_lines = f.readlines()

            filename_str = os.path.basename(filename).replace('.atp', '')

            create_scenarios(f_lines, filename_str, results_path)
            print('DONE')

            time.sleep(1)

        if choice in {2, 3}:
            filename_str = os.path.basename(filename).replace('.atp', '')

            print('UPDATING EARTH RESISTANCES...')

            with open(filename) as f:
                f_lines = f.readlines()

            lccs = get_lcc_nodes(f_lines)

            no_earth = True if choice == 3 else False
            lccs = filter_fault_nodes(
                                        lccs,
                                        filename_str,
                                        results_path,
                                        no_earth
            )

            # ------------- READ EXEL FILE WITH NEW RESISTANCES -------------
            filetypes = (
                    ('Excel Files', "*.xlsx"),

            )

            msg_title = "Select excel file with new resistances"
            excelname = fd.askopenfilename(
                                          title=msg_title,
                                          initialdir=os.getcwd(),
                                          filetypes=filetypes
                       )

            temp_f_lines = update_resistance_values(
                                                        lccs,
                                                        f_lines,
                                                        excelname
                                                    )

            results_path = check_folder_existence(results_path)

            user_data['RESULTS_PATH'] = results_path

            save_user_settings(user_data)

            # ------------- CREATE NEW CASES -------------
            print('CREATING CUSTOM FAULT SCENARIOS...')
            create_scenarios(temp_f_lines, filename_str, results_path)
            print('DONE')

            time.sleep(1)

        # if choice == 3:
        #     pass

        if choice == 4:
            print('RUNNING FAULT SCENARIOS...')
            run_scenarios(filename, results_path, atp_solver)
            print('\nDONE')

            time.sleep(1)

        if choice == 5:
            print('EXTRACTING RESULTS...')

            filename_str = os.path.basename(filename).replace('.atp', '') 

            with open(filename) as f:
                f_lines = f.readlines()

            lccs = get_lcc_nodes(f_lines)
            lccs = filter_fault_nodes(lccs, filename_str, results_path)

            extract_results(filename, results_path, lccs)
            print('DONE')

            time.sleep(1)

        elif choice == 6:
            print('CREATING EXCEL BASE FILE')

            filename_str = os.path.basename(filename).replace('.atp', '')

            with open(filename) as f:
                f_lines = f.readlines()

            lccs = get_lcc_nodes(f_lines)
            lccs = filter_fault_nodes(lccs, filename_str, results_path)

            create_excel_file(lccs, f_lines, filename, results_path)
            print('DONE')

            time.sleep(1)

        if choice == 7:
            break


def sub_menu_1(atp_filename):
    options = [
        "Deterministic Method",
        "Statistical Method",
        "Go Back"
    ]

    while True:
        os.system("cls")
        user_data = check_user_settings()

        atp_path = user_data['ATP_FILE_PATH']
        results_path = user_data['RESULTS_PATH']
        atp_solver = user_data['ATP_SOLVER_PATH']
        earthing_data_path = user_data['EARTHING_DATA_FILE_PATH']

        if not os.path.isdir(results_path):
            results_path = cwd + '/Results'

        print(f'Current .atp file path: "{shorten_path(atp_path)}"')
        print(f'Current results path: "{shorten_path(results_path)}"')
        print(f'Current ATP solver: "{shorten_path(atp_solver)}"')
        print(f'Earthing Data Excel: {shorten_path(earthing_data_path)}')

        print_menu(options)

        choice = get_choice(len(options))

        if choice == 1:
            deterministic_menu(atp_filename)

        if choice == 2:
            statistical_menu(atp_filename)

        if choice == 3:
            break


def main_menu():
    options = [
        "Load .atp File",
        "Choose Results Path",
        "Choose ATP Solver",
        "Choose Earthing Data Excel File",
        "Exit "
    ]

    while True:
        os.system("cls")

        user_data = check_user_settings()

        atp_path = user_data['ATP_FILE_PATH']
        results_path = user_data['RESULTS_PATH']
        atp_solver = user_data['ATP_SOLVER_PATH']
        earthing_data_path = user_data['EARTHING_DATA_FILE_PATH']

        if not os.path.isdir(results_path):
            results_path = shorten_path(cwd + '/Results')

        print(f'Current results path: "{shorten_path(results_path)}"')
        print(f'Current ATP solver: "{shorten_path(atp_solver)}"')
        print(f'Earthing Data Excel: {shorten_path(earthing_data_path)}')

        print_menu(options)
        choice = get_choice(len(options))

        if choice == 1:
            filetypes = (
                    ('ATP Files', "*.atp"),

            )

            filename = fd.askopenfilename(
                                          title='Select .atp Base File',
                                          initialdir=os.getcwd(),
                                          filetypes=filetypes
                       )

            if filename == '':
                print('Wrong selection. Select a proper .atp file')

            else:

                user_data['ATP_FILE_PATH'] = filename

                save_user_settings(user_data)

                sub_menu_1(filename)

        if choice == 2:
            custom_results_path = fd.askdirectory(
                title='Select Results Folder'
            )

            if custom_results_path == '':
                os.system('cls')

                print(f'Wrong selection. Results will be stored in {results_path}')

            else:
                os.system('cls')
                results_path = custom_results_path

                print(f'Results wil be stored in "{results_path}"')

            user_data['RESULTS_PATH'] = results_path

            save_user_settings(user_data)

        if choice == 3:
            filetypes = (
                    ('BAT Files', "*.bat"),

            )

            filename = fd.askopenfilename(
                                          title='Select .bat Solver File',
                                          initialdir=os.getcwd(),
                                          filetypes=filetypes
                       )

            if filename == '':
                print('Wrong selection. Select a proper .bat ATP solver')

            else:
                user_data['ATP_SOLVER_PATH'] = filename

                save_user_settings(user_data)

        if choice == 4:
            filetypes = (
                    ('Excel Files', "*.xlsx"),

            )

            filename = fd.askopenfilename(
                                          title='Select .xlsx Earthing Data File',
                                          initialdir=os.getcwd(),
                                          filetypes=filetypes
                       )

            if filename == '':
                print('Wrong selection. Select a proper .xlsx earthing data file')

            else:
                user_data['ATP_SOLVER_PATH'] = filename

                save_user_settings(user_data)

        if choice == 5:
            print("Exiting...")
            time.sleep(0.5)
            os.system('cls')

            break


def print_menu(options):
    print("\n")
    for i, option in enumerate(options):
        print(f'{i+1}. {option}')
    print()


def get_choice(num_options):
    while True:
        choice = input(f'Enter a choice (1-{num_options}): ')
        if not choice.isdigit():
            print('Invalid input. Please enter a number.')
            time.sleep(1)
            os.system("cls")
            break

        elif int(choice) < 1 or int(choice) > num_options:
            print(f'Invalid input. Please enter a number between 1 and {num_options}.')
            time.sleep(1)

            os.system("cls")
            break

        else:
            return int(choice)


def main():
    main_menu()


if __name__ == "__main__":
    main_menu()
