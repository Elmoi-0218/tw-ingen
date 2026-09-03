import re
import os
import sys
import pickle

import json

from collections import defaultdict


def shorten_path(path):
    path = os.path.normpath(path)
    components = path.split(os.sep)

    # Remove empty string at the beginning or end of components
    if components[0] == '':
        components = components[1:]
    if components[-1] == '':
        components = components[:-1]

    shortened_components = []
    for i, component in enumerate(components):
        if i == 0:
            shortened_components.append(component)
        elif i == len(components) - 1:
            if os.path.isdir(component):
                shortened_components.append(component)
            else:
                dirname, basename = os.path.split(component)
                name, ext = os.path.splitext(basename)
                shortened_components.append(os.path.join(os.path.basename(dirname), name + ext))
        elif i == len(components) - 2:
            shortened_components.append(component)
        else:
            shortened_components.append(component[0])

    return os.sep.join(shortened_components)


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def save_value(val, file_name='user_settings.pkl'):

    open_file = open(resolve_path(file_name), "wb")
    pickle.dump(val, open_file)
    open_file.close()


def get_value(file_name='user_settings.pkl'):

    file_name = file_name
    open_file = open(resolve_path(file_name), "rb")
    loaded_data = pickle.load(open_file)
    open_file.close()

    return loaded_data


def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


def check_user_settings(filename='user_settings.json'):

    try:
        with open(filename, 'r') as read_file:
            user_data = json.load(read_file)
            user_data = defaultdict(str, user_data)

    except FileNotFoundError:
        user_data = defaultdict(str)
        save_user_settings(user_data)

    # atp_file = user_data['ATP_FILE_PATH']
    # results_path = user_data['RESULTS_PATH']
    # atp_solver = user_data['ATP_SOLVER_PATH']
    #
    # return atp_file, results_path, atp_solver, user_data
    return user_data


def save_user_settings(data, filename='user_settings.json'):
    with open(filename, "w") as write_file:
        json.dump(data, write_file)


def to_atp_format(scnum, roundafter, width):
    formstr = "".join(("{:.", str(roundafter), "e}"))
    scnum = formstr.format(scnum)
    base, exponent = float(scnum[:roundafter+2]), int(scnum[-3:])

    final_val = str(base) + 'E' + str(exponent)

    return final_val.center(width)


def check_file_existence(filepath):

    path_norm = os.path.normpath(filepath)

    f_path, _ = os.path.split(path_norm)

    f_name, f_ext = os.path.splitext(os.path.basename(path_norm))

    try:
        idx = int(f_name.split("_")[-1])
        base_name = "_".join(f_name.split("_")[:-1])

    except ValueError:
        idx = 1
        base_name = f_name

    val = True
    while val:

        if os.path.isfile(path_norm):
            new_filename = f'{base_name}_{idx}'

            path_norm = f'{f_path}/{new_filename}{f_ext}'

            idx += 1

        else:
            val = False

            return path_norm

def check_folder_existence(folderpath):

    path_norm = os.path.normpath(folderpath)

    folder_split = path_norm.split(os.sep)
    folder_name = folder_split[-1]

    try:
        idx = int(folder_name.split("_")[-1])
        base_name = "_".join(folder_name.split("_")[:-1])

    except ValueError:
        idx = 1
        base_name = folder_name

    val = True
    while val:

        if os.path.isdir(path_norm):
            new_foldername = f'{base_name}_{idx}'

            path_norm = f'{"/".join(folder_split[:-1])}/{new_foldername}'

            idx += 1

        else:
            val = False

            return path_norm

# def check_file_dialog(file_ext, file_type):
