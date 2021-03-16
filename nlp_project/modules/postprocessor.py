from modules.preprocessor import Preprocessor
from nltk import word_tokenize, sent_tokenize, edit_distance
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.corpus import cess_esp
from nltk.util import everygrams, pad_sequence
import pickle
from difflib import SequenceMatcher
import time
from symspellpy.symspellpy import SymSpell, Verbosity
import string
from copy import deepcopy
from nltk.corpus import stopwords
import os
import re
import helpers.file as fh
import config
import operator
import itertools as iter

NGRAM = config.ngram

class Postprocessor:
    def __init__(self):
        self.sym_spell = None

        # CONSTANTES
        self.max_edit_distance_dictionary = config.max_edit_distance_dictionary
        self.prefix_length = 7
        self.term_index = 0
        self.count_index = 1
        self.dir_path_vocabulary = os.path.join(os.path.dirname(__file__), '../docs/vocabularies/')
        self.dir_path_output = os.path.join(os.path.dirname(__file__), '../docs/outputs/')
        self.suggestion_verbosity = config.suggestion_verbosity

    def build_symspell(self):
        self.sym_spell = SymSpell(
            self.max_edit_distance_dictionary,
            self.prefix_length
        )

    def save_sysmspell(self, filename):
        if not self.sym_spell:
            raise ValueError('Symspell not created')

        print('guardando symspell...')
        self.sym_spell.save_pickle(self.dir_path_vocabulary + filename)
        print('symspell guardado\n')

    def load_vocabulary(self, vocabulary_name):
        if not self.sym_spell:
            self.build_symspell()

        if not vocabulary_name:
            raise ValueError('Vocabulary is required')

        print('cargando vocabulario', config.vocabulary)

        extension = os.path.splitext(vocabulary_name)[1].lower()

        if extension == '.txt':
            if not self.sym_spell.load_dictionary(
                self.dir_path_vocabulary + vocabulary_name,
                self.term_index, self.count_index,
                encoding='utf8'
            ):
                raise ValueError('Dictionary file not found')
        elif extension == '.pkl':
            if not self.sym_spell.load_pickle(self.dir_path_vocabulary + vocabulary_name):
                raise ValueError('Dictionary file not found')
        else:
            raise ValueError('Unsupported file not found')

        print('vocabulario cargado\n')

    def tokenize_text(self, text):
        tokenized_text = [list(word_tokenize(sent))
                          for sent in sent_tokenize(text)]

        train_data, padded_sents = padded_everygram_pipeline(
            NGRAM, tokenized_text)
        return padded_sents


    def tokenize_by_sent(self, text):
        # Se tokeniza el text por sentencia y luego por palabra. Se pasa cada palabra a minúsculas.
        tokenized_text = [list(map(str.lower, sent_tokenize(text)))]
        return tokenized_text


    def have_errors(self, word, vocabulary, tokens, i):
        def is_non_alphanumeric(s):
            return all(not c.isalnum() for c in s)

        def is_first_word_paragraph(tokens, i):
            return i != 0 and tokens[i-1] == '<s>'

        def has_format_like_date(text):
            pattern = re.compile("^(\d+)$|^((\w+\/){2})\w+$")
            return bool(pattern.match(text))

        def have_ortography_error(word):
            return word not in ['<s>', '</s>'] and (not is_non_alphanumeric(word) and not word.isnumeric()) and word not in vocabulary

        word_lower = str.lower(word)

        if ("//||" in word or "||//" in word):
            return False
        elif config.correct_upper_case_first_letter and config.correct_upper_case:
            return have_ortography_error(word_lower) and not has_format_like_date(word_lower)

        elif config.correct_upper_case_first_letter and not config.correct_upper_case:
            return have_ortography_error(word_lower) and not( word.isupper() and not any(char.isdigit() for char in word)) and not has_format_like_date(word_lower)

        elif not config.correct_upper_case_first_letter and config.correct_upper_case:
            return have_ortography_error(word_lower) and \
                (not word[0].isupper() or is_first_word_paragraph(tokens, i)) and not has_format_like_date(word_lower)

        else:
            return have_ortography_error(word_lower) and \
                   (not word.isupper() and not any(char.isdigit() for char in word)) and \
                (not word[0].isupper() or is_first_word_paragraph(tokens, i)) and not has_format_like_date(word_lower)

    def find_correction_candidates(self, error_word):
        error_word_low = str.lower(error_word)
        max_edit_distance_lookup = config.edit_distance_conf(len(error_word_low))

        suggestions = self.sym_spell.lookup(error_word_low, self.suggestion_verbosity,
                                            max_edit_distance_lookup)
        return [ { "value": s.term, "distance": s.distance } for s in suggestions ]

    def process_with_edit_distance_and_google_language_model(self, text, language_model):
        # result = {
        #     "corrected_text": 'texto corregido',
        #     "tokens": [
        #         {"value": "Bien", "isError": False},
        #         {"value": "Mal", "isError": True, "correction": "Malito", "suggestions": []}
        #     ]
        # }

        if not self.sym_spell:
            raise ValueError('SymSpell not initialized')

        print('procesando con edit distance y modelo de lenguage de ' + config.language_model)

        result = { "tokens": [], "corrected_text": "" }
        vocabulary = self.sym_spell._words
        tokenized_text = list(deepcopy(self.tokenize_text(text)))
        # print('text tokenized:', tokenized_text)
        tokenized_corrected_text = list(deepcopy(self.tokenize_text(text)))

        for i, word in enumerate(tokenized_text):

            if self.have_errors(word, vocabulary, tokenized_text, i):
                # Busco candidatos cercanos para corregir la palabra errónea
                candidates = self.find_correction_candidates(word)

                # Obtengo las palabras previas a la palabra errónea (contexto) sin tomar en cuenta símbolos de inicio y fin de sentencia
                previous_words = [ w for w in tokenized_corrected_text[i-NGRAM+1 : i] if w not in ['<s>', '</s>'] ]

                # Mientras no se encuentra candidato se sigue buscando con un contexto cada vez más pequeño.
                # Nota: Al buscar de esta manera se da prioridad a ngramas de mayor tamaño.
                corrected_word = word
                while corrected_word == word:
                    # print('error: ' + word)
                    # print('contexto: ' + str(previous_words))
                    corrected_word, scored_suggestions = language_model.get_language_model_correction(word, previous_words, candidates, config.context_direction)

                    # Si ya se probó con todo contexto posible (incluso unigramas) o se encontró candidato, salgo del loop.
                    if not previous_words or corrected_word != word:
                        break
                    previous_words.pop(0)

                # Actualizo el texto tokenizado para tener cuenta las correcciones
                tokenized_corrected_text[i] = corrected_word

                result["corrected_text"] += corrected_word + ' '
                result["tokens"].append({
                    "previous_words": previous_words,
                    "value": word,
                    "isError": True,
                    "suggestions": scored_suggestions,
                    "correction": corrected_word
                })
            elif word not in ['<s>', '</s>']:
                result["corrected_text"] += word + ' '
                result["tokens"].append({"value": word, "isError": False, "correction": word})

            if i and i%20==0:
                result["corrected_text"] += '\n'

        print('procesamiento finalizado\n')
        return result



    def clean_context(self, context, vocabulary, iterate_backwards=False):
        def normalize(word):
            leave_only_alphanum = lambda word: re.sub("[\W\d_]+", '', word)

            return leave_only_alphanum(word).lower()

        new_context = []
        if iterate_backwards: context.reverse()
        for word in context:
            if config.language_model == '1_billion' and word in ['<s>', '</s>']:
                new_context.append(word)
            elif (word in vocabulary or \
                word.upper() in vocabulary or \
                word.lower() in vocabulary or \
                word.capitalize() in vocabulary):
                new_context.append(word) if word not in ['<s>', '</s>'] else new_context.append(word.upper())
            elif normalize(word) in vocabulary:
                new_context.append(normalize(word))
            else:
                break

        if iterate_backwards: new_context.reverse()

        return new_context

    def get_contexts(self, tokenized_corrected_text, i, vocabulary):
        contexts = {}
        
        if (config.context_direction in "previous,all"):
            # Obtengo las palabras previas a la palabra errónea (contexto) sin tomar en cuenta símbolos de inicio y fin de sentencia
            if config.language_model == '1_billion':
                previous_words = [ w for w in tokenized_corrected_text[i-NGRAM+1 : i] ]
            else:
                previous_words = [ w for w in tokenized_corrected_text[i-NGRAM+1 : i] if w not in ['<s>', '</s>'] ]

            previous_words = self.clean_context(previous_words, vocabulary, iterate_backwards=True)

            contexts["previous_words"] = previous_words

        if (config.context_direction in "forward,all"):
            # Obtengo las palabras siguientes a la palabra errónea (contexto) sin tomar en cuenta símbolos de inicio y fin de sentencia
            if config.language_model == '1_billion':
                forward_words = [ w for w in tokenized_corrected_text[i+1:i+NGRAM] ]
            else:
                forward_words = [ w for w in tokenized_corrected_text[i+1:i+NGRAM] if w not in ['<s>', '</s>'] ]

            forward_words = self.clean_context(forward_words, vocabulary)

            contexts["forward_words"] = forward_words

        if (config.context_direction in "middle,all"):
            # Obtengo la palabras previa y posterior a la palabra errónea (contexto) sin tomar en cuenta símbolos de inicio y fin de sentencia
            if config.language_model == '1_billion':
                middle_previous_words = [ w for w in tokenized_corrected_text[i-(NGRAM)//2 : i] ]
                middle_forward_words = [ w for w in tokenized_corrected_text[i+1 : i+(NGRAM)//2+1] ]
            else:
                middle_previous_words = [ w for w in tokenized_corrected_text[i-(NGRAM)//2 : i] if w not in ['<s>', '</s>'] ]
                middle_forward_words = [ w for w in tokenized_corrected_text[i+1 : i+(NGRAM)//2+1] if w not in ['<s>', '</s>'] ]

            middle_previous_words = self.clean_context(middle_previous_words, vocabulary, iterate_backwards=True)
            middle_forward_words = self.clean_context(middle_forward_words, vocabulary)

            contexts["middle_previous_words"] = middle_previous_words
            contexts["middle_forward_words"] = middle_forward_words

        return contexts

    def get_correction_word(self, word, contexts, language_model, candidates):
        previous_words = []
        forward_words = []
        middle_previous_words = []
        middle_forward_words = []
        scored_suggestions_prev = []
        scored_suggestions_middle = []
        scored_suggestions_forw = []

        prev_win = 0
        middle_win = 0
        forw_win = 0
        prev_midd_win = 0
        prev_forw_win = 0
        midd_forw_win = 0
        equal_win = 0

        if "previous_words" in contexts:
            previous_words = contexts["previous_words"]

            # print("Contexto previo:")
            # print(previous_words)
            # Mientras no se encuentra candidato se sigue buscando con un contexto cada vez más pequeño.
            # Nota: Al buscar de esta manera se da prioridad a ngramas de mayor tamaño.
            scored_suggestions_prev = []
            corrected_word_prev = word
            while corrected_word_prev == word:
                # print('error: ' + word)
                # print('contexto: ' + str(previous_words))
                corrected_word_prev, scored_suggestions_prev = language_model.get_language_model_correction(word, previous_words, [], candidates, "previous")
                # print("scored_suggestions_prev")
                # print(scored_suggestions_prev)

                # Si ya se probó con todo contexto posible (incluso unigramas) o se encontró candidato, salgo del loop.
                if not previous_words or corrected_word_prev != word:
                    break
                previous_words.pop(0)

        # Contexto SIGUENTE
        if "forward_words" in contexts:
            # Obtengo las palabras siguientes a la palabra errónea (contexto) sin tomar en cuenta símbolos de inicio y fin de sentencia
            forward_words = contexts["forward_words"]

            # print("Contexto forward:")
            # print(forward_words)

            # Mientras no se encuentra candidato se sigue buscando con un contexto cada vez más pequeño.
            # Nota: Al buscar de esta manera se da prioridad a ngramas de mayor tamaño.
            corrected_word_forw = word
            while corrected_word_forw == word:
                # print('error: ' + word)
                # print('contexto: ' + str(forward_words))
                corrected_word_forw, scored_suggestions_forw = language_model.get_language_model_correction(word,[],forward_words, candidates,"forward")

                # Si ya se probó con t odo contexto posible (incluso unigramas) o se encontró candidato, salgo del loop.
                if not forward_words or corrected_word_forw != word:
                    break
                forward_words.pop()

        #CONTEXTO EN EL MEDIO
        if "middle_previous_words" in contexts:
            # Obtengo la palabras previa y posterior a la palabra errónea (contexto) sin tomar en cuenta símbolos de inicio y fin de sentencia
            
            middle_previous_words = contexts["middle_previous_words"]
            middle_forward_words = contexts["middle_forward_words"]

            # print("Contexto middle:")
            # print(middle_previous_words)
            # print(middle_forward_words)

            # Mientras no se encuentra candidato se sigue buscando con un contexto cada vez más pequeño.
            # Nota: Al buscar de esta manera se da prioridad a ngramas de mayor tamaño.
            corrected_word_middle = word
            while corrected_word_middle == word:
                # print('error: ' + word)
                # print('contexto: ' + str(middle_previous_words + middle_forward_words))
                corrected_word_middle, scored_suggestions_middle = language_model.get_language_model_correction(word, middle_previous_words,middle_forward_words, candidates,"middle")

                # Si ya se probó con t odo contexto posible (incluso unigramas) o se encontró candidato, salgo del loop.
                if not middle_forward_words or corrected_word_middle != word:
                    if not middle_previous_words or corrected_word_middle != word:
                        break

                if middle_forward_words:
                    middle_forward_words.pop()
                else:
                    middle_previous_words.pop()

        corrected_word = word

        len_previous_words = len(previous_words)
        len_forward_words = len(forward_words)
        len_middle_words = len(middle_previous_words) + len(middle_forward_words)
        if len_previous_words > len_forward_words and len_previous_words > len_middle_words:
            # print("Gano Previous word")
            prev_win = prev_win +1
            corrected_word = corrected_word_prev
            scored_suggestions = scored_suggestions_prev
        elif len_forward_words > len_previous_words and len_forward_words > len_middle_words:
            # print("Gano Forward word")
            forw_win = forw_win +1
            corrected_word = corrected_word_forw
            scored_suggestions = scored_suggestions_forw
        elif len_middle_words > len_previous_words and len_middle_words > len_forward_words:
            # print("Gano middle word")
            middle_win = middle_win +1
            corrected_word = corrected_word_middle
            scored_suggestions = scored_suggestions_middle
        elif len_previous_words == len_forward_words and len_previous_words > len_middle_words:
            # print("Gano previous y forward word")
            prev_forw_win= prev_forw_win +1
            corrected_word,scored_suggestions = self.sum_score_and_select_maximun(candidates,word,scored_suggestions_prev,scored_suggestions_forw)
        elif len_previous_words == len_middle_words and len_previous_words > len_forward_words:
            # print("Gano previous y middle word")
            prev_midd_win = prev_midd_win +1
            corrected_word,scored_suggestions = self.sum_score_and_select_maximun(candidates,word,scored_suggestions_prev,scored_suggestions_middle)
        elif len_middle_words == len_forward_words and len_middle_words > len_previous_words:
            # print("Gano middle y forward word")
            midd_forw_win = midd_forw_win +1
            corrected_word,scored_suggestions = self.sum_score_and_select_maximun(candidates,word,scored_suggestions_middle,scored_suggestions_forw)
        else:
            equal_win = equal_win +1
            scored_suggestions = []
            for n in range(0,len(candidates)):
                suggestions = {}
                suggestions["value"] = candidates[n]["value"]
                suggestions["score"] = 0
                #Por si no están inicializados
                if (scored_suggestions_prev != []):
                    suggestions["score"] += scored_suggestions_prev[n]['score']
                if (scored_suggestions_middle != []):
                    suggestions["score"] += scored_suggestions_middle[n]['score']
                if (scored_suggestions_forw != []):
                    scored_suggestions_forw[n]['score']
                # suggestions["score"] = scored_suggestions_prev[n]['score'] + scored_suggestions_middle[n]['score']+ scored_suggestions_forw[n]['score']
                suggestions["distance"] = candidates[n]["distance"]
                scored_suggestions.append(suggestions)
                #Se obtiene el candidato con mayor score
            if not scored_suggestions == []:
                index_corrected_word =max(range(len(scored_suggestions)), key=lambda index: scored_suggestions[index]['score'])
                corrected_word = scored_suggestions[index_corrected_word]["value"]
            else:
                corrected_word = word
        
        return {
            "word": word,
            "corrected_word": corrected_word,
            "previous_words": previous_words,
            "forward_words": forward_words,
            "scored_suggestions": scored_suggestions
        }
        

    def process_with_edit_distance_and_language_model_with_direction(self, text, language_model):
        # result = {
        #     "corrected_text": 'texto corregido',
        #     "tokens": [
        #         {"value": "Bien", "isError": False},
        #         {"value": "Mal", "isError": True, "correction": "Malito", "suggestions": []}
        #     ]
        # }

        if not self.sym_spell:
            raise ValueError('SymSpell not initialized')

        print('procesando con edit distance y modelo de lenguage de ' + config.language_model)

        result = { "tokens": [], "corrected_text": "" }
        vocabulary = self.sym_spell._words
        tokenized_text = list(deepcopy(self.tokenize_text(text)))
        # print('text tokenized:', tokenized_text)
        tokenized_corrected_text = list(deepcopy(self.tokenize_text(text)))


        # print("*******************")
        # for i, word in enumerate(tokenized_text):
        #     if ("//||" in word or "||//" in word):
        #         print(word)
        for i, word in enumerate(tokenized_text):

            # print(self.have_errors(word, vocabulary, tokenized_text, i))
            if self.have_errors(word, vocabulary, tokenized_text, i):
                # Busco candidatos cercanos para corregir la palabra errónea
                candidates = self.find_correction_candidates(word)

                contexts = self.get_contexts(tokenized_corrected_text, i, vocabulary)

                correction_and_parameters = self.get_correction_word(word, contexts, language_model, candidates)

                word = correction_and_parameters["word"]
                corrected_word = correction_and_parameters["corrected_word"]
                previous_words = correction_and_parameters["previous_words"]
                forward_words = correction_and_parameters["forward_words"]
                scored_suggestions = correction_and_parameters["scored_suggestions"]

                # Actualizo el texto tokenizado para tener cuenta las correcciones
                tokenized_corrected_text[i] = corrected_word

                result["corrected_text"] += corrected_word + ' '
                result["tokens"].append({
                    "previous_words": previous_words,
                    "forwards_words": forward_words,
                    "value": word,
                    "isError": True,
                    "suggestions": scored_suggestions,
                    "correction": corrected_word
                })
            elif word not in ['<s>', '</s>']:
                if ("//||" in word or "||//" in word):
                    clean_word = word.replace("//||","").replace("||//","")
                    result["corrected_text"] += clean_word + ' '
                    result["tokens"].append({"value": word, "isError": False, "correction": clean_word})
                else:
                    result["corrected_text"] += word + ' '
                    result["tokens"].append({"value": word, "isError": False, "correction": word})

            if i and i%20==0:
                result["corrected_text"] += '\n'

        print('procesamiento finalizado\n')
        return result

    def sum_score_and_select_maximun(self, candidates, word, score_suggestions_1, score_suggestions_2):
        scored_suggestions = []
        for n in range(0,len(candidates)):
            suggestions = {}
            suggestions["value"] = candidates[n]["value"]
            suggestions["score"] = score_suggestions_1[n]['score'] + score_suggestions_2[n]['score']
            suggestions["distance"] = candidates[n]["distance"]
            scored_suggestions.append(suggestions)
            #Se obtiene el candidato con mayor score
        if not scored_suggestions == []:
            index_corrected_word =max(range(len(scored_suggestions)), key=lambda index: scored_suggestions[index]['score'])
            corrected_word = scored_suggestions[index_corrected_word]["value"]
            return [corrected_word, scored_suggestions]
        else:
            return [word,scored_suggestions]


    def correct_errors_process(self, text, language_model):
        if (config.language_model ==  'google'):
            return self.process_with_edit_distance_and_language_model_with_direction(text, language_model)
        elif (config.language_model ==  'elmo'):
            return self.process_with_elmo(text, language_model)
        elif (config.language_model == '1_billion'):
            return self.process_with_edit_distance_and_language_model_with_direction(text, language_model)

        return self.process_with_edit_distance_and_language_model_with_direction(text, language_model)

    def process_with_elmo(self, text, language_model):
        print('procesando con elmo...')
        print('context direction: ', config.context_direction)
        print()

        # Load vocabulary
        vocabulary = []
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../docs/vocabularies/elmo_vocabulary.txt', encoding='utf-8') as fin:
            for line in fin:
                vocabulary.append(line.strip())

        result = { "tokens": [], "corrected_text": "" }
        tokenized_text = list(deepcopy(self.tokenize_text(text)))
        tokenized_corrected_text = list(deepcopy(self.tokenize_text(text)))

        for i, word in enumerate(tokenized_text):

            if self.have_errors(word, vocabulary, tokenized_text, i):
                # Busco candidatos cercanos para corregir la palabra errónea
                candidates = self.find_correction_candidates(word)

                # Obtengo las palabras previas o siguientes a la palabra errónea (contexto)
                if (config.context_direction == 'previous'):
                    context = [ w for w in tokenized_corrected_text[i-NGRAM+1 : i] ]
                    context = self.clean_context(context, vocabulary, iterate_backwards=True)
                elif (config.context_direction == 'forward'):
                    context = [ w for w in tokenized_corrected_text[i+1:i+NGRAM] ]
                    context = self.clean_context(context, vocabulary)
                else:
                    context = [ w for w in tokenized_corrected_text[i-NGRAM+1 : i] ]
                    context = self.clean_context(context, vocabulary, iterate_backwards=True)



                # Mientras no se encuentra candidato se sigue buscando con un contexto cada vez más pequeño.
                # Nota: Al buscar de esta manera se da prioridad a ngramas de mayor tamaño.
                corrected_word = word
                while corrected_word == word:
                    # print('error: ' + word)
                    # print('contexto: ' + str(context))
                    corrected_word, scored_suggestions = language_model.get_elmo_correction(word, context, candidates, vocabulary)

                    # Si ya se probó con todo contexto posible (incluso unigramas) o se encontró candidato, salgo del loop.
                    if not context or corrected_word != word:
                        break
                    context.pop(0)

                # Actualizo el texto tokenizado para tener cuenta las correcciones
                tokenized_corrected_text[i] = corrected_word

                result["corrected_text"] += corrected_word + ' '
                result["tokens"].append({
                    "value": word,
                    "isError": True,
                    "suggestions": scored_suggestions,
                    "correction": corrected_word
                })

                if (config.context_direction == 'previous'):
                    result["tokens"][-1]["previous_words"] = context
                    result["tokens"][-1]["forwards_words"] = ''
                elif (config.context_direction == 'forward'):
                    result["tokens"][-1]["previous_words"] = ''
                    result["tokens"][-1]["forwards_words"] = context
                else:
                    result["tokens"][-1]["previous_words"] = context
                    result["tokens"][-1]["forwards_words"] = ''

            elif word not in ['<s>', '</s>']:
                result["corrected_text"] += word + ' '
                result["tokens"].append({"value": word, "isError": False, "correction": word})

            if i and i%20==0:
                result["corrected_text"] += '\n'

        print('procesamiento finalizado\n')
        return result


    def process_with_regex(self, text):
        print('procesando con expresiones regulares...')

        text = re.sub(r'\.-', '.', text)

        text = re.sub(r"''", '"', text)

        text = re.sub(r"``", '"', text)

        text = re.sub(r"’’", '"', text)

        #Se suplantan caracteres que dividen tokens por otro que no divide (y no aparece con abby)
        text = re.sub(r"&", '½', text)

        text = re.sub(r"(\w)(\*\*)( |\n)", lambda match_obj: match_obj.group(1) + '-' + match_obj.group(3), text)

        # Remove empty lines
        lines = text.split("\n")
        non_empty_lines = [line for line in lines if line.strip() != ""]

        string_without_empty_lines = ""
        for line in non_empty_lines:
            string_without_empty_lines += line + "\n"

        text = string_without_empty_lines

        print('procesamiento regex finalizado\n')
        return text

    def align_documents(self, source, target):
        os.system('./bleualign.py -s ' + source + ' -t ' + target + '-o ' + source)