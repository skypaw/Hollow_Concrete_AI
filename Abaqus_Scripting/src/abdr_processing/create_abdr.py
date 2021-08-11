import matplotlib.pylab as plt
import numpy as np
from creating_main_stiffness_matrix import creating_global_matrix
from filtering_main_matrix import nodes_location


class CreateAbdr:
    __file_name = None
    __a = None
    __area = None
    __ndof = None
    __matrix_k = None

    def __init__(self):
        print ("Init ABDR object")

    def calculate_abdr(self):
        self.__calculate_area(self.__a)

        print self.__file_name, self.__a, self.__area

        self.__matrix_k = creating_global_matrix(self.__file_name, self.__ndof)
        #print self.__matrix_k.shape, "Shape of the Main Matrix"

        dof_external, dof_internal, nodes_external_inp, nodes_correction = nodes_location(self.__file_name, self.__ndof)

        matrix_k_ee = self.filtering_matrix(dof_external, dof_external)
        matrix_k_ii = self.filtering_matrix(dof_internal, dof_internal)
        matrix_k_ei = self.filtering_matrix(dof_external, dof_internal)
        matrix_k_ie = self.filtering_matrix(dof_internal, dof_external)

        #print(matrix_k_ee.shape, matrix_k_ei.shape, matrix_k_ie.shape, matrix_k_ii.shape), "Shape of the Sub Matricies"

        matrix_k_ = self.calculate_condensed_matrix(matrix_k_ee, matrix_k_ei, matrix_k_ii, matrix_k_ie)
        print (matrix_k_.shape), "Shape of the Condensed Matrix"

        matrix_a_e = self.a_matrix_for_every_external_node(nodes_external_inp, nodes_correction)
        self.final_matrix_a_k = np.matmul(np.matmul(np.transpose(matrix_a_e), matrix_k_), matrix_a_e) / self.__area

        # self.spy_graphs(self.__matrix_k)

        for i in range(len(self.final_matrix_a_k)):
            for j in range(len(self.final_matrix_a_k)):
                if self.final_matrix_a_k[i][j] <= 1e-5:
                    self.final_matrix_a_k[i][j] = 0

        # np.savetxt("..//..//resources//abdr-{}.csv".format(self.__file_name), self.final_matrix_a_k, delimiter=",",fmt='% s')

        # self.nodes_graph(nodes_correction, 'CorrectNodes')
        # print('zapisano {}'.format(self.__file_name))
        # print(final_matrix_a_k)
        print "End of calculation"

    def set_data(self, file_name, a, ndof):
        self.__file_name = file_name
        self.__a = a
        self.__ndof = int(ndof)

    def get_results(self):
        a11 = self.final_matrix_a_k[0, 0]
        a22 = self.final_matrix_a_k[1, 1]
        a12 = self.final_matrix_a_k[0, 1]
        a33 = self.final_matrix_a_k[2, 2]
        d11 = self.final_matrix_a_k[3, 3]
        d22 = self.final_matrix_a_k[4, 4]
        d12 = self.final_matrix_a_k[3, 4]
        d33 = self.final_matrix_a_k[5, 5]
        a44 = self.final_matrix_a_k[6, 6]
        a55 = self.final_matrix_a_k[7, 7]

        return np.array([a11, a22, a12, a33, d11, d22, d12, d33, a44, a55])

    def __calculate_area(self, a):
        self.__area = float(a) ** 2

    def nodes_graph(self, node_list, title):
        fig = plt.figure()
        fig.add_axes()
        ax = fig.gca(projection='3d')
        X = node_list[:, 1]
        Y = node_list[:, 2]
        Z = node_list[:, 3]

        ax.scatter(X, Y, Z)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.title('{}'.format(title))
        plt.show()

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
                  [0, 0, 0, (-x ** 2) / 2, (-y ** 2) / 2, -x * y / 2, (-x) / 2, (-y) / 2], ]

        else:

            a0 = [[x, 0, (y / 2), (x * z), 0, (y * z / 2), (-z / 2), 0],
                  [0, y, (x / 2), 0, (y * z), (x * z / 2), 0, (-z / 2)],
                  [0, 0, 0, (-x ** 2 / 2), (-y ** 2 / 2), (-x * y / 2), (-x / 2), (-y / 2)],

                  [0, 0, 0, 0, -y, (-x / 2), 0, 0],
                  [0, 0, 0, x, 0, (y / 2), 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0], ]

        return np.array(a0)

    def a_matrix_for_every_external_node(self, table_ndof, table_to_abdr):
        abdr = []
        for items in table_to_abdr:
            if int(items[0] - 1) in table_ndof:
                a0 = self.__a0_func(float(items[1]), float(items[2]), float(items[3]))

                abdr.extend(a0)
        return abdr

    def filtering_matrix(self, i_ndof, j_ndof):
        matrix_ij_half = self.__matrix_k[i_ndof, :]
        matrix_ij = matrix_ij_half[:, j_ndof]
        return matrix_ij


if __name__ == "__main__":
    # CreateAbdr('Test-Two-Elements', 0.2,3)
    # CreateAbdr('Test-Two-Elements-Same-Stiffness-Reinforcement', 0.2,3)

    # CreateAbdr('Test-Advanced-Hole', 0.2,3)
    # CreateAbdr('Job-1', 0.2,3)

    # CreateAbdr('Dwuteownik', 8.0, 6)
    c = CreateAbdr()
    c.set_data('bianco-saw595-ax', 8.0, 6)
    c.calculate_abdr()
    print(c.get_results())
