from nltk import word_tokenize, sent_tokenize, edit_distance
from nltk.lm.preprocessing import padded_everygram_pipeline
from collections import Counter
from symspellpy.symspellpy import SymSpell
import codecs


class Preprocessor:
    def __init__(self):

        # CONSTANTES
        self.max_edit_distance_dictionary = 2
        self.prefix_length = 7
        self.term_index = 0
        self.count_index = 1
        self.vocabulary_dir_path = './docs/vocabularies/'

    def build_sysmpell(self):
        return SymSpell(
            self.max_edit_distance_dictionary, self.prefix_length)

    def save_current_vocabulary_to_file(self, vocabulary, filename):
        import csv
        filename = filename + '.csv' if '.csv' not in filename else filename
        with open(self.vocabulary_dir_path + filename, 'w') as f:
            for key in vocabulary.keys():
                f.write("%s %s\n" % (key, vocabulary[key]))

    def generate_vocabulary(self, corpus_path):
        sym_spell = self.build_sysmpell()
        sym_spell.create_dictionary(corpus_path)

        self.save_current_vocabulary_to_file(
            sym_spell.words, corpus_path.split('/')[-1])

    def print_vocabulary(self, sym_spell):
        for key, count in sym_spell.words.items():
            print("{} {}".format(key, count))

    def load_vocabulary(self, vocabulary_name):
        sym_spell = self.build_sysmpell()
        if not sym_spell.load_dictionary(self.vocabulary_dir_path + vocabulary_name, self.term_index, self.count_index):
            print("Dictionary file not found")
            return
        return sym_spell

    def remove_less_freq_than(self, n, vocabulary_name):
        sym_spell = self.load_vocabulary(vocabulary_name)

        keeped_words = {}
        removed_words = {}

        for key, count in sym_spell.words.items():
            if count < n:
                removed_words[key] = count
            else:
                keeped_words[key] = count

        self.save_current_vocabulary_to_file(
            keeped_words, 'keeped_' + str(n) + '_' + vocabulary_name)

        self.save_current_vocabulary_to_file(
            removed_words, 'removed_' + str(n) + '_' + vocabulary_name)

    def is_alpha(self, key, count):
        return key.isalpha()
    
    def more_than_4(self, key, count):
        return count > 4

    def filter(self, vocabulary_name, functions):
        sym_spell = self.load_vocabulary(vocabulary_name)

        keeped_words = {}
        removed_words = {}

        for key, count in sym_spell.words.items():
            keep = True
            for fun in functions:
                if not fun(key, count):
                    keep = False
                    break
            if (keep):
                keeped_words[key] = count
            else:
                removed_words[key] = count
            
        return (keeped_words, removed_words) 

    def addWordIfNotExists(self, word, vocabulary):
        with open(self.vocabulary_dir_path + vocabulary, "a") as f:
            f.write("\n" + word +  " 10")
        self.keepUniquesWords(vocabulary)
    
    def keepUniquesWords(self, vocabulary):
        import os
        os.system('sort ' + self.vocabulary_dir_path + vocabulary + ' | uniq -u > ' + self.vocabulary_dir_path + vocabulary + '.temp')
        os.system('sort ' + self.vocabulary_dir_path + vocabulary + ' | uniq -d >> ' + self.vocabulary_dir_path + vocabulary + '.temp')
        os.system('mv ' + self.vocabulary_dir_path + vocabulary + '.temp' + ' ' + self.vocabulary_dir_path + vocabulary)