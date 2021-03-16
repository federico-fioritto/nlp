from modules.language_model import LanguageModel
import os.path

if (os.path.exists('./language_models/wiki_3gram_as_dict.pkl')):
  print('finished')
  exit()


lm = LanguageModel(3)
print('a crear')
# lm.to_lower('wikiCorpus.txt')
appearences, model = lm.create_model_as_dict('lower_wikiCorpus.txt')
print('creó', model)
lm.save_model(model, 'wiki_3gram_as_dict.pkl')
print('guardó model')
print('guarar appearences')
lm.save_model(appearences, 'appearences_wiki_3gram_as_dict.pkl')
print('guardó')


# d = dict(model["vale", "la"])['revancha']
# print(d)

