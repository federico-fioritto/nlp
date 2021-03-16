from nltk import word_tokenize, sent_tokenize
from nltk.lm import MLE
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import cess_esp
# import dill as pickle
import pickle
from nltk.corpus import PlaintextCorpusReader
from functools import reduce
import os
import pdb
import kenlm
from nltk import bigrams, trigrams
from collections import Counter, defaultdict
from copy import deepcopy
import requests
import urllib.parse as urlencoder
import asyncio
import json
import sys
import config
# from allennlp.commands.elmo import ElmoEmbedder
# import h5py
import numpy as np
# from scipy import special as sp
warmed = False

# Para usar el corpus grande de wikipedia (hay que descargarlo del drive)
# corpus = PlaintextCorpusReader('./', 'wikiCorpus.txt')

CORPUS_DIR = './docs/corpus/'

corpus = 'Hola que tal tu cómo estas, dime si eres feliz. Porque que yo ya me rendí, y por tll esto estoy aquí.'


class LanguageModel:
    def __init__(self, ngram=config.ngram):
        self.lm: None
        self.ngram = ngram
        self.language_models_dir_path = os.path.join(os.path.dirname(__file__), '../language_models/')

    def tokenize_corpus(self, corpus_name):
        # Se tokeniza el corpus por sentencia y luego por palabra. Se pasa cada palabra a minúsculas.

        print('reading corpus')
        reader = PlaintextCorpusReader('./docs/corpus/', corpus_name)
        print ('tokenizo sentencias')
        for sent in reader.sents():
            if self.ngram == 2:
                grams = bigrams(sentence, pad_right=True, pad_left=True)
            elif self.ngram == 3:
                grams = trigrams(sentence, pad_right=True, pad_left=True)
            print('word tokenize')
            words = word_tokenize(sent)
            print('to lower')
            words_lower = map(str.lower, words)
            print('lo hace lista')
            words_lower = list(words_lower)

        return words_lower
        # return [list(map(str.lower, word_tokenize(sent)))
        #         for sent in sent_tokenize(corpus)]

    def create_and_fit_model(self, corpus):
        # Recibe un corpus tokenizado por sentencia y por palabra.
        print('primer paso')
        train_data, padded_sents = padded_everygram_pipeline(
            self.ngram, corpus)

        print('creando modelo')
        # Crea modelo
        model = MLE(self.ngram)

        print('ajustando datos')
        # Ajusta a los datos
        model.fit(train_data, padded_sents)
        print('ajusto')

        return model

    def save_model(self, model, model_name='trained_model.pkl'):
        with open('./language_models/' + model_name, 'wb') as fout:
            pickle.dump(model, fout)

    def load_model(self, model_name='trained_model.pkl'):
        if config.language_model == '1_billion':
            print('cargando modelo de lenguaje...')
            self.lm = kenlm.Model(os.getenv('LOCAL_1_BILLION_PATH'))
            print('modelo de lenguaje cargado\n')

    def to_lower(self, corpus_name):
        f = open(CORPUS_DIR + 'lower_' + corpus_name, "w+")
        with open(CORPUS_DIR + corpus_name, encoding='utf8', errors='ignore') as infile:
            for line in infile:
                f.write(line.lower())
        f.close()

    def create_model(self, corpus_name):
        print('reading corpus')
        reader = PlaintextCorpusReader(CORPUS_DIR, corpus_name)

        print('padded everygram pipeline')
        train_data, vocab = padded_everygram_pipeline(self.ngram, (reader.sents()))

        print('creando modelo')
        # Crea modelo
        model = MLE(self.ngram)

        print('ajustando datos')
        # Ajusta a los datos
        model.fit(train_data, vocab)
        print('ajusto')

        return model

    def get_language_model_correction(self, error_word, prev_words, forw_word, suggestions, context_dir):
        if config.language_model == 'google':
            return self.get_google_correction(error_word, prev_words, forw_word, suggestions, context_dir)
        elif config.language_model == '1_billion':
            return self.get_1_billion_correction(error_word, prev_words, forw_word, suggestions)

    def get_1_billion_correction(self, error_word, prev_words, forw_word, suggestions):
        scored_suggestions = []

        bos = '<s>' in prev_words
        eos = '</s>' in forw_word

        prev_words = [ w for w in prev_words if w != '<s>' ]
        forw_word = [ w for w in prev_words if w != '</s>' ]

        for suggestion in suggestions:
            sentence = ' '.join(prev_words) + ' ' + suggestion['value'] +' '+ ' '.join(forw_word)
            score = self.lm.score(sentence, bos, eos)
            scored_suggestions.append({"value": suggestion['value'], "score": score, "distance": suggestion['distance']})

        if scored_suggestions:
            best_suggestion = max(scored_suggestions, key=lambda elem: elem["score"])["value"]
        else:
            best_suggestion = error_word

        return [best_suggestion, scored_suggestions]

    def get_google_correction(self, error_word, prev_words, forw_word, suggestions, context_dir):

        if len(suggestions) == 0:
            return [error_word, []]

        if not context_dir:
            context_dir = config.context_direction

        texts = []
        scored_suggestions = []

        if (context_dir == "previous"):
            for suggestion in suggestions:
                texts.append(' '.join(prev_words) + ' ' + suggestion['value'])
        elif (context_dir == "forward"):
            for suggestion in suggestions:
                texts.append(suggestion['value'] +' '+ ' '.join(forw_word) )
        elif (context_dir == "middle"):
            for suggestion in suggestions:
                if not forw_word == []:
                    texts.append(' '.join(prev_words) + ' ' + suggestion['value'] +' '+ ' '.join(forw_word))
                else:
                    texts.append(' '.join(prev_words) + ' ' + suggestion['value'])

        freqs = self.nodejs_async_get_google_relative_frequencies(texts)
        for i, freq in enumerate(freqs):
            s = suggestions[i]
            scored_suggestions.append({"value": s['value'], "score": freq, "distance": s['distance']})

        index = freqs.index(max(freqs)) if freqs else None

        if index is not None and scored_suggestions[index]['score']:
            return [suggestions[index]['value'], scored_suggestions]
        else:
            return [error_word, scored_suggestions]

    def get_google_correction_inverted(self, error_word, forward_words, suggestions):
        if len(suggestions) == 0:
            return [error_word, []]

        texts = []
        scored_suggestions = []

        for suggestion in suggestions:
            texts.append(suggestion['value'] +' '+ ' '.join(forward_words) )

        freqs = self.nodejs_async_get_google_relative_frequencies(texts)

        for i, freq in enumerate(freqs):
            s = suggestions[i]
            scored_suggestions.append({"value": s['value'], "score": freq, "distance": s['distance']})

        index = freqs.index(max(freqs)) if freqs else None

        if index is not None and scored_suggestions[index]['score']:
            return [suggestions[index]['value'], scored_suggestions]
        else:
            return [error_word, scored_suggestions]

    def get_google_correction_middle(self, error_word, prev_forward_words, suggestions):
        if len(suggestions) == 0:
            return [error_word, []]

        texts = []
        scored_suggestions = []

        for suggestion in suggestions:
            texts.append(prev_forward_words[0]+' '+suggestion['value'])
            if (len(prev_forward_words)>1):
                texts.append(prev_forward_words[1])

        freqs = self.nodejs_async_get_google_relative_frequencies(texts)

        for i, freq in enumerate(freqs):
            s = suggestions[i]
            scored_suggestions.append({"value": s['value'], "score": freq, "distance": s['distance']})

        index = freqs.index(max(freqs)) if freqs else None

        if index is not None and scored_suggestions[index]['score']:
            return [suggestions[index]['value'], scored_suggestions]
        else:
            return [error_word, scored_suggestions]

    def get_google_relative_frequency(self, text, corpus='spa', nmin=1, nmax=5, topk=100):
        # Retorna la frecuencia relativa del ngrama text
        text = text.replace('\\','\\\\')
        text = urlencoder.quote(text)
        response = requests.get(
            f'https://api.phrasefinder.io/search?corpus={corpus}&query={text}&nmin={nmin}&nmax={nmax}&topk={topk}'
        )
        json_response = response.json()

        if response.status_code != 200:
            return json_response

        total = 0
        for phrase in json_response['phrases']:
            total += phrase['mc']

        return total

    def get_google_relative_frequencies(self, ngrams, corpus='spa', nmin=1, nmax=5, topk=100):
        results = [0] * len(texts)

        for i, ngram in enumerate(ngrams):
            ngram = ngram.replace('\\','\\\\')
            ngram = urlencoder.quote(ngram)
            response = requests.get(f'https://api.phrasefinder.io/search?corpus={corpus}&query={ngram}&nmin={nmin}&nmax={nmax}&topk={topk}')
            json = response.json()
            if 'error' not in json:
                total = 0
                for phrase in json['phrases']:
                    total += phrase['mc']
                results[i] = total
            else:
                print('Phrasefinder error: ', json)

        return results

    def async_get_google_relative_frequencies(self, texts, corpus='spa', nmin=1, nmax=5, topk=100):
        # Retorna las frecuencias relativas de los ngramas de texts, los requests se hacen asíncrónicamente
        semaphore = asyncio.Semaphore(2)

        async def logic(texts):
            async with semaphore:
                def sum_frequecies(json):
                    total = 0
                    for phrase in json['phrases']:
                        total += phrase['mc']
                    return total

                results = [0] * len(texts)
                loop = asyncio.get_event_loop()
                futures = []

                for text in texts:
                    text = text.replace('\\','\\\\')
                    text = urlencoder.quote(text)
                    futures.append(loop.run_in_executor(
                        None,
                        requests.get,
                        f'https://api.phrasefinder.io/search?corpus={corpus}&query={text}&nmin={nmin}&nmax={nmax}&topk={topk}'
                    ))

                for i, response in enumerate(await asyncio.gather(*futures)):
                    json = response.json()
                    if 'error' not in json:
                        results[i] = sum_frequecies(json)
                    else:
                        print('Phrasefinder error: ', json)
                return results

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(logic(texts))

    def nodejs_async_get_google_relative_frequencies(self, texts, corpus='spa', nmin=1, nmax=5, topk=100):
        PARALLEL = config.parallel_phrasefinder_requests
        results = []
        body = list(map(lambda x: {'ngram': x}, texts))

        try:
            responses = requests.post(f'http://localhost:5111/{PARALLEL}', json = body)
        except requests.exceptions.RequestException as e:
            print('ERROR: ¿Está corriendo la aplicación node ubicada')
            print('\ten nlp_project/async_requests con el comando')
            print('\tnode index.js (instalando previamente con npm i)?')
            sys.exit(1)

        responses = responses.json()

        for response in responses:
            response = json.loads(response)
            if 'error' not in response:
                total = 0
                for phrase in response['phrases']:
                    total += phrase['mc']
                results.append(total)
            else:
                print('Phrasefinder error: ', response)

        return results

    def create_model_as_dict(self, corpus_name):
        # USO: dict(model["vale", "la"])['revancha']
        #                 previous_words    word


        # Create a placeholder for model
        # model = defaultdict(lambda: defaultdict(lambda: 0))

        print('leyendo corpus')
        reader = PlaintextCorpusReader(CORPUS_DIR, corpus_name)
        print('leyo corpus')
        train, vocab = padded_everygram_pipeline(self.ngram, reader.sents())
        print('everygram completed')

        model = dict()
        appearences = dict()

        # Cada elemento de list(train) es la lista con todos los ngrama (1,2,3,...) de cada sentencia
        i = 1
        print('inicializando')
        for everygram in train:
            # print('i:', i)
            # i += 1
            # j = 1
            for gram in everygram:
                # print('j:', j)
                j += 1
                if len(gram) == 1:
                    if gram[0] not in appearences:
                        appearences[gram[0]] = 1
                    else:
                        appearences[gram[0]] += 1
                elif len(gram) == 2:
                    if not gram[0] in model:
                        model[gram[0]] = dict()
                    if gram[1] not in model[gram[0]]:
                        model[gram[0]][gram[1]] = 1
                    else:
                        model[gram[0]][gram[1]] += 1
                elif len(gram) == 3:
                    if not (gram[0], gram[1]) in model:
                        model[(gram[0], gram[1])] = dict()
                    if gram[2] not in model[(gram[0], gram[1])]:
                        model[(gram[0], gram[1])][gram[2]] = 1
                    else:
                        model[(gram[0], gram[1])][gram[2]] += 1

        # print('conto todo', model)
        for w1 in model:
            # print('sumando', w1)
            total_count = float(sum(model[w1].values()))
            for w3 in model[w1]:
                # print('calculando', w3)
                model[w1][w3] /= total_count

        print('paso a probabilidad')

        return appearences, model

    def get_elmo_probability(self, vocabulary, ngram, suggestion, embeddings):
        # SOLO SE PUEDE USAR CON GPU PORQUE ELMO LO REQUIERE
        # ngram es un array con el contexto
        # Rutas hardcodeadas para colab y google drive
        if suggestion not in vocabulary:
            return 0
        if (ngram == [] or ngram == None or ngram == ''):
            ngram = ['</S>'] if config.context_direction == 'forward' else ['<S>']

        WEIGHT_FILE = '/content/drive/My Drive/TESIS/spanishElmo/weights.hdf5'
        OPTIONS_FILE = '/content/drive/My Drive/TESIS/spanishElmo/options.json'
        VOCABULARY_FILE = '/content/drive/My Drive/TESIS/spanishElmo/vocab.txt'

        # Load weights to AllenNLP embedder (1)
        elmo = ElmoEmbedder(cuda_device=0, weight_file=WEIGHT_FILE, options_file=OPTIONS_FILE)

        # Load softmax layer weights (2)
        with h5py.File(WEIGHT_FILE, 'r', libver='latest', swmr=True) as fin:
            softmax = fin['softmax/W'][:, :].transpose()


        if (not warmed):
            self.warm_up(elmo)

        # Get the embeddings (use embed_sentences method if more than one)
        str_ngram = ', '.join(ngram)
        if (str_ngram not in embeddings):
            embedded = list(elmo.embed_sentence(ngram))
            embeddings[str_ngram] = embedded
        else:
            embedded = embeddings[str_ngram]

        # Get the 2nd layer embedding of the final token, for the forward LM or previous context (first 512 entries)
        # last 512 are from backwards LM or forward context
        if (config.context_direction == 'previous'):
            embedding = embedded[2][-1][:512]
        elif (config.context_direction == 'forward'):
            embedding = embedded[2][-1][512:]
        else:
            embedding = embedded[2][-1][:512]

        # Multiply forward embedding by softmax layer, to distribute probability along the vocabulary
        log_probs = np.matmul(embedding, softmax)

        # Apply softmax function (8)
        probs = sp.softmax(log_probs)

        sentence_probability = probs[vocabulary.index(suggestion)]
        return sentence_probability

    def warm_up(self, elmo):
         # Warm up embedder (according to Amrami & Goldberg, running a few sentences in elmo will set it to a better state than initial zeros) (4)
        warm_up = "En efecto , rematado ya su juicio , vino a dar en el más " \
                "extraño pensamiento que jamás dio loco en el mundo ; y fue que " \
                "le pareció convenible y necesario , así para el aumento de su honra " \
                "como para el servicio de su república , hacerse caballero andante , e irse " \
                "por todo el mundo con sus armas y caballo a buscar las " \
                "aventuras y a ejercitarse en todo aquello que él había leído que " \
                "los caballeros andantes se ejercitaban , deshaciendo todo género de agravio , y poniéndose " \
                "en ocasiones y peligros donde , acabándolos , cobrase eterno nombre y fama .".split()
        for _ in range(3):
            _ = elmo.embed_sentence(warm_up)
        warmed = True
        return

    def get_elmo_correction(self, error_word, context, suggestions, vocabulary):
        if not vocabulary:
            vocabulary = []
            with open(os.path.dirname(os.path.realpath(__file__)) + '/../docs/vocabularies/elmo_vocabulary.txt', encoding='utf-8') as fin:
                for line in fin:
                    vocabulary.append(line.strip())
        if len(suggestions) == 0:
            return [error_word, []]

        texts = []
        scored_suggestions = []

        freqs = []
        embeddings = {}
        for suggestion in suggestions:
            freqs.append(self.get_elmo_probability(vocabulary, context, suggestion['value'], embeddings))

        for i, freq in enumerate(freqs):
            s = suggestions[i]
            scored_suggestions.append({"value": s['value'], "score": freq, "distance": s['distance']})

        index = freqs.index(max(freqs)) if freqs else None

        if index is not None and scored_suggestions[index]['score']:
            return [suggestions[index]['value'], scored_suggestions]
        else:
            return [error_word, scored_suggestions]

    def get_correction(self, error_word, context, prev_words, forw_words, suggestions, vocabulary,context_dir):
        if (config.language_model ==  'google'):
            return self.get_google_correction(error_word, prev_words, forw_words, suggestions, context_dir)
        elif (config.language_model ==  'elmo'):
            return self.get_elmo_correction(error_word, context, suggestions, vocabulary)
