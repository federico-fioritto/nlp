from difflib import SequenceMatcher
import sys

arg0 = sys.argv[1]
arg1 = sys.argv[2]
one = open(arg0, errors='ignore').read()
two = open(arg1, errors='ignore').read()

print("Secuence Matcher")
print(str(SequenceMatcher(None, one, two).ratio()))


import spacy
nlp = spacy.load('es')
doc1 = nlp(one)
doc2 = nlp(two)

#Tira warning porque es muy chico el corpus o los docs que vamos a comparar
print("Spacy")
print(doc1.similarity(doc2))
