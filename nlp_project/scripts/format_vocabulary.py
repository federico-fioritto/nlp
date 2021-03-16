# Formatea un vocabulario temporal que tiene / y comentarios para agregar al archivo vocabulary final

with open('../docs/vocabularies/rla1.txt', encoding='utf8') as fp:
  line = fp.readline()
  out = open("../docs/vocabularies/rla2.txt", "a+", encoding='utf8')
  
  while line:
    word = line.split('/')[0].rstrip()
    word = word.split('#')[0].rstrip()
    print('procesando ', word)
    
    if word != '':
      out.write(word + ' 10\n')
    
    line = fp.readline()

  out.close()