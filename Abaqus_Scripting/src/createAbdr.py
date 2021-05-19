from scipy.sparse import csr_matrix
import matplotlib.pylab as plt
import numpy as np
from find_external import *
from warnings import warn


class CreateAbdr:
    __file_name = None
    __area = None

    def __init__(self, file_name, a):
        self.__file_name = file_name
        self.__calculate_area(a)

        mtx_table = self.read_mtx()

        table_to_abdr = reading_ndof_to_abdr(self.__file_name)

        table_ndof = reading_ndof(self.__file_name)

        mtx_indexes, mtx_data = self.split_data(mtx_table)

        i_mtx_index, j_mtx_index = self.calculate_index(mtx_indexes)

        B = self.func(mtx_data, i_mtx_index, j_mtx_index)

        external_ndof = get_ndof(table_ndof)

        internal_ndof = self.read_internal(i_mtx_index, external_ndof)

        kee1, kii1, kei1, kie1 = self.filtering_matrix(B, external_ndof, internal_ndof)

        K_ = self.calculate_condensed_matrix(kee1, kei1, kii1, kie1)

        abdr = self.a_matrix_for_every_node(table_ndof, table_to_abdr)


        ak = np.matmul(np.matmul(np.transpose(abdr), K_), abdr) / self.__area

        for index_i in range(0, len(ak)):
            for index_j in range(0, len(ak)):
                if ak[index_i][index_j] <= 1e-5:
                    ak[index_i][index_j] = 0

        np.savetxt("abdr-{}.csv".format(self.__file_name), ak, delimiter=",", fmt='% s')

        print ak

    def __calculate_area(self, a):
        self.__area = float(a) ** 2

    def read_mtx(self):
        global input_file
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

            ndofs = 3
            i_index = (a - 1) * ndofs + b - 1
            j_index = (c - 1) * ndofs + d - 1

            i_table.append(int(round(i_index, 0)))
            j_table.append(int(round(j_index, 0)))

        return i_table, j_table

    def func(self, mtx_data, i_mtx_index, j_mtx_index):
        array = csr_matrix((mtx_data, (i_mtx_index, j_mtx_index))).toarray()
        array1 = csr_matrix((mtx_data, (j_mtx_index, i_mtx_index))).toarray()

        A = csr_matrix(array)
        A.todense()
        A.toarray()

        A1 = csr_matrix(array1)
        A1.todense()
        A1.toarray()

        B = array + array1

        length = B.shape[0]

        for index_i in range(0, length):
            for index_j in range(0, length):
                if index_i == index_j:
                    B[index_i, index_j] = B[index_i, index_j] / 2

        return B

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
        a0 = [[x, 0, y / 2, x * z, 0, y * z / 2, -z / 2, 0],
              [0, y, x / 2, 0, y * z, x * z / 2, 0, -z / 2],
              [0, 0, 0, (-x) ** 2 / 2, (-y) ** 2 / 2, -x * y / 2, -x / 2, -y / 2]]
        return a0

    def a_matrix_for_every_node(self, table_ndof, table_to_abdr):
        abdr = []
        for items in table_to_abdr:
            if int(items[0]) in table_ndof:
                a0 = self.a0_func(items[1], items[2], items[3])
                for items2 in a0:
                    abdr.append(items2)
        return abdr

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
    CreateAbdr('Test-One-Element', 0.2)

    CreateAbdr('Test-Basic-Hole', 0.2)

    CreateAbdr('Test-Two-Elements', 0.2)
    CreateAbdr('Test-Basic', 0.2)

'''if __name__ == "__main__":
      
    main_matrix = np.array(([1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]))
    external = [0, 1, 2]
    internal = [3]

    k, l, m, n = filtering_matrix(main_matrix, external, internal)

    plt.spy(main_matrix, precision=0.001, markersize=1)
    plt.show()
    plt.spy(k, precision=0.001, markersize=1)
    plt.show()
    plt.spy(l, precision=0.001, markersize=1)
    plt.show()
    plt.spy(m, precision=0.001, markersize=1)
    plt.show()
    plt.spy(n, precision=0.001, markersize=1)
    plt.show()

    print (main_matrix)
    print (k)
    print (l)
    print (m)
    print (n)
'''
