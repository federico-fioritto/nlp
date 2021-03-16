from difflib import SequenceMatcher
import sys


one = open(sys.argv[1], errors='ignore').read()
two = open(sys.argv[2], errors='ignore').read()

print('ratio')
print(str(SequenceMatcher(None, one, two).ratio()))


a = set(one.split())
b = set(two.split())
c = a.intersection(b)
print('jaccard')
print(float(len(c)) / (len(a) + len(b) - len(c)))