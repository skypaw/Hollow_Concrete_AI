from numpy import pi


def mesh_calculation(a, h):
    """mesh_calculation
    ===================

    Function responsible for calculation of the mesh size

    :param a: a
    :param h: height of the model
    :return: mesh size
    """

    mesh_size = (float(a) + float(h)) / 2 / 15
    return mesh_size


def r_calculate(as_size):
    """r_calculate
    ==============

    Function responsible for calculation of the mesh size

    :param as_size: area of the reinforcement in model
    :return: area per one bar in model
    """

    as_r = (as_size / pi) ** 0.5 / 2
    return as_r


def check_dimensions(r, l, a, a1, h):
    """check dimensions
    ===================

    checking model dimensions. Model is limited by geometric values. For example hole cannot be greater than width and
    height of the model. Parameters a1, a, h are responsible for excluding cases in which the model would be incorrect.

    :param r: radius of the hole in a concrete model
    :param l: height of the hole in the concrete model
    :param a: width of the concrete model
    :param a1: lagging in concrete models that prevents reinforcement from environmental influences
    :param h: height of the concrete model

    :return: new or unchanged values for radius and height of the hole
    """

    # Checking if diameter isn't greater than width of the model, if is -> change radius
    diameter = 2 * float(r)

    if diameter >= a:
        r = float(a) / 2 - 0.01 * float(a)

    # Checking if l (height of the hole in concrete) isn't too large, if is -> change l

    if 2 * a1 + r * 2 + l >= h:
        l = float(h) - (float(a1) * 2 + float(r) * 2)

        if l < 0:
            l = float(0)

    return r, l


if __name__ == "__main__":
    print('Testing functions')

    __mesh_size = mesh_calculation(10, 10)
    __r_size = r_calculate(4)
    __new_r, __new_l = check_dimensions(10, 10, 5, 2, 15)

    print(__mesh_size)
    print(__r_size)
    print('10', __new_r, '10', __new_l)
