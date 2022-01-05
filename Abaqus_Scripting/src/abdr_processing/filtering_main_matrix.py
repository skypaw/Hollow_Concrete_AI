import numpy as np
from read_files import reading_inp_file
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def make_translation(to_translate, direction, translation):
    to_translate[:, direction] = to_translate[:, direction] + translation
    return to_translate[:, direction]


def make_rotation(table_to_abdr, table_rotation):
    translation = table_rotation[0]
    rotation = table_rotation[1]

    # print translation, rotation, 'ROTATION TRANSLA'

    table_x = table_to_abdr[:, 1]
    table_y = table_to_abdr[:, 2]
    table_z = table_to_abdr[:, 3]

    """fig = plt.figure()
    fig.add_axes()
    ax = fig.gca(projection='3d')

    ax.scatter(table_x, table_y, table_z)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.title('{}'.format('Nodes before correction'))
    plt.show()"""

    table_x = make_translation(table_to_abdr, 1, translation[0])
    table_y = make_translation(table_to_abdr, 2, translation[1])
    table_z = make_translation(table_to_abdr, 3, translation[2])

    """fig = plt.figure()
    fig.add_axes()
    ax = fig.gca(projection='3d')
    ax.scatter(table_x, table_y, table_z)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.title('{}'.format('Nodes after translation'))
    plt.show()"""

    r1 = rotation[3:6]
    # print r1
    angle = np.deg2rad(rotation[6])
    # print angle*r1[0]

    if angle * r1[0] >= 0:
        T = [
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)],
        ]
    else:
        T = [
            [1, 0, 0],
            [0, np.cos(angle), np.sin(angle)],
            [0, -np.sin(angle), np.cos(angle)],
        ]

    srodGlob = r1
    for i in range(len(table_to_abdr)):
        punkt0glob = table_to_abdr[i][1:]
        punkt0lok = np.array(srodGlob) * -1 + punkt0glob

        punkt1lok = np.matmul(np.array(T), np.transpose(punkt0lok))
        punkt1Glob = np.transpose(punkt1lok) + r1
        table_to_abdr[i][1:] = punkt1Glob

    """fig = plt.figure()
    fig.add_axes()
    ax = fig.gca(projection='3d')
    ax.scatter(table_x, table_y, table_z)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.title('{}'.format('Nodes after rotation'))
    plt.show()"""

    maxx = max(table_x)
    maxy = max(table_y)
    maxz = max(table_z)
    minz = min(table_z)

    # todo: check if it makes any differnet at all to move it to the center

    table_x = make_translation(table_to_abdr, 1, -maxx / 2)
    table_y = make_translation(table_to_abdr, 2, -maxy / 2)
    table_z = make_translation(table_to_abdr, 3, -(abs(maxz) + abs(minz)) / 2)

    """fig = plt.figure()
    fig.add_axes()
    ax = fig.gca(projection='3d')
    ax.scatter(table_to_abdr[:, 1], table_to_abdr[:, 2], table_to_abdr[:, 3])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.title('{}'.format('Nodes translation to center'))
    plt.show()"""

    # print table_to_abdr

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
    table_to_abdr = make_rotation(table_to_abdr, table_rotation)

    table_n = table_to_abdr[:, 0]

    table_x = table_to_abdr[:, 1]
    table_y = table_to_abdr[:, 2]

    maxx = max(table_x)
    maxy = max(table_y)

    minx = min(table_x)
    miny = min(table_y)

    """print(maxx, maxy, maxz), "Max values"
    print(minx, miny, minz), "min val"""

    diff_x = abs(maxx - minx)
    diff_y = abs(maxy - miny)

    table_x = table_x - minx - diff_x / 2
    table_y = table_y - miny - diff_y / 2

    external_from_file = []
    internal_from_file = []

    for index in range(len(table_to_abdr)):
        index_number = int(table_n[index] - 1)

        index_x = table_x[index]
        index_y = table_y[index]

        if (
            abs(index_x - diff_x / 2) <= 1e-4
            or abs(index_y - diff_y / 2) <= 1e-4
            or abs(index_x + diff_x / 2) <= 1e-4
            or abs(index_y + diff_y / 2) <= 1e-4
        ):
            external_from_file.append(index_number)
        else:
            internal_from_file.append(index_number)

    mtx_external_dof = calculate_dofs(external_from_file, number_of_dofs)
    mtx_internal_dof = calculate_dofs(internal_from_file, number_of_dofs)

    return (
        mtx_external_dof,
        mtx_internal_dof,
        np.array(external_from_file),
        table_to_abdr,
    )
