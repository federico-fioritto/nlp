import re
from collections import Counter
from nltk.corpus import cess_esp
# import numpy as np
# from weighted_levenshtein import lev
#
#
# insert_costs = np.ones(128, dtype=np.float64)  # make an array of all 1's of size 128, the number of ASCII characters
# insert_costs[ord('D')] = 1.5  # make inserting the character 'D' have cost 1.5 (instead of 1)
#
# # you can just specify the insertion costs
# # delete_costs and substitute_costs default to 1 for all characters if unspecified
# print( lev('BANANAS', 'BANDANAS', insert_costs=insert_costs))  # prints '1.5'

def words(text): return re.findall(r'\w+', text.lower())

# Se carga el corpus
# WORDS = Counter(words(open('Corpus/big2.txt', encoding="utf8").read()))
# WORDS = Counter(words(open('../wikiOutXML.txt', encoding="utf8").read()))
WORDS = sorted(set(ces_esp.words()))
#WORDS = "Cancion cancion cancion cancon toocoo lalal"
# WORDS = Counter(words(open('manual/example_1.txt', encoding="utf8").read()))

def P(word, N=sum(WORDS.values())):
    "Probabilidad de la parabra `word`."
    return WORDS[word] / N

def correction(word):
    "Correccion mas probable para la palabra word."
    return max(candidates(word), key=P)

def candidates(word):
    "Generador de posibles correcciones para word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or known(edits3(word)) or [word])

def known(words):
    "Subconjunto de `words` que aparecen en el diccionario de WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "Todas las ediciones de distancia uno para `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "Todas las ediciones de distancia dos para `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def edits3(word):
    "Todas las ediciones de distancia tres para `word`."
    return (e3 for e2 in edits2(word) for e3 in edits1(e2))

#Deberia devolver "cancion"
fix = correction('canqiom')
print(fix)


# sentence = "Canciom es me codige"   #Lets assume this is your sentence.
# ejemplo = open('OCRoutput/example_1.tif.txt').read()
# print(ejemplo)
# formatted_sentence = ''
# for i  in ejemplo.split():
#     corrected_word = correction(i)
#     formatted_sentence += ' '+(corrected_word)
# print(formatted_sentence)