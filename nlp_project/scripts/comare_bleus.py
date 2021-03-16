import os

config1_dir = 'config1'
config2_dir = 'config2'
config3_dir = 'config3'
config4_dir = 'config4'
config5_dir = 'config5'
config6_dir = 'config6'

matches = {}
for filename in os.listdir(config1_dir):
  
  if filename.split('-')[-1] == 't':
    filename = filename.split('-')[0]
    matches[filename] = {} 

    source_file_1 = open(os.path.join(config1_dir, filename + '-s'), "r")
    source_file_2 = open(os.path.join(config2_dir, filename + '-s'), "r")
    source_file_3 = open(os.path.join(config3_dir, filename + '-s'), "r")
    source_file_4 = open(os.path.join(config4_dir, filename + '-s'), "r")
    source_file_5 = open(os.path.join(config5_dir, filename + '-s'), "r")
    source_file_6 = open(os.path.join(config6_dir, filename + '-s'), "r")

    target_file_1 = open(os.path.join(config1_dir, filename + '-t'), "r")
    target_file_2 = open(os.path.join(config2_dir, filename + '-t'), "r")
    target_file_3 = open(os.path.join(config3_dir, filename + '-t'), "r")
    target_file_4 = open(os.path.join(config4_dir, filename + '-t'), "r")
    target_file_5 = open(os.path.join(config5_dir, filename + '-t'), "r")
    target_file_6 = open(os.path.join(config6_dir, filename + '-t'), "r")

    source_lines_1 = list(map(str.strip, source_file_1.readlines()))
    source_lines_2 = list(map(str.strip, source_file_2.readlines()))
    source_lines_3 = list(map(str.strip, source_file_3.readlines()))
    source_lines_4 = list(map(str.strip, source_file_4.readlines()))
    source_lines_5 = list(map(str.strip, source_file_5.readlines()))
    source_lines_6 = list(map(str.strip, source_file_6.readlines()))

    target_lines_1 = list(map(str.strip, target_file_1.readlines()))
    target_lines_2 = list(map(str.strip, target_file_2.readlines()))
    target_lines_3 = list(map(str.strip, target_file_3.readlines()))
    target_lines_4 = list(map(str.strip, target_file_4.readlines()))
    target_lines_5 = list(map(str.strip, target_file_5.readlines()))
    target_lines_6 = list(map(str.strip, target_file_6.readlines()))

    source_files = [source_lines_1, source_lines_2, source_lines_3, source_lines_4, source_lines_5, source_lines_6]
    target_files = [target_lines_1, target_lines_2, target_lines_3, target_lines_4, target_lines_5, target_lines_6]
    
    index_file = -1
    for ft in target_files:
      index_file += 1
      index_line = -1
      for ft_line in target_files[index_file]:
        index_line += 1
        
        source_ref = source_files[index_file][index_line]
        
        if ft_line in matches[filename]:
          if source_ref in matches[filename][ft_line]:
            matches[filename][ft_line][source_ref] += ',config' + str(index_file+1)
          else:
            matches[filename][ft_line] = {source_ref: 'config' + str(index_file+1)}
        else:
          matches[filename][ft_line] = {source_ref: 'config' + str(index_file+1)}


fw = open('bleu_compare.txt', "a", encoding='utf8')
fw.truncate(0)
for ffile, json in matches.items():
  fw.write(ffile+'\n')
  for target, source in json.items():
    if len(list(source.values())[0].split(',')) < 6:
      fw.write('target: ' + target + '\n')
      fw.write('source: ' + list(source.keys())[0] + '\n')
      fw.write('configs: ' + list(source.values())[0] + '\n\n')


# print(matches)






  