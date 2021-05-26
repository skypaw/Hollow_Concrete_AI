from scipy.sparse import csr_matrix
import matplotlib.pylab as plt
import numpy as np
from find_external import *
from warnings import warn
from matplotlib import pyplot as plt3d
from mpl_toolkits import mplot3d


class CreateAbdr:
    __file_name = None
    __area = None
    __ndof = 6

    def __init__(self, file_name, a):
        self.__file_name = file_name
        self.__calculate_area(a)

        mtx_data_from_file = self.read_mtx()

        nodes_from_inp = reading_nodes(self.__file_name)
        dof_external, dof_internal, nodes_external_inp = self.nodes_location(nodes_from_inp)

        mtx_indices, mtx_dof_values = self.split_data(mtx_data_from_file)
        mtx_i, mtx_j = self.calculate_index(mtx_indices)

        matrix_k = self.func(mtx_dof_values, mtx_i, mtx_j)

        matrix_k_ee, matrix_k_ii, matrix_k_ei, matrix_k_ie = self.filtering_matrix(matrix_k, dof_external, dof_internal)

        matrix_k_ = self.calculate_condensed_matrix(matrix_k_ee, matrix_k_ei, matrix_k_ii, matrix_k_ie)

        matrix_a_e = self.a_matrix_for_every_external_node(nodes_external_inp, nodes_from_inp)

        final_matrix_a_k = np.matmul(np.matmul(np.transpose(matrix_a_e), matrix_k_), matrix_a_e) / self.__area

        for index_i in range(0, len(final_matrix_a_k)):
            for index_j in range(0, len(final_matrix_a_k)):
                if final_matrix_a_k[index_i][index_j] <= 1e-5:
                    final_matrix_a_k[index_i][index_j] = 0

        np.savetxt("abdr-{}.csv".format(self.__file_name), final_matrix_a_k, delimiter=",", fmt='% s')
        print 'zapisano {}'.format(self.__file_name)

        print final_matrix_a_k

    def __calculate_area(self, a):
        self.__area = float(a) ** 2

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

            return np.array(table)

        except IOError:
            warn("Failed to open 'C:\\temp\\{}-C_STIF1.mtx".format(self.__file_name))
            return None

    def split_data(self, mtx_table):
        index_table = mtx_table[:, 0:4]
        data_table = mtx_table[:, 4]
        return index_table, data_table

    def calculate_index(self, mtx_indexes):
        i_table = []
        j_table = []

        for line in range(0, len(mtx_indexes)):
            a = mtx_indexes[line][0]
            b = mtx_indexes[line][1]
            c = mtx_indexes[line][2]
            d = mtx_indexes[line][3]

            i_index = (a - 1) * self.__ndof + b - 1
            j_index = (c - 1) * self.__ndof + d - 1

            i_table.append(int(round(i_index, 0)))
            j_table.append(int(round(j_index, 0)))

        return i_table, j_table

    def func(self, mtx_data, i_mtx_index, j_mtx_index):
        array = csr_matrix((mtx_data, (i_mtx_index, j_mtx_index))).toarray()
        array1 = csr_matrix((mtx_data, (j_mtx_index, i_mtx_index))).toarray()

        B = array + array1

        length = B.shape[0]

        for index_i in range(0, length):
            for index_j in range(0, length):
                if index_i == index_j:
                    B[index_i, index_j] = B[index_i, index_j] / 2

        return B

    def nodes_location(self, table_to_abdr):
        table_to_abdr = np.array(table_to_abdr)

        table_x = table_to_abdr[:, 1]
        table_y = table_to_abdr[:, 2]
        table_z = table_to_abdr[:, 3]

        maxx = max(table_x)
        maxy = max(table_y)
        maxz = max(table_z)

        print maxx, maxy, maxz

        external_from_file = []
        internal_from_file = []

        for index in table_to_abdr:
            index_number = index[0]

            index_x = index[1]
            index_y = index[2]

            if (abs(index_x - maxx) <= 0e-5 or abs(index_y - maxy) <= 0e-5) or \
                    (abs(index_x - 0) <= 0e-5 or abs(index_y - 0) <= 0e-5):
                external_from_file.append(int(index_number - 1))

            else:
                internal_from_file.append(int(index_number - 1))

        mtx_external_nodes = []
        for node in external_from_file:
            ndof_index = node * self.__ndof
            for nodes in range(self.__ndof):
                mtx_external_nodes.append(ndof_index + nodes)

        mtx_internal_nodes = []
        for node in internal_from_file:
            ndof_index = node * self.__ndof
            for nodes in range(self.__ndof):
                mtx_internal_nodes.append(ndof_index + nodes)

        return np.array(mtx_external_nodes), np.array(mtx_internal_nodes), np.array(external_from_file)

    def read_internal(self, i_table_index, mtx_exterernal_ndof):
        internal_ndof = []
        for item in i_table_index:
            if item not in mtx_exterernal_ndof:
                if item not in internal_ndof:
                    internal_ndof.append(item)

        return internal_ndof

    def spy_graphs(self, main_matrix, kee, kei, kie, kii):
        """spy graphs
        =============

        Function responsible for drawing graph of the matrixes to check if matrix has correct size
        """

        plt.spy(main_matrix, precision=0.001, markersize=0.1)
        plt.show()
        plt.spy(kee, precision=0.001, markersize=0.1)
        plt.show()
        plt.spy(kei, precision=0.001, markersize=0.1)
        plt.show()
        plt.spy(kie, precision=0.001, markersize=0.1)
        plt.show()
        plt.spy(kii, precision=0.001, markersize=0.1)
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

    def a0_func(self, x, y, z):
        if self.__ndof == 3:
            a0 = [[x, 0, y / 2, x * z, 0, y * z / 2, -z / 2, 0],
                  [0, y, x / 2, 0, y * z, x * z / 2, 0, -z / 2],
                  [0, 0, 0, (-x) ** 2 / 2, (-y) ** 2 / 2, -x * y / 2, -x / 2, -y / 2]]

        else:
            a0 = [[x, 0, y / 2, x * z, 0, y * z / 2, -z / 2, 0],
                  [0, y, x / 2, 0, y * z, x * z / 2, 0, -z / 2],
                  [0, 0, 0, (-x) ** 2 / 2, (-y) ** 2 / 2, -x * y / 2, -x / 2, -y / 2],
                  [0, 0, 0, 0, -y, -x / 2, 0,0],
                  [0, 0, 0, x, 0, y / 2, -0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

        return a0

    def a_matrix_for_every_external_node(self, table_ndof, table_to_abdr):
        abdr = []
        for items in table_to_abdr:
            if int(items[0] - 1) in table_ndof:
                a0 = self.a0_func(items[1], items[2], items[3])
                for items2 in a0:
                    abdr.append(np.array(items2))
        return np.array(abdr)

    def filtering_matrix(self, mtx_main_matrix, external_ndof, internal_ndof):
        kee = mtx_main_matrix[external_ndof, :]
        kee1 = kee[:, external_ndof]

        kii = mtx_main_matrix[internal_ndof, :]
        kii1 = kii[:, internal_ndof]

        kei = mtx_main_matrix[:, internal_ndof]
        kei1 = kei[external_ndof, :]

        kie = mtx_main_matrix[internal_ndof, :]
        kie1 = kie[:, external_ndof]

        return kee1, kii1, kei1, kie1


if __name__ == "__main__":
    '''CreateAbdr('Test-Two-Elements', 0.2)
    CreateAbdr('Test-Two-Elements-E11', 0.2)
    CreateAbdr('Test-Two-Elements-E22', 0.2)
    CreateAbdr('Test-Two-Elements-E33', 0.2)
    CreateAbdr('Test-Two-Elements-Same-Stiffness', 0.2)
    CreateAbdr('Test-Two-Elements-Same-Stiffness-1', 0.2)'''

    CreateAbdr('bianco-saw595-ax', 8.0)
