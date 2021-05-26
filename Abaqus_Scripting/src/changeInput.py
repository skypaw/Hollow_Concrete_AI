import warnings


def change_input(job_name, job_name_changed):
    """change_input
    ===============

    Function responsible for changing input of the file .inp. Step is changed to calculate stiffness matrix

    :param job_name: string with the name of the job
    :param job_name_changed: string with the name of the job after changed step
    :return:
    """

    try:
        input_file = open("C:\\temp\\{}.inp".format(job_name))
        output_file = open("C:\\temp\\{}.inp".format(job_name_changed), "w")

        for line in input_file:

            output_file.write(line)
            if line.startswith("** STEP:"):
                output_file.write('**\n** Output Global Stiffness Matrix\n*Step, name=Global_Stiffness_Matrix\n* \
                MATRIX GENERATE, STIFFNESS\n* MATRIXOUTPUT, STIFFNESS, FORMAT = MATRIXINPUT\n* ENDSTEP\n')

                print('Changed inp for {}'.format(job_name))
                return

        warnings.warn("File doesn't contain specific line")

    except IOError:
        warnings.warn("File C:\\temp\\{}.inp doesn't exist)".format(job_name))


if __name__ == "__main__":
    print("Testing of the input")

    change_input('test', 'test-s')
    change_input('test-1', 'test-s-1')
    change_input('Test-One-Element', 'Test-One-Element-C')
    change_input('Test-Two-Elements', 'Test-Two-Elements-C')
    change_input('Test-Two-Elements-Same-Stiffness', 'Test-Two-Elements-Same-Stiffness-C')
    change_input('Test-Two-Elements-Same-Stiffness-1', 'Test-Two-Elements-Same-Stiffness-1-C')
    change_input('Test-Two-Elements-E11', 'Test-Two-Elements-E11-C')
    change_input('Test-Two-Elements-E22', 'Test-Two-Elements-E22-C')
    change_input('Test-Two-Elements-E33', 'Test-Two-Elements-E33-C')
    change_input('Test-Basic', 'Test-Basic-C')
    change_input('Test-Basic-Hole', 'Test-Basic-Hole-C')
    change_input('Test-Advanced', 'Test-Advanced-C')
    change_input('Test-Advanced-Hole', 'Test-Advanced-Hole-C')
