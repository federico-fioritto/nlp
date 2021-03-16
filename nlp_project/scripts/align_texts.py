import sys
from difflib import SequenceMatcher

matches = []
f1_used_lines = {}
file1 = sys.argv[1]
file2 = sys.argv[2]


all_matched = False

while not all_matched:
  all_matched = True
  f2 = open(file2, "r")
  f2_index = -1

  for line2 in f2:
    f2_index += 1
    if len(matches) < f2_index + 1:
      # Inicializo líneas no matcheadas
      matches.append({
        'prob': -1,
      })
    
    
    if line2.strip() == '' and matches[f2_index]['prob'] == -1:
      # Matcheo los saltos de línea
      matches[f2_index]['prob'] = 0
      matches[f2_index]['line1'] = '\n'
      matches[f2_index]['line2'] = line2
    elif matches[f2_index]['prob'] == -1:
      # Si no es -1, es porque ya se encontró el match
      f1 = open(file1, "r")
      max_prob = -1
      index_f1 = 0
      max_line = ''

      for i, line1 in enumerate(f1):
        # Recorro el file1 buscando el mejor match
        score = SequenceMatcher(None, line2, line1).ratio()
        if score > max_prob and (i not in f1_used_lines or f1_used_lines[i]['prob'] < score):
          # Encuentro la línea del file1 con más score que no haya sido usada o que tenga mayor score que la que ya haya sido usada
          max_prob = score
          index_f1 = i
          max_line = line1

      # Si ya se usó => esta tiene más score (por la condición dentro del for)
      if index_f1 in f1_used_lines:
        # Existen líneas sin matchear
        all_matched = False
        # Marco una línea anterior como no matcheada
        matches[f1_used_lines[index_f1]['f2_index']]['prob'] = -1

        f1_used_lines[index_f1]['prob'] = max_prob
        f1_used_lines[index_f1]['f2_index'] = f2_index
      else:
        f1_used_lines[index_f1] = {
          'prob': max_prob,
          'f2_index': f2_index
        }
      
      
      matches[f2_index]['prob'] = max_prob
      matches[f2_index]['line1'] = max_line
      matches[f2_index]['line2'] = line2


fw1 = open('aligned_' + file1, "a")
# fw2 = open("file2.txt", "a")
for elem in matches:
  fw1.write(elem['line1'])
  # fw2.write(elem['line2'])

  
f1.close()
fw1.close()
f2.close()
# fw2.close()






















    # if len(matches) > index_f1 and matches[index_f1]['prob'] < max_prob :
    #   matches[index_f1]['prob'] = max_prob
    #   matches[index_f1]['line1'] = max_line
    #   matches[index_f1]['line2'] = line2
    # elif len(matches) <= index_f1 :
    #   print(a'')
    #   matches.append({
    #     'prob': max_prob, 
    #     'line1': max_line, 
    #     'line2': line2
    #   })

# for line1 in f1:
#   if line1.strip() != '':
#     print('file1:', line1)
#     f2 = open(file2, "r")
#     max_prob = -1
#     index = 0
#     max_line = ''

#     for i, line2 in enumerate(f2):
#       score = SequenceMatcher(None, line1, line2).ratio()
#       if score > max_prob:
#         max_prob = score
#         index = i
#         max_line = line2

#     # print('file2:', max_prob, max_line)
#     if len(matches) > index and matches[index]['prob'] < max_prob :
#       matches[index]['prob'] = max_prob
#       matches[index]['line1'] = line1
#       matches[index]['line2'] = max_line
#     elif len(matches) <= index :
#       matches.append({
#         'prob': max_prob, 
#         'line1': line1, 
#         'line2': max_line
#       })
    
#     # print(matches[0:5])