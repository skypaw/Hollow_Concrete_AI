import numpy as np
import matplotlib.pyplot as plt


def volume(a, r):
    """" volume - temporary function
    ================================

    Calculate volume of concrete cube
    """

    volume_cube = a ** 3
    volume_cylinder = np.pi * r ** 2 * a
    volume_final = volume_cube - volume_cylinder
    return volume_final


def mass(volume_final, concrete):
    """" mass - temporary function
    ================================

    Calculate mass of concrete cube
    """

    cube_mass_calculation = concrete * volume_final
    return cube_mass_calculation


def data_for_network():
    """" data for networ - temporary function
    ================================

    It creates two arrays of data mass array and volume array based on two functions above with from minimum dimension
    to maximum, by increasing value of dimension a by 2 mm, and r by 1 mm
    """

    r = 0.05
    a = 0.150
    concrete = 2500

    # initialization of array for data elements
    dimensions = np.empty((0, 1), float)
    cube_mass = np.empty((0, 1), float)

    i = 0
    range_max = 760

    for i in range(range_max):
        volume_final = volume(a, r)
        cube_mass_calculation = mass(volume_final, concrete)

        dimensions = np.append(dimensions, volume_final)
        cube_mass = np.append(cube_mass, cube_mass_calculation)

        # new dimensions

        r += 0.001
        a += 0.002

        # increment
        i += 1

        # progress bar for big data input -> to check if program is still working
        if i % 10000 == 0:
            information = float(i) / range_max * 100
            final_information = "Calculating: " + str(information) + "%"
            print(final_information)

    print(dimensions)

    return dimensions, cube_mass


def plot(dim, cm):
    dim, cm = data_for_network()
    print(dim)
    print(cm)

    plt.plot(dim, cm)
    plt.show()


def data_for_testing():
    r = 0.0505
    a = 0.151
    concrete = 2500

    # initialization of array for data elements
    dimensions = np.empty((0, 1), float)
    cube_mass = np.empty((0, 1), float)

    i = 0
    range_max = 30

    for i in range(range_max):
        volume_final = volume(a, r)
        cube_mass_calculation = mass(volume_final, concrete)

        dimensions = np.append(dimensions, volume_final)
        cube_mass = np.append(cube_mass, cube_mass_calculation)

        # new dimensions

        r += 0.004
        a += 0.008

        # increment
        i += 1
    return dimensions, cube_mass


print(data_for_testing())