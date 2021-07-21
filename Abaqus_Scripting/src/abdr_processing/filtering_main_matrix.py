import numpy as np
from read_files import reading_inp_file

def make_rotation(table_to_abdr, table_rotation):
    translation = table_rotation[0]
    rotation = table_rotation[1]

    table_to_abdr[:, 1] = table_to_abdr[:, 1] + translation[0]
    table_to_abdr[:, 2] = table_to_abdr[:, 2] + translation[1]
    table_to_abdr[:, 3] = table_to_abdr[:, 3] + translation[2]

    r1 = rotation[0:3]
    r1 = rotation[3:6]
    print r1

    # r1 = np.array([-5.00000001268805, -4., 1.755])

    angle = np.deg2rad(rotation[6])

    if (angle >= 0):
        T = [[1, 0, 0],
             [0, np.cos(angle), -np.sin(angle)],
             [0, np.sin(angle), np.cos(angle)]]
    else:
        T = [[1, 0, 0],
             [0, np.cos(angle), np.sin(angle)],
             [0, -np.sin(angle), np.cos(angle)]]

    srodGlob = r1
    for i in range(len(table_to_abdr)):
        punkt0glob = table_to_abdr[i][1:]
        punkt0lok = np.array(srodGlob) * -1 + punkt0glob

        punkt1lok = np.matmul(np.array(T), np.transpose(punkt0lok))
        punkt1Glob = np.transpose(punkt1lok) + r1
        table_to_abdr[i][1:] = punkt1Glob

    return table_to_abdr




def calculate_dofs(ext_int, number_of_dofs):
    mtx_dof = []
    for node in ext_int:
        ndof_index = node * number_of_dofs
        for nodes in range(number_of_dofs):
            mtx_dof.append(ndof_index + nodes)
    return np.array(mtx_dof)



def nodes_location(file_name, number_of_dofs):
    table_to_abdr, table_rotation = reading_inp_file(file_name)

    table_to_abdr = np.array(table_to_abdr)
    table_to_abdr = make_rotation(table_to_abdr,table_rotation)

    table_n = table_to_abdr[:, 0]

    table_x = table_to_abdr[:, 1]
    table_y = table_to_abdr[:, 2]
    table_z = table_to_abdr[:, 3]

    maxx = max(table_x)
    maxy = max(table_y)
    maxz = max(table_z)

    minx = min(table_x)
    miny = min(table_y)
    minz = min(table_z)

    print(maxx, maxy, maxz)
    print(minx, miny, minz)

    diff_x = abs(maxx - minx)
    diff_y = abs(maxy - miny)
    diff_z = abs(maxz - minz)

    print (diff_x, diff_y, diff_z)

    table_x = table_x - minx - diff_x / 2
    table_y = table_y - miny - diff_y / 2

    external_from_file = []
    internal_from_file = []

    for index in range(len(table_to_abdr)):
        index_number = int(table_n[index] - 1)

        index_x = table_x[index]
        index_y = table_y[index]

        if abs(index_x - diff_x / 2) <= 1e-4 or abs(index_y - diff_y / 2) <= 1e-4 \
                or abs(index_x + diff_x / 2) <= 1e-4 or abs(index_y + diff_y / 2) <= 1e-4:
            external_from_file.append(index_number)
        else:
            internal_from_file.append(index_number)

    mtx_external_dof = calculate_dofs(external_from_file, number_of_dofs)
    mtx_internal_dof = calculate_dofs(internal_from_file,number_of_dofs)

    '''for node in range(len(table_to_abdr)):
        table_to_abdr[node][1] = table_to_abdr[node][1] - diff_x / 2  # X Axis
        table_to_abdr[node][2] = table_to_abdr[node][2] - abs(diff_y) / 2  # Y Axis

        table_to_abdr[node][3] = table_to_abdr[node][3] - abs(diff_z) / 2  # Z Axis
    '''
    return mtx_external_dof, mtx_internal_dof, np.array(external_from_file), table_to_abdr