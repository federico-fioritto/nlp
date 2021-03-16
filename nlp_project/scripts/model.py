from nltk import word_tokenize, sent_tokenize
from nltk.lm import MLE
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import cess_esp
import dill as pickle
from nltk.corpus import PlaintextCorpusReader

# Para usar el corpus grande de wikipedia (hay que descargarlo del drive)
# corpus = PlaintextCorpusReader('./', 'wikiCorpus.txt')

NGRAM = 3

corpus = 'Hola que tal tu cómo estas, dime si eres feliz. Porque qsue yo ya me rendí, y por esto estoy aquí.'


def tokenize_corpus(corpus):
    # Se tokeniza el corpus por sentencia y luego por palabra. Se pasa cada palabra a minúsculas.
    return [list(map(str.lower, word_tokenize(sent)))
            for sent in sent_tokenize(corpus)]


def create_and_fit_model(corpus):
    # Recibe un corpus tokenizado por sentencia y por palabra.
    train_data, padded_sents = padded_everygram_pipeline(
        NGRAM, corpus)

    # Crea modelo
    model = MLE(NGRAM)

    # Ajusta a los datos
    model.fit(train_data, padded_sents)

    return model


def save_model(model, model_name='trained_model.pkl'):
    with open('trained_model.pkl', 'wb') as fout:
        pickle.dump(model, fout)


def load_model(model_name='trained_model.pkl'):
    with open('trained_model.pkl', 'rb') as fin:
        return pickle.load(fin)


# tokenized_corpus = tokenize_corpus(corpus)
model = create_and_fit_model(cess_esp.sents())
save_model(model, 'trained_model.pkl')
model_loaded = load_model('trained_model.pkl')


print(model_loaded.score('central', ['una']))
print(model_loaded.score('tal', ['que']))

print(model_loaded.logscore('central', ['una']))
print(model_loaded.logscore('tal', ['que']))

# print(model.score('tal', ['Hola que'])):
#   probabilidad de que aparezca 'tal' dado que ocurrió un 'Hola que' anteriormente
