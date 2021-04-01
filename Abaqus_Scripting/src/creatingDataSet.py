from main import Main

cDS = Main()

for a in range(100, 181, 16):
    for h in range(150, 501, 35):
        Main.modify_model(cDS, a, h, 226, 30, 30)
        Main.read_dimensions(cDS)
        Main.creating_model(cDS)
        Main.read_odb(cDS)

Main.save_dimensions(cDS)
Main.save_results(cDS)
