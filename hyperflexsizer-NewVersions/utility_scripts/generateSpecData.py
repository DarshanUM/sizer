import csv


def create_data():
    fo = open('SpecInfo.csv', 'r')
    output = open('SpecIntData.sql','w')

    json_data = csv.DictReader(fo)
    record_id = 1
    for row in json_data:
        output_string = "INSERT INTO hyperconverged_specintdata "
        output_string += "(id, model, speed, cores, blended_core) VALUES ("
        output_string += str(record_id) + ",\"" + row["Model"] + "\"" 
        output_string += "," + str(row["Speed (GHz)"]) + "," + str(row["Cores"])
        output_string += "," + str(row["Blended/Core"]) + ");\n"

        output.write(output_string)

        record_id += 1

    fo.close()
    output.close()

create_data()
