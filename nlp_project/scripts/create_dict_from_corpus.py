
import sys

if (len(sys.argv) == 1) :
  print('Ingrese el archivo del corpus como argumento. Ej: python createDictFromCorpus.py corpus.txt')
else :
  import os
  import csv
  from nltk.corpus import PlaintextCorpusReader
  
  path, file = os.path.split(sys.argv[1])
  corpus = PlaintextCorpusReader(path, file)
  wordsToLower = map(lambda x:x.lower(), corpus.words())
  d = dict.fromkeys(set(wordsToLower), 1)
  w = csv.writer(open(file + ".csv", "w"))
  for key, val in d.items():
      w.writerow([key, val])
