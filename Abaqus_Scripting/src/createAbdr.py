from scipy.sparse import csr_matrix
import matplotlib.pylab as plt
import numpy as np
from find_external import *
from warnings import warn
import matplotlib.pyplot as plt
import pylab
from mpl_toolkits.mplot3d import Axes3D


class CreateAbdr:
    __file_name = None
    __area = None
    __ndof = None
    __matrix_k = None

    def __init__(self, file_name, a, ndof):
        self.__file_name = file_name
        self.__calculate_area(a)
        self.__ndof = int(ndof)

        dof_external, dof_internal, nodes_external_inp, nodes_correction = self.nodes_location()
        self.__matrix_k = self.creating_global_matrix()
        print self.__matrix_k.shape

        matrix_k_ee = self.filtering_matrix(dof_external, dof_external)
        matrix_k_ii = self.filtering_matrix(dof_internal, dof_internal)
        matrix_k_ei = self.filtering_matrix(dof_external, dof_internal)
        matrix_k_ie = self.filtering_matrix(dof_internal, dof_external)

        print(matrix_k_ee.shape, matrix_k_ei.shape, matrix_k_ie.shape, matrix_k_ii.shape)

        matrix_k_ = self.calculate_condensed_matrix(matrix_k_ee, matrix_k_ei, matrix_k_ii, matrix_k_ie)
        print (matrix_k_.shape)

        matrix_a_e = self.a_matrix_for_every_external_node(nodes_external_inp, nodes_correction)

        final_matrix_a_k = np.matmul(np.matmul(np.transpose(matrix_a_e), matrix_k_), matrix_a_e) / self.__area

        # self.spy_graphs(self.__matrix_k)

        for i in range(len(final_matrix_a_k)):
            for j in range(len(final_matrix_a_k)):
                if final_matrix_a_k[i][j] <= 1e-5:
                    final_matrix_a_k[i][j] = 0

        np.savetxt("..//resources//abdr-{}.csv".format(self.__file_name), final_matrix_a_k, delimiter=",",
                   fmt='% s')

        self.nodes_graph(nodes_correction, 'CorrectNodes')
        # print('zapisano {}'.format(self.__file_name))
        # print(final_matrix_a_k)

    def __calculate_area(self, a):
        self.__area = float(a) ** 2

    def nodes_graph(self, node_list, title):
        fig = plt.figure()
        fig.add_axes()
        ax = fig.gca(projection='3d')
        X = node_list[:, 1]
        Y = node_list[:, 3]
        Z = node_list[:, 2]

        ax.scatter(X, Y, Z)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.title('{}'.format(title))
        plt.show()

    def read_mtx(self):
        table = []
        try:
            input_file = open('C:\\temp\\{}-C_STIF1.mtx'.format(self.__file_name))
            for line in input_file:
                line_table = []
                for items in line.split(','):
                    line_table.append(float(items))

                table.append(line_table)
                del line_table

            input_file.close()
            return np.array(table)

        except IOError:
            warn("Failed to open 'C:\\temp\\{}-C_STIF1.mtx".format(self.__file_name))
            return None

    def split_data(self):
        mtx_data_from_file = self.read_mtx()

        index_table = mtx_data_from_file[:, 0:4]
        data_table = mtx_data_from_file[:, 4]
        return index_table, data_table

    def calculate_index(self, mtx_indexes):
        i_table = []
        j_table = []

        for line in range(len(mtx_indexes)):
            a = mtx_indexes[line][0]
            b = mtx_indexes[line][1]
            c = mtx_indexes[line][2]
            d = mtx_indexes[line][3]

            i_index = (a - 1) * self.__ndof + b - 1
            j_index = (c - 1) * self.__ndof + d - 1

            i_table.append(int(round(i_index, 0)))
            j_table.append(int(round(j_index, 0)))

        return i_table, j_table

    def creating_global_matrix(self):
        mtx_indices, mtx_data = self.split_data()
        i_mtx_index, j_mtx_index = self.calculate_index(mtx_indices)

        array_bottom = csr_matrix((mtx_data, (i_mtx_index, j_mtx_index)))
        array_top = csr_matrix((mtx_data, (j_mtx_index, i_mtx_index)))

        global_stiff_matrix = (array_bottom + array_top).toarray()

        length = global_stiff_matrix.shape[0]

        for i in range(length):
            for j in range(length):
                if i == j:
                    global_stiff_matrix[i, j] = global_stiff_matrix[i, j] / 2

        return global_stiff_matrix

    def calculate_dofs(self, ext_int):
        mtx_dof = []
        for node in ext_int:
            ndof_index = node * self.__ndof
            for nodes in range(self.__ndof):
                mtx_dof.append(ndof_index + nodes)
        return np.array(mtx_dof)

    def nodes_location(self):

        table_to_abdr = reading_nodes(self.__file_name)
        table_to_abdr = np.array(table_to_abdr)

        table_n = table_to_abdr[:, 0]

        table_x = table_to_abdr[:, 1]
        table_y = table_to_abdr[:, 3] * -1.0
        table_z = table_to_abdr[:, 2]

        self.nodes_graph(table_to_abdr, 'NodesBeforeCorrecting')

        maxx = max(table_x)
        maxy = max(table_y)
        maxz = max(table_z)

        minx = min(table_x)
        miny = min(table_y)
        minz = min(table_z)

        print(maxx, maxy, maxz)
        print(minx, miny, minz)

        table_x = table_x - maxx / 2
        table_y = table_y - miny / 2

        external_from_file = []
        internal_from_file = []

        for index in range(len(table_to_abdr)):
            index_number = int(table_n[index] - 1)

            index_x = table_x[index]
            index_y = table_y[index]

            if abs(index_x - maxx / 2) <= 1e-5 or abs(index_y - miny / 2) <= 1e-5 \
                    or abs(index_x + maxx / 2) <= 1e-5 or abs(index_y + miny / 2) <= 1e-5:
                external_from_file.append(index_number)

            else:
                internal_from_file.append(index_number)

        mtx_external_dof = self.calculate_dofs(external_from_file)
        mtx_internal_dof = self.calculate_dofs(internal_from_file)

        for node in range(len(table_to_abdr)):
            table_to_abdr[node][1] = table_to_abdr[node][1] - maxx / 2  # X Axis
            table_to_abdr[node][3] = table_to_abdr[node][3] * (-1) + abs(miny) / 2  # Y Axis

            table_to_abdr[node][2] = table_to_abdr[node][2] - maxz / 2  # Z Axis

        return mtx_external_dof, mtx_internal_dof, np.array(external_from_file), table_to_abdr

    def spy_graphs(self, spy_matrix):
        """spy graphs
        =============

        Function responsible for drawing graph of the matrices to check if matrix has correct size
        """

        plt.spy(spy_matrix, precision=0.001, markersize=0.1)
        plt.show()

    def calculate_condensed_matrix(self, kee2, kei2, kii2, kie2):
        """calculate condensed matrix
        ==============================

        Function responsible for multiplying matrices

        :param kee: stiffness matrix build from external nodes
        :param kei: stiffness matrix build from external and internal nodes
        :param kii: stiffness matrix build from internal nodes
        :param kie: stiffness matrix build from internal and external nodes
        :return: K_ condensed matrix
        """

        K_ = kee2 - np.matmul(np.matmul(kei2, np.linalg.inv(kii2)), kie2)
        return K_

    def __a0_func(self, x, y, z):
        if self.__ndof == 3:
            a0 = [[x, 0, y / 2, x * z, 0, y * z / 2, (-z) / 2, 0],
                  [0, y, x / 2, 0, y * z, x * z / 2, 0, (-z) / 2],
                  [0, 0, 0, ((-x) ** 2) / 2, ((-y) ** 2) / 2, (-x * y) / 2, (-x) / 2, (-y) / 2]]

        else:

            a0 = [[x, 0, y / 2, x * z, 0, y * z / 2, (-z) / 2, 0],
                  [0, y, x / 2, 0, y * z, x * z / 2, 0, (-z) / 2],
                  [0, 0, 0, ((-x) ** 2) / 2, ((-y) ** 2) / 2, (-x * y) / 2, (-x) / 2, (-y) / 2],

                  [0, 0, 0, 0, -y, (-x) / 2, 0, 0],
                  [0, 0, 0, x, 0, y / 2, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

        return np.array(a0)

    def a_matrix_for_every_external_node(self, table_ndof, table_to_abdr):
        abdr = []
        for items in table_to_abdr:
            if int(items[0] - 1) in table_ndof:
                a0 = self.__a0_func(items[1], items[3], items[2])
                for items2 in a0:
                    abdr.append(np.array(items2))
        return abdr

    def filtering_matrix(self, i_ndof, j_ndof):
        matrix_ij_half = self.__matrix_k[i_ndof, :]
        matrix_ij = matrix_ij_half[:, j_ndof]
        return matrix_ij


if __name__ == "__main__":
    # CreateAbdr('Test-Two-Elements', 0.2,3)
    # CreateAbdr('Test-Two-Elements-Same-Stiffness-Reinforcement', 0.2,3)

    # CreateAbdr('Test-Advanced-Hole', 0.2,3)
    # CreateAbdr('Test-Basic-Hole', 0.2,3)
    CreateAbdr('bianco', 8.0, 6)
