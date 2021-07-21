from scipy.sparse import csr_matrix
from read_files import *


def calculate_index(mtx_indexes, number_of_ndofs):
    i_table = []
    j_table = []
    data_table = []

    for line in range(len(mtx_indexes)):
        a, b, c, d, e = mtx_indexes[line]

        i_index = (a - 1) * number_of_ndofs + b - 1
        j_index = (c - 1) * number_of_ndofs + d - 1

        i_table.append(int(round(i_index, 0)))
        j_table.append(int(round(j_index, 0)))
        data_table.append(e)

    return i_table, j_table, data_table


def creating_global_matrix(file_name, number_of_ndofs):
    mtx_data_from_file = read_mtx(file_name)

    i_mtx_index, j_mtx_index, data_mtx = calculate_index(mtx_data_from_file, number_of_ndofs)

    bottom_part_matrix = csr_matrix((data_mtx, (i_mtx_index, j_mtx_index)))
    top_part_matrix = csr_matrix.transpose(bottom_part_matrix)

    global_stiff_matrix = (bottom_part_matrix + top_part_matrix).toarray()

    length = global_stiff_matrix.shape[0]

    for i in range(length):
        for j in range(length):
            if i == j:
                global_stiff_matrix[i, j] = global_stiff_matrix[i, j] / 2

    return global_stiff_matrix
