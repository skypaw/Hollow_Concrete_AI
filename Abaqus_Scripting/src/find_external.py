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

        if line.startswith("*Element"):
            input_file.close()
            return table

    input_file.close()
    return None


if __name__ == "__main__":
    print('test')
