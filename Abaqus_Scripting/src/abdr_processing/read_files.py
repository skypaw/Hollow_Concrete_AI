import numpy as np
from warnings import warn


def append_items_to_table(line, table_to_return):
    table_line = []
    if not line.startswith("*"):
        for items in line.split(','):
            table_line.append(float(items))
    if not table_line == []:
        table_to_return.append(table_line)
    del table_line

    return table_to_return


def reading_inp_file(file_name):
    is_main_part = False
    is_node_line = False
    is_assembly_line = False

    table_nodes = []
    table_rotation_assembly = []

    with open("C:\\temp\\{}.inp".format(file_name)) as input_file:
        for line in input_file:

            # Bool statements to navigate in the file

            if line.startswith("*Part, name=Concrete-Cube") or line.startswith("*Part, name=Part-1"):
                is_main_part = True

            if line.startswith("*Instance, name=ConcreteCube-1") or line.startswith("*Instance, name=Part-1-1"):
                is_assembly_line = True

            if line.startswith("*Node"):
                is_node_line = True

            if line.startswith("*Element"):
                is_node_line = False
                is_main_part = False

            # Creating lists of elements

            if is_node_line and is_main_part:
                append_items_to_table(line, table_nodes)

            if is_assembly_line:
                append_items_to_table(line, table_rotation_assembly)

            if is_assembly_line and line.startswith("*End Instance"):
                return table_nodes, table_rotation_assembly

    warn("Failed to read file 'C:\\temp\\{}-C_STIF1.mtx".format(file_name))
    return None


def read_mtx(file_name):
    sparse_matrix_table = []

    with open('C:\\temp\\{}-C_STIF1.mtx'.format(file_name)) as input_file:
        for line in input_file:
            append_items_to_table(line, sparse_matrix_table)

        return np.array(sparse_matrix_table)


if __name__ == "__main__":
    print(reading_inp_file("Job-1"))
    print(read_mtx("Dwuteownik"))
