import os
from symspellpy.symspellpy import SymSpell, Verbosity


class ErrorDetector:

    def __init__(self, sym_spell):
        self.sym_spell = sym_spell

    def detect_errors(self, dictionary, tokenized_text):
        error_words = []
        for token in tokenized_text:
            if token not in dictionary and token not in ['<s>', '</s>']:
                error_words.append(token)
        return error_words

    def find_correction_candidates(self, dictionary, errors, max_edit_distance_lookup):
        corrections = []
        suggestion_verbosity = Verbosity.CLOSEST
        for error_word in errors:
            suggestions = self.sym_spell.lookup(
                error_word, suggestion_verbosity, max_edit_distance_lookup)
            # Si no encontramos candidatos meto la misma.
            if(suggestions):
                corrections.append(suggestions[0])
            else:
                corrections.append(error_word)
        return corrections

    # display suggestion term, term frequency, and edit distance
    # print(suggestions)
    # for suggestion in suggestions:
    #     print("{}, {}, {}".format(suggestion.term, suggestion.distance,
    #                               suggestion.count))
