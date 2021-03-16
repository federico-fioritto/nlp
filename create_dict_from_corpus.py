
import sys

if (len(sys.argv) == 1) :
  print('Ingrese el archivo del corpus como argumento. Ej: python createDictFromCorpus.py corpus.txt')
elif sys.argv[1] == 'cess_esp' :
  import json
  from nltk.corpus import cess_esp

  file = 'cess_esp'
  wordsToLower = map(lambda x:x.lower(), cess_esp.words())
  d = dict.fromkeys(set(wordsToLower), 1)
else :
  import os
  import json
  from nltk.corpus import PlaintextCorpusReader
  
  path, file = os.path.split(sys.argv[1])
  corpus = PlaintextCorpusReader(path, file)
  wordsToLower = map(lambda x:x.lower(), corpus.words())
  d = dict.fromkeys(set(wordsToLower), 1)

jsonF = json.dumps(d)
f = open(file + ".json", "w")
f.write(jsonF)
f.close()
