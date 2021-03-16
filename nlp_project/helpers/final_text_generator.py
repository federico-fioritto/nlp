
import re
from copy import deepcopy

SPECIAL_CHARACTERS = {
    "''": '"',
    "``": '"',
    "’’": '"',
}

def handle_special_tokens(token):
    # Algunos tokens son transformados por nuesto tokenizador, cuando buscamos por ellos en el texto
    # original los devolvemos a su forma original.
    if token in SPECIAL_CHARACTERS:
        return SPECIAL_CHARACTERS[token]

    return token

def calculate_search_start_index(partially_indexed_tokens):
    # Recibe una lista de tokens parcial con sus posiciones iniciales dentro del texto.
    # Notar que la lista la recibe mientras esta se va construyendo, de ahí el nombre de la variable.
    # Asume que se quiere el índice de búsqueda del token que le sigue al último token apendeado en la lista.

    # Texto: 'Hola que tal'
    # Recibe: [{value: 'hola', index_in_text: 0}] -> Lista parcial de tokens indexados
    # Devuelve: 0 + 4 (last_index_found + len*())

    # Si se está indizando el primer token, el indice de comienzo de búsqueda será 0.
    if not partially_indexed_tokens: return 0

    last_indexed_token = handle_special_tokens(partially_indexed_tokens[-1]["value"])
    last_index_found = partially_indexed_tokens[-1]["index_in_text"]

    return last_index_found + len(last_indexed_token)


def search_token_index_in_text(searched_token, text, search_start_index):
    # Buscamos el token indicado dentro del texto.
    # La búsqueda dentro del texto comienza a partir del índice pasado por parámetro: search_start_index.
    # Se asume que el token buscado será la primer debe ser la primer palabra a partir del search_start_index.
    # Una vez que comienza la búsqueda, se matchean cero o más espacios en blanco al inicio
    # del texto.
    # Devuelve el índice del primer caracter del token dentro del texto.

    searched_token = handle_special_tokens(searched_token)
    escaped_searched_token = re.escape(searched_token)

    regex = rf'^(\s*){escaped_searched_token}'

    match = re.search(regex, text[search_start_index:], re.IGNORECASE)

    if match:
        white_spaces_matched = match.group(1)
        return search_start_index + len(white_spaces_matched)
    else:
        raise ValueError(f'The token: {searched_token} was not found in the given text')

def calculate_token_indexes(text, tokens):
    indexed_tokens = []
    for i, token in enumerate(tokens):

        # Calculo el índice en el que comenzará la búsuqeda de _token_ en el texto
        search_start_index = calculate_search_start_index(indexed_tokens)

        # Una vez obtenido el índice de comienzo de búsqueda, buscamos _token_ en el texto
        token_index = search_token_index_in_text(token, text, search_start_index)

        # Guardamos el resultado
        indexed_tokens.append({
            "value": token,
            "index_in_text": token_index
        })
    return indexed_tokens

def insert_between_indexes(elem_to_insert, index_start, index_end, text):
    return text[:index_start] + elem_to_insert + text[index_end:]

def correct_tokens_in_text(original_text, tokens_with_corrections):
    new_text = deepcopy(original_text)

    for elem in reversed(tokens_with_corrections):
        #Se si la palabra no es error pero tiene correccion (fue marcada con *|) se corrige
        if not elem["isError"] and elem["value"] == elem["correction"]: continue

        elem_to_insert = elem["correction"]
        index_start = elem["index_in_text"]
        index_end = elem["index_in_text"] + len(handle_special_tokens(elem["value"]))

        new_text = insert_between_indexes(elem_to_insert, index_start, index_end, new_text)

    return new_text

def correct_tokens_in_text_split_words_by_line(original_text, tokens_with_corrections):
    new_text = deepcopy(original_text)

    for i, elem in reversed(list(enumerate(tokens_with_corrections))):
        if elem["isSecondPart"]:
            elem_to_insert = elem["correction"]
            index_start =tokens_with_corrections[i-1]["index_in_text"]
            index_end = elem["index_in_text"] + len(handle_special_tokens(elem["value"]))
            new_text = insert_between_indexes(elem_to_insert, index_start, index_end, new_text)

    return new_text

def correct_tokens_in_text_split_words(original_text, tokens_with_corrections):
    new_text = deepcopy(original_text)

    reverse_list = reversed(list(enumerate(tokens_with_corrections)))
    for i, elem in reverse_list:

        if elem["isLastPart"]:
            elem_to_insert = elem["correction"]

            if (elem["wordParts"] == 3):
                index_start =tokens_with_corrections[i-2]["index_in_text"]
            else:
                index_start =tokens_with_corrections[i-1]["index_in_text"]
            index_end = elem["index_in_text"] + len(handle_special_tokens(elem["value"]))
            new_text = insert_between_indexes(elem_to_insert, index_start, index_end, new_text)

    return new_text

def test_indexes(text, indexed_tokens):
    for indexed_token in indexed_tokens:
        largo = indexed_token["index_in_text"] + len(handle_special_tokens(indexed_token["value"]))
        original = text[indexed_token["index_in_text"]:largo].lower()
        token = handle_special_tokens(indexed_token["value"]).lower()
        if original != token:
            print(original)
            print(token)


def generate_text(original_text, tokens_with_corrections):
    tokens_with_corrections = deepcopy(tokens_with_corrections)
    original_tokens = [elem["value"] for elem in tokens_with_corrections]

    # Calculo la posición de comienzo de cada token en el texto
    indexed_tokens = calculate_token_indexes(original_text, original_tokens)

    # Una vez que se tienen las posiciones de comienzo, agrego cada posición a su token correspondiente
    # en la lista de resultados.
    for i, elem in enumerate(tokens_with_corrections):
        elem.update({"index_in_text": indexed_tokens[i]["index_in_text"]})

    # Finalmente, teniendo la lista de resultados con correcciones y con posiciones, corrijo el texto.
    final_text = correct_tokens_in_text(original_text, tokens_with_corrections)

    return final_text

def generate_text_split_words_by_newline(original_text, tokens_with_corrections):
    tokens_with_corrections = deepcopy(tokens_with_corrections)
    original_tokens = [elem["value"] for elem in tokens_with_corrections]

    # Calculo la posición de comienzo de cada token en el texto
    indexed_tokens = calculate_token_indexes(original_text, original_tokens)

    # Una vez que se tienen las posiciones de comienzo, agrego cada posición a su token correspondiente
    # en la lista de resultados.
    for i, elem in enumerate(tokens_with_corrections):
        elem.update({"index_in_text": indexed_tokens[i]["index_in_text"]})

    # Finalmente, teniendo la lista de resultados con correcciones y con posiciones, corrijo el texto.
    final_text = correct_tokens_in_text_split_words_by_line(original_text, tokens_with_corrections)

    return final_text

def generate_text_split_words(original_text, tokens_with_corrections):
    tokens_with_corrections = deepcopy(tokens_with_corrections)
    original_tokens = [elem["value"] for elem in tokens_with_corrections]

    # Calculo la posición de comienzo de cada token en el texto
    indexed_tokens = calculate_token_indexes(original_text, original_tokens)

    # Una vez que se tienen las posiciones de comienzo, agrego cada posición a su token correspondiente
    # en la lista de resultados.
    for i, elem in enumerate(tokens_with_corrections):
        elem.update({"index_in_text": indexed_tokens[i]["index_in_text"]})

    # Finalmente, teniendo la lista de resultados con correcciones y con posiciones, corrijo el texto.
    final_text = correct_tokens_in_text_split_words(original_text, tokens_with_corrections)

    return final_text