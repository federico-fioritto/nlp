import os

# GENERAR UN CSV CON LOS PRINTS E IMPORTAR A LA BASE


# PRINTEA PARA GENERAR UN CSV DE LAS 576 CONFIGS 
# for i in range(576):
#   indexFile = i + 1

#   conffile = open(os.getcwd() + "/../docs/results/config" + str(indexFile) + '.csv' , "r")
#   for line in conffile.readlines()[1:]:
#     line = line.rstrip().split(',')
#     # print(line.rstrip().split(','))
#     # print("INSERT INTO CONFIGS (config, score, file) VALUES ('config" + str(indexFile) + ".csv', " + line[1] + ",'" + line[0] + "');")
#     print("'config" + str(indexFile) + ".csv', " + line[1] + ",'" + line[0] + "'")


# PRINTEA PARA GENERAR UN CSV DE LOS ARCHIVOS SIN PROCESAR
conffile = open(os.getcwd() + "/../docs/results/159692463466.csv", "r")
for line in conffile.readlines()[1:]:
  line = line.rstrip().split(',')
  print("'not_processed', " + line[1] + ",'" + line[0] + "'")