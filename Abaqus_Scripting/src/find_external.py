def get_ndof(table):
    external_ndof = []
    ndofs = 3

    for item in table:
        for item2 in range(1, ndofs + 1):
            i_index = (item - 1) * ndofs + item2 - 1
            external_ndof.append(i_index)

    return external_ndof


def reading_nodes(file_name):
    input_file = open("C:\\temp\\{}.inp".format(file_name))

    table = []
    is_correct_line = False

    for line in input_file:
        if line.startswith("*Node"):
            is_correct_line = True

        if is_correct_line:
            table_line = []
            if not line.startswith("*"):
                for items in line.split(','):
                    table_line.append(float(items))

            if not table_line == []:
                table.append(table_line)
            del table_line
        if line.startswith("*Element, type="):
            input_file.close()
            return table

    input_file.close()
    return 0


if __name__ == "__main__":
    print('test')