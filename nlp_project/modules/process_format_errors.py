
from .postprocessor import Postprocessor
from .language_model import LanguageModel
# from modules.language_model import LanguageModel
from copy import deepcopy
import re
import config


class ProcessFormatError:
    def __init__(self, post, lm):
        self.post = post
        self.lm = lm

    def correct_split_word_by_newline(self,text, proccess_split_word, language_model):
        print('corrigiendo palabras separadas por salto de lineas...')
        tokens_list = list(deepcopy(self.post.tokenize_text(text)))
        sent_list = list(deepcopy(self.post.tokenize_by_sent(text)))

        avoid_next_word = False
        vocabulary = self.post.sym_spell._words

        result = { "tokens": []}

        is_new_line = False
        nr_fixed_words = 0
        len_sents = len(sent_list[0])
        index_sents = 0
        for i, word in enumerate(tokens_list):
            if (not avoid_next_word):
                if self.post.have_errors(str.lower(word), vocabulary, tokens_list, i):
                    # word puede ser la primera parte de la palabra dividida
                    if (word[-1] == "-"):
                        new_word = word.rstrip('-')+tokens_list[i+1]
                        nl_word = word + "\n"+tokens_list[i+1]
                        #Busco que sea un salto de linea a partir de la ultima sentencia explorada

                        for y in range(index_sents,len_sents):

                            # Busco si la palabra es dividida por uno o varios saltos de linea
                            pattern = ".*"+re.escape(word)+"\\n+"+re.escape(tokens_list[i+1])+".*"
                            if (bool(re.search(pattern, sent_list[0][y].lower(), re.IGNORECASE))):
                                index_sents = y
                                # is_new_line indica que se encontró un salto de linea entre las dos partes
                                is_new_line = True
                                break

                        if is_new_line and not self.post.have_errors(str.lower(new_word), vocabulary, tokens_list, i):
                            correct_word= new_word + "\n" if proccess_split_word == "join" else "//||"+nl_word+"||//"
                            result["tokens"].append({"value": word, "isError": True,"isFirstPart": True,"isSecondPart": False, "correction": correct_word})
                            #solo se utiliza el la segunda parte de la palabra para hacer la sustitucion
                            result["tokens"].append({"value": tokens_list[i+1], "isError": True,"isFirstPart": False,"isSecondPart": True, "correction": correct_word})
                            avoid_next_word = True
                            nr_fixed_words = nr_fixed_words +1
                        else:
                            if is_new_line:
                                # Debo buscar una correccion
                                contexts = self.post.get_contexts(tokens_list, i, vocabulary)
                                candidates = self.post.find_correction_candidates(new_word)

                                correction_and_parameters = self.post.get_correction_word(new_word, contexts, language_model, candidates)

                                corrected_word = correction_and_parameters["corrected_word"]
                                prev_words = correction_and_parameters["previous_words"]
                                forw_words = correction_and_parameters["forward_words"]
                                scored_suggestions = correction_and_parameters["scored_suggestions"]

                                if new_word != corrected_word:
                                    len_first_word = len(word)
                                    nl_word_correction = corrected_word[:len_first_word] + '-\n' + corrected_word[len_first_word:]
                                    correct_word= corrected_word + "\n" if proccess_split_word == "join" else "//||"+nl_word_correction+"//||"
                                    result["tokens"].append({"value": word, "isError": True,"isFirstPart": True,"isSecondPart": False, "correction": correct_word})

                                    #solo se utiliza el la segunda parte de la palabra para hacer la sustitucion
                                    result["tokens"].append({"value": tokens_list[i+1], "isError": True,"isFirstPart": False,"isSecondPart": True, "correction": correct_word})
                                    avoid_next_word = True
                                    nr_fixed_words = nr_fixed_words +1
                                else:
                                    result["tokens"].append({"value": word, "isError": True,"isFirstPart": None,"isSecondPart": None,"correction": word})
                            else:
                                result["tokens"].append({"value": word, "isError": True,"isFirstPart": None,"isSecondPart": None,"correction": word})
                        is_new_line = False
                    else:
                        result["tokens"].append({"value": word, "isError": True,"isFirstPart": None,"isSecondPart": None,"correction": word})
                elif word not in ['<s>', '</s>']:
                    result["tokens"].append({"value": word, "isError": False,"isFirstPart": None,"isSecondPart": None,"correction": word})
            else:
                avoid_next_word = False
        print('procesamiento palabras separadas por salto de lineas finalizado. Cantidad palabras corregidas: ' + str(nr_fixed_words) + '\n')
        return result



    def correct_split_word(self,text):
        tokens_list = list(deepcopy(self.post.tokenize_text(text)))
        sent_list = list(deepcopy(self.post.tokenize_by_sent(text)))

        avoid_n_word = 0
        vocabulary = self.post.sym_spell._words

        result = { "tokens": []}
        nr_fixed_words = 0
        len_sents = len(sent_list[0])
        len_token = len(tokens_list)
        index_sents = 0
        for i, word in enumerate(tokens_list):

            if (not avoid_n_word>0 ):

                if self.post.have_errors(word, vocabulary, tokens_list, i):

                    #Se revisa si los dos tokens erroneos forman una palabra correcta
                    if ((len_token >= i+1) and self.post.have_errors(tokens_list[i+1], vocabulary, tokens_list, i+1)):
                        new_word = word + tokens_list[i+1]
                        is_correct_word = not self.post.have_errors(new_word, vocabulary, tokens_list, i)

                        #Se chequea si los tokens contienen un salto de linea
                        index_sents, has_new_line = self.is_split_by_new_line(index_sents, i, text, 2)

                        if (not has_new_line or config.correct_split_word == "any_line"):

                            if (is_correct_word):
                                if (has_new_line):
                                    new_word = new_word + "\n"
                                result["tokens"].append({"value": word, "isError": True,"wordParts": 2,"isLastPart": None, "correction": new_word})
                                #solo se utiliza el la segunda parte de la palabra para hacer la sustitucion
                                result["tokens"].append({"value": tokens_list[i+1], "isError": True,"wordParts": 2,"isLastPart": True, "correction": new_word})
                                avoid_n_word = 1
                                nr_fixed_words = nr_fixed_words +1

                            else:
                                if ((len_token >= i+2) and self.post.have_errors(tokens_list[i+2], vocabulary, tokens_list, i+2)):

                                    new_word_2 = new_word + tokens_list[i+2]
                                    is_correct_word_v2 = not self.post.have_errors(new_word_2, vocabulary, tokens_list, i)

                                    #Se chequea si los tokens contienen un salto de linea
                                    index_sents, has_new_line = self.is_split_by_new_line(index_sents, i, text, 3)

                                    if (not has_new_line or config.correct_split_word == "any_line"):

                                        if (is_correct_word_v2):
                                            result["tokens"].append({"value": word, "isError": True,"wordParts": 3,"isLastPart": None, "correction": new_word_2})
                                            result["tokens"].append({"value": tokens_list[i+1], "isError": True,"wordParts": 3,"isLastPart": None, "correction": new_word_2})
                                            result["tokens"].append({"value": tokens_list[i+2], "isError": True,"wordParts": 3,"isLastPart": True, "correction": new_word_2})
                                            avoid_n_word = 2
                                            nr_fixed_words = nr_fixed_words +1
                                        else:
                                            result["tokens"].append({"value": word, "isError": True,"wordParts": 0,"isLastPart": None,"correction": word})
                                    else:
                                        result["tokens"].append({"value": word, "isError": True,"wordParts": 0,"isLastPart": None,"correction": word})
                                else:
                                    result["tokens"].append({"value": word, "isError": True,"wordParts": 0,"isLastPart": None,"correction": word})

                        else:
                            result["tokens"].append({"value": word, "isError": True,"wordParts": 0,"isLastPart": None,"correction": word})
                    else:
                        result["tokens"].append({"value": word, "isError": True,"wordParts": 0,"isLastPart": None,"correction": word})

                elif word not in ['<s>', '</s>']:
                    result["tokens"].append({"value": word, "isError": False,"wordParts": 0,"isLastPart": None,"correction": word})
            else:
                avoid_n_word =  avoid_n_word-1
        # print("Cant. palabras corregidas: "+ str(nr_fixed_words))
        # print(result)
        return result


    def is_split_by_new_line(self,index_sents,token_index, text, n_gram):
        tokens_list = list(deepcopy(self.post.tokenize_text(text)))
        sent_list = list(deepcopy(self.post.tokenize_by_sent(text)))
        len_sents = len(sent_list[0])

        has_new_line = False
        for y in range(index_sents,len_sents):

            # Busco si la palabra es dividida por uno o varios saltos de linea
            pattern = ".*"+re.escape(tokens_list[token_index])+"\\n+"+re.escape(tokens_list[token_index+1])+".*"
            if (bool(re.search(pattern, sent_list[0][y].lower()))):
                index_sents = y
                # has_new_line indica que se encontró un salto de linea entre las dos partes
                has_new_line = True
                break
        if (n_gram>2 and not has_new_line):

            for y in range(index_sents,len_sents):

                # Busco si la palabra es dividida por uno o varios saltos de linea
                pattern = ".*"+re.escape(tokens_list[token_index+1])+"\\n+"+re.escape(tokens_list[token_index+2])+".*"
                if (bool(re.search(pattern, sent_list[0][y].lower()))):
                    index_sents = y
                    # has_new_line indica que se encontró un salto de linea entre las dos partes
                    has_new_line = True
                    break


        return index_sents, has_new_line


