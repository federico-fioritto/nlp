import os
DICT_AR='es_AR'
DICT_UY='es_UY'

if (os.path.exists('./wordlist')):
  print('finished')
  exit()

with open(DICT_AR + '.dic', encoding='utf8') as fp:
  line = fp.readline()
  while line:
    word = line.split('/')[0].rstrip()
    print('procesando ', word)
    
    if word != '':
      os.system('wordforms ' + DICT_AR + '.aff ' + DICT_AR + '.dic ' + word + ' >> wordlist')
    
    line = fp.readline()
    
with open(DICT_UY + '.dic', encoding='utf8') as fp:
  line = fp.readline()
  while line:
    word = line.split('/')[0].rstrip()
    print('procesando ', word)
    
    if word != '':
      os.system('wordforms ' + DICT_UY + '.aff ' + DICT_UY + '.dic ' + word + ' >> wordlist')
    
    line = fp.readline()