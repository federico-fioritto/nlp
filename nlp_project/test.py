from dotenv import load_dotenv
load_dotenv()
# import modules.results_evaluator as results_evaluator
# import re
from modules.postprocessor import Postprocessor
from modules.language_model import LanguageModel
# from modules.process_format_errors import ProcessFormatError
# import helpers.final_text_generator as text_generator
# from modules.process_format_errors import ProcessFormatError
# import helpers.final_text_generator as text_generator
import config
import re

print("Comienza test...")

# f1 = open("docs/outputs/example_1.txt", "r", encoding='utf-8-sig').read()
# f1 = "Saltó por el cand elabro el´poder de ernesto"
# f2 = open("docs/outputs/example_2.txt", "r").read()


def have_errors(word, vocabulary, tokens, i):
    def is_non_alphanumeric(s):
        return all(not c.isalnum() for c in s)

    # def is_first_word_paragraph(tokens, i):
    #     return i != 0 and tokens[i-1] == '<s>'
    def is_first_word_paragraph(tokens, i):
        return True


    def has_format_like_date(text):
        pattern = re.compile("^(\d+)$|^((\w+\/){2})\w+$")
        return bool(pattern.match(text))

    def have_ortography_error(word):
        # print(word)
        # print(1)
        # print(word not in ['<s>', '</s>'])
        # print(2)
        # print(not is_non_alphanumeric(word))
        # print(3)
        # print(not word.isnumeric())
        # print(4)
        # print(word not in vocabulary)
        # print(5)

        return word not in ['<s>', '</s>'] and not is_non_alphanumeric(word) and not word.isnumeric() and word not in vocabulary

    word_lower = str.lower(word)

    if ("//||" in word or "||//" in word):
        print(0)
        return False
    elif config.correct_upper_case_first_letter and config.correct_upper_case:
        print(1)
        return have_ortography_error(word_lower) and not has_format_like_date(word_lower)

    elif config.correct_upper_case_first_letter and not config.correct_upper_case:
        print(2)
        print(have_ortography_error(word_lower))
        print((not word.isupper() and not any(char.isdigit() for char in word)))
        print(not has_format_like_date(word_lower))
        return have_ortography_error(word_lower) and not ( word.isupper() and not any(char.isdigit() for char in word)) and not has_format_like_date(word_lower)

    elif not config.correct_upper_case_first_letter and config.correct_upper_case:
        print(3)
        return have_ortography_error(word_lower) and \
               (not word[0].isupper() or is_first_word_paragraph(tokens, i)) and not has_format_like_date(word_lower)

    else:
        print(4)
        return have_ortography_error(word_lower) and \
               (not word.isupper() and not any(char.isdigit() for char in word)) and \
               (not word[0].isupper() or is_first_word_paragraph(tokens, i)) and not has_format_like_date(word_lower)





    # # print(f)
post = Postprocessor()
post.load_vocabulary(config.vocabulary)
vocabulary = post.sym_spell._words


print()
print("Palabra: E1")
result = have_errors("E1", vocabulary,[], 0)
print("Solucion a E1")
print(result)

print()
print()
# no hay digitos
algo =not (any(char.isdigit() for char in "E1"))
print(algo)
#
# print()
# print("Palabra: E1los")
# result = have_errors("E1los", vocabulary,[], 0)
# print("Solucion a E1los")
# print(result)
#
# print()
# print("Palabra: Esta1121")
# result = have_errors("Esta1121", vocabulary,[], 0)
# print("Solucion a Esta1121")
# print(result)
#
# print()
# print("Palabra: 131pepe")
# result = have_errors("131pepe", vocabulary,[], 0)
# print("Solucion a 131pepe")
# print(result)
#
# print()
# print("Palabra: ER131832049")
# result = have_errors("ER131832049", vocabulary,[], 0)
# print("Solucion a ER131832049")
# print(result)
#
# print()
# print("Palabra: 1318ER32049")
# result = have_errors("1318ER32049", vocabulary,[], 0)
# print("Solucion a 1318ER32049")
# print(result)

    # pfe = ProcessFormatError(post,lm)

    # print("Corrijo ejemplo 1")
    # correccion1 = pfe.correctUnigrams(f1)
    # correccion1 = pfe.correctUnigrams(f13)
    # correccion2 = pfe.correctBigrams(f1)

    # print(correccion2)

    # mejora = text_generator.generate_text_split_words_by_newline(f1, correccion2['tokens'])
