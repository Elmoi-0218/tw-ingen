import os
from collections import defaultdict

from update_base_case import get_resistances_from_excel

def get_lcc_nodes(f_lines):
    lccs = defaultdict(lambda: defaultdict(list))
    lcc_count = 1
    fault_line_n = 0
    for idx_line, line in enumerate(f_lines):

        # if 'FAULT_LOCATION (DO NOT CHANGE THIS LINE)' in line:
        #     fault_line_n = idx_line + 1

        if '$INSERT' in line:
            _, lcc_path = line.split(',')
            lcc_path = lcc_path.strip()

            # lcc_id = os.path.basename(lcc_path).replace('.pch', '')[:-len(f'{lcc_count}')]

            lcc_id = f_lines[idx_line - 1][1:-1].strip()

            lccs[lcc_id]['pch_path'] = lcc_path

            with open(lcc_path) as fp:
                fp_lines = fp.readlines()

            flag_1 = False
            flag_2 = True
            line_n = 1
            for line_p in fp_lines:
                if '$UNITS' in line_p and flag_2 == True:
                    flag_1 = True

                if flag_1 and str(line_n) == line_p[len(f'{line_n}')]:

                    node_in = line_p[2:8]
                    node_out = line_p[8:14]

                    connection_id = line_p[1]

                    lccs[lcc_id]['nodes_in'].append(node_in)
                    lccs[lcc_id]['nodes_out'].append(node_out)
                    lccs[lcc_id]['connection_ids'].append(connection_id)
                        
                    line_n += 1

                    flag_2 = False

            lcc_count += 1

    return lccs


def create_fault_case(line_nodes, new_f_lines, earth_nodes=None, excel_file=None):
    for line_node, atp_path in zip(line_nodes['fault_nodes'], line_nodes['atp_paths']):
        earth_node = line_nodes['earth_nodes'][0]

        if excel_file:
            fault_r = line_nodes['tower_R']

        val_3 = True
        if earth_node == "".ljust(6):
            val_3 = False
            earth_node = "earth_"

        for idx_line, line in enumerate(new_f_lines):

            val_1 = line[:14].strip() == earth_node
            if earth_nodes is not None:
                val_1 = line[:14].strip() in earth_nodes

            val_2 = not 'SE' in new_f_lines[idx_line - 1]
            if val_1 and val_2 and val_3:
                # print([line[:-2]], [line[-1:]])
                new_f_lines[idx_line] = f'{line[:-2]}1{line[-1:]}'

            if 'FAULT_LOCATION (DO NOT CHANGE THIS LINE)' in line:
                fault_line_n = idx_line + 1

            if 'EARTH_RESISTANCE (DO NOT CHANGE THIS LINE)' in line:
                fault_resistance_n = idx_line + 1

                resistance_line = new_f_lines[fault_resistance_n]
                new_f_lines[fault_resistance_n] = f'{resistance_line[:26]}{fault_r}{resistance_line[32:]}'

                resistance_line = new_f_lines[fault_resistance_n]
                new_f_lines[fault_resistance_n] = f'{resistance_line[:-2]}1{resistance_line[-1:]}'

                no_earth = True

        # ------------- APPLY FAULT -------------
        fault_line = new_f_lines[fault_line_n]
        new_f_lines[fault_line_n] = f'{fault_line[:2]}{line_node}{earth_node}{fault_line[14:]}'

        if 'no_earth' in locals():
            # ASSIGN FAULT RESISTANCE
            ground_node = "".ljust(6)
            new_f_lines[fault_resistance_n] = f'{resistance_line[:2]}{earth_node}{ground_node}{resistance_line[14:]}'

        # ------------- SAVE FAULT CASE -------------
        with open(atp_path, 'w') as f:
            f.writelines(new_f_lines)


def create_fault_cases(lccs, f_lines, excel_file):
    for lcc_id in lccs.keys():
        line_nodes = lccs[lcc_id]
        # print(line_nodes)

        create_fault_case(line_nodes, f_lines.copy(), excel_file=excel_file)


def create_statistical_fault_cases(lccs, f_lines):
    i_key = "earth_nodes"
    earth_nodes = [values[i_key][0] for _, values in lccs.items() if i_key in values]
    for lcc_id in lccs.keys():
        line_nodes = lccs[lcc_id]

        create_fault_case(line_nodes, f_lines.copy(), earth_nodes=earth_nodes)


def filter_fault_nodes(lccs, filename_str, results_path, no_earth=False):
    # filename_str = os.path.basename(filename).replace('.atp', '')

    for lcc_id in lccs.keys():
        nodes_in = lccs[lcc_id]['nodes_in']
        nodes_out = lccs[lcc_id]['nodes_out']

        # new_f_lines = f_lines.copy()
        line_nodes = defaultdict(list)

        for node_in, node_out in zip(nodes_in, nodes_out):

            if 'A' in node_out:
                new_atp_path = f'{results_path}/{lcc_id}'
                new_atp_path = f'{new_atp_path}/{filename_str}_{lcc_id}_F{node_in.strip()[-1]}'
                new_atp_f_path = f'{new_atp_path}/{filename_str}_{lcc_id}_F{node_in.strip()[-1]}.atp'

                os.makedirs(new_atp_path, exist_ok=True)

                line_nodes['fault_nodes'].append(node_out)
                line_nodes['atp_paths'].append(new_atp_f_path)

                lccs[lcc_id]['fault_nodes'].append(node_out)
                lccs[lcc_id]['atp_paths'].append(new_atp_f_path)

            elif "B" in node_out or "C" in node_out:
                pass

            else:
                line_nodes['earth_nodes'].append(node_out)
                lccs[lcc_id]['earth_nodes'].append(node_out)

                # earth_nodes.append(node_out)

        if no_earth:
            node_out = ''.ljust(6)
            line_nodes['earth_nodes'].append(node_out)
            lccs[lcc_id]['earth_nodes'].append(node_out)

    return lccs


def create_scenarios(f_lines, filename_str, results_path, excel_file=None):
    lccs = get_lcc_nodes(f_lines)

    no_earth = True if excel_file else False

    lccs = filter_fault_nodes(lccs, filename_str, results_path, no_earth)

    if excel_file:
        lccs = get_resistances_from_excel(lccs, excel_file)

    create_fault_cases(lccs, f_lines, excel_file)

    return lccs


def create_statistical_scenarios(f_lines, filename_str, results_path):
    lccs = get_lcc_nodes(f_lines)

    lccs = filter_fault_nodes(lccs, filename_str, results_path)

    create_statistical_fault_cases(lccs, f_lines)

    return lccs
