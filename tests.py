from functions import check_file_existence, check_folder_existence, to_atp_format

from set_fault_resistance import to_atp_format

# tower_R = float(input('Enter resistance: '))

# new_resistance = '{:2.1E}'.format(tower_R)

# new_resistance = fmt.format('{:m}', tower_R)

# new_resistance = to_atp_format(tower_R)
#
# print(new_resistance)
# print(len(new_resistance))

with open("edeq.dat", "r") as file:
    lines = file.readlines()


for idx_line, line in enumerate(lines):
    if "BLANK CARD ENDING CONDUCTOR CARDS" in line:
        flag = idx_line + 1
        value = lines[flag][44:52]

        print([value])

        print([to_atp_format(float(value), n_chars=8)])
