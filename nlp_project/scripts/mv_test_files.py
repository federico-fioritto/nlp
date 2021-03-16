import os

print(os.getcwd())
namefiles = open(os.getcwd() + '/../docs/used_files_for_configs_test.txt', "r")

os.system('mkdir '+ os.getcwd() + '/../docs/outputs/tanda1/test/')
for filename in namefiles:
  # luisa
  os.system('cp '+ os.getcwd() + '/../LUISA/luisa_join/tanda1/' + filename.strip() + ' ' + os.getcwd() + '/../LUISA/luisa_join/tanda1_test/' ) 
  os.system('cp '+ os.getcwd() + '/../LUISA/luisa_split/tanda1/' + filename.strip() + ' ' + os.getcwd() + '/../LUISA/luisa_split/tanda1_test/' )

  # abbyy
  os.system('cp '+ os.getcwd() + '/../docs/outputs/tanda1/all/' + filename.strip() + ' ' + os.getcwd() + '/../docs/outputs/tanda1/test/' ) 