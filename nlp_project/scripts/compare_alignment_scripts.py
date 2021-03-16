_import os

luisa_dir = 'luisa'
bleu_dir = 'bleu'
own_dir = 'own_script'
compare_dir = 'compare'

for filename in os.listdir(luisa_dir):
  # El índice de luisa y own es el mismo
  luisa_index = -1
  bleu_index = 0

  luisa_file = open(os.path.join(luisa_dir, filename), "r")
  luisa_content = list(map(str.strip, luisa_file.readlines()))

  luisa_file = open(os.path.join(luisa_dir, filename), "r")
  bleu_source_file = open(os.path.join(bleu_dir, filename + '-s'), "r")
  bleu_target_file = open(os.path.join(bleu_dir, filename + '-t'), "r")
  own_file = open(os.path.join(own_dir, filename), "r")
  compare_file = open(os.path.join(compare_dir, "compare_" + filename), "a")
  compare_file.truncate(0)

  bleu_target_content = list(map(str.strip, bleu_target_file.readlines()))
  bleu_source_content = list(map(str.strip, bleu_source_file.readlines()))
  own_content = list(map(str.strip, own_file.readlines()))

  for luisa_line in luisa_file:
    luisa_index += 1
    luisa_line = luisa_line.strip()
    if luisa_line.strip() != '':
      own_line = own_content[luisa_index].strip()

      # print(luisa_index+1, bleu_index+1)
      # if luisa_index == 36:
      #   print(luisa_line, bleu_index)
      #   print(bleu_target_content[bleu_index])
      #   print(bleu_target_content[bleu_index].strip() == luisa_line.strip())
      #   print(luisa_index < len(bleu_target_content) )
      #   print(len(bleu_target_content) )
      if (bleu_index < len(bleu_target_content) and bleu_target_content[bleu_index] not in luisa_content):
        bleu_source_line = bleu_source_content[bleu_index].strip()
        bleu_target_line = bleu_target_content[bleu_index].strip()
        bleu_index += 1
        compare_file.write('-------------BLEU CAMBIO LINEA LUISA-------------\n')
        compare_file.write('TARGET:    ' + bleu_target_line + '\n')
        compare_file.write('SOURCE:    ' + bleu_source_line + '\n')
        compare_file.write('\n')
      if bleu_index < len(bleu_target_content) and bleu_target_content[bleu_index].strip() == luisa_line.strip():
        # Bleu conservó la línea
        bleu_line = bleu_source_content[bleu_index].strip()
        bleu_index += 1
        if own_line.strip() != bleu_line.strip():
          compare_file.write('-------------DISTINTAS ALINEACIONES-------------\n')
          compare_file.write('LUISA:    ' + luisa_line + '\n')
          compare_file.write('BLEU:     ' + bleu_line + '\n')
          compare_file.write('OWN:      ' + own_line + '\n')
          compare_file.write('\n')
      else:
        compare_file.write('-------------BLEU ELIMINÓ-------------\n')
        compare_file.write('LUISA:    ' + luisa_line + '\n')
        compare_file.write('OWN:      ' + own_line + '\n')
        compare_file.write('\n')


  luisa_file.close()
  bleu_target_file.close()
  bleu_source_file.close()
  own_file.close()
  compare_file.close()