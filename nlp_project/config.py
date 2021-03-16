from symspellpy.symspellpy import Verbosity

# Máxima edit distance calculada para el vocabulario Symspell.
max_edit_distance_dictionary = 6

# Configuración de distancias de edición para buscar en el diccionario según largo del token.
def edc(word_len):
   if word_len <= 3: return 1
   if word_len <= 6: return 2
   if word_len <= 10: return 3
   return 4

edit_distance_conf = edc

# Tipo de búsqueda
# Top: Top suggestion with the highest term frequency of the suggestions of smallest edit distance found.
# Closest: All suggestions of smallest edit distance found, suggestions ordered by term frequency.
# All: All suggestions within maxEditDistance, suggestions ordered by edit distance, then by term frequency.
suggestion_verbosity = Verbosity.CLOSEST

# Vocabulario a usar
# vocabulary = 'vocabulary1.4.pkl'
vocabulary = 'vocabulary1.5.pkl'

# Ngramas a comparar
ngram = 3

# Cantidad de request paralelas a la API de phrasefinder
parallel_phrasefinder_requests = 1000


# Si es true, corrige errores en palabras que todas sus letras estén en mayúscula
# Si es false, ignora errores en palabras escritas en mayúscula
correct_upper_case = False

# Si es true, corrige errores en palabras con la primera letra en mayúscula
# Si es false, ignora errores en palabras con la primera letra en mayúscula sin ser de inicio de oración
correct_upper_case_first_letter = True



# "split" para corregir palabras separadas con salto de linea y guion manteniendo la separacion
# "join"  para corregir palabras separadas con salto de linea y guion eliminando la separacion
#  "not_process" para no procesar palabras separadas con salto de linea y guion
# process_split_word = "not_process"
# process_split_word_by_newline = "join"
process_split_word_by_newline = "split"

# "previous" para contexto anterior,
# "forward" para contexto hacia adelante
# "middle" para contexto hacia adelante
# "all" para ambos
# context_direction = "forward"
# context_direction = "previous"
# context_direction = "middle"
context_direction = "all"


# Qué usamos como modelo de lenguaje?
# ["elmo", "google", "1_billion"]
language_model = 'google'

# "same_line" unicamente junta palabras partidas en el mismo renglon
# "any_line" junta palabras partidas en el mismo renglon y con salto de linea,
# "not_process" no procesar,
# correct_split_word = "any_line"
correct_split_word = "same_line"
# correct_split_word = "not_process"
