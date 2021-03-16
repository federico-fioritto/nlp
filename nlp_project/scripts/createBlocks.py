#Flags POSIBLES
# "-t", "--tanda"
# "-i", "--image"
# "-fc", "--filterChar"
# '-Join_Split_Word',"Las palabras dividas con '-' se unen"

try:
    from PIL import Image
except ImportError:
    import Image
import psycopg2
from txtgenerator import TxtGenerator
import imp
import re
import os
import argparse
from dotenv import load_dotenv

PSQL_HOST = None
PSQL_PORT = None
PSQL_USER = None
PSQL_PASS = None
PSQL_DB = None
most_common_dict = None
caracteresAFiltrar = ''
fh = None

import os
from dotenv import load_dotenv
load_dotenv()


import sys
sys.path.append("..")
import config
from modules.postprocessor import Postprocessor
post = None
from symspellpy.symspellpy import SymSpell, Verbosity

# Esta configuracion se puede modificar o tomar de config.py
sym_spell = None
count_index = 1
term_index = 0
dir_path_vocabulary = os.path.join(os.path.dirname(__file__), '../docs/vocabularies/')
dir_path_output = os.path.join(os.path.dirname(__file__), '../docs/outputs/')
suggestion_verbosity = "Verbosity.CLOSEST"


def build_script_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--image", required=False)
    arg_parser.add_argument("-d", "--dbType", required=False)
    arg_parser.add_argument("-t", "--tanda", required=False)
    arg_parser.add_argument("-fc", "--filterChar", required=False)
    # arg_parser.add_argument("-px", "--pixel", required=False)
    arg_parser.add_argument('-Join_Split_Word', action='store_true',help="Las palabras dividas con '-' se unen")

    return arg_parser.parse_args()


def existTranslate(idBloque):

    return (idBloque in most_common_dict.keys() and most_common_dict[idBloque]!= "")

def blocksToFilter(idBloqueActual, idBloqueProximo):
    return most_common_dict[idBloqueActual] == '.' and (most_common_dict[idBloqueProximo] == '.')

def insertNewLine(idBloqueAnterior, idBloqueActual):

    # '.-' en ultimos dos bloques
    insertNewLine = existTranslate(idBloqueAnterior) and existTranslate(idBloqueActual) and \
                    most_common_dict[idBloqueAnterior] == '.' and most_common_dict[idBloqueActual] == '-'

    # '.-' en ultimo bloque
    insertNewLine = insertNewLine or existTranslate(idBloqueActual) and '.-' in most_common_dict[idBloqueActual]

    return insertNewLine

def charOccur(charFilter, tradicction):

    for elem in charFilter:
        if (elem in tradicction):
            return True

    return False

def cleanText(traduccion):
    cleanText = ""
    for line in traduccion.splitlines():
        # [^\s^,]*(.*)
        buscarCosa = re.findall(r'^[\s.,\-:;\"]*(.*)', line)
        cleanText = cleanText + buscarCosa[0] + '\n'

    return cleanText

def join_split_word(word1,word2):

    if (str(most_common_dict[word1])[-1] == "-") and (len(str(most_common_dict[word1]))>1) and (str(most_common_dict[word1])[-2].isalpha()):
        return most_common_dict[word1][:-1]+most_common_dict[word2]
    else:
        #No se pueden unir
        return None


def have_errors(word, vocabulary):
    def is_non_alphanumeric(s):
        return all(not c.isalnum() for c in s)

    def has_format_like_date(text):
        pattern = re.compile("^(\d+)$|^((\w+\/){2})\w+$")
        return bool(pattern.match(text))

    def have_ortography_error(word):
        return not is_non_alphanumeric(word) and not word.isnumeric() and word not in vocabulary

    word_lower = str.lower(word)

    return have_ortography_error(word_lower) and not has_format_like_date(word_lower)


def load_vocabulary(sym_spell, vocabulary_name):
    if not sym_spell:
        sym_spell = SymSpell(3,7)

    if not vocabulary_name:
        raise ValueError('Vocabulary is required')

    print('cargando vocabulario', vocabulary_name)

    extension = os.path.splitext(vocabulary_name)[1].lower()
    if extension == '.txt':
        if not sym_spell.load_dictionary(
                dir_path_vocabulary + vocabulary_name,
                term_index, count_index,
                encoding='utf8'
        ):
            raise ValueError('Dictionary file not found')
    elif extension == '.pkl':
        if not sym_spell.load_pickle(dir_path_vocabulary + vocabulary_name):
            raise ValueError('Dictionary file not found')
    else:
        raise ValueError('Unsupported file not found')

    print('vocabulario cargado\n')
    return sym_spell._words

def has_format_like_date(text):
    pattern = re.compile("^(\d+)$|^((\w+\/){2})\w+$")
    return bool(pattern.match(text))

def remove_stamp(text):
    bloque = text.replace("PROCESADO","")
    bloque = bloque.replace("DEP. I","")
    bloque = bloque.replace("DEP.","")
    bloque = bloque.replace("I.","")
    return bloque

def get_blocks_to_avoid():
#Para tanda 1 devolvio 651 resultados
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (
        PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
    conn = psycopg2.connect(connstr)
    # Abrir un cursor para realizar operaciones sobre la base de datos
    cur = conn.cursor()

    if dbType == "2":
        avoid_blocksSQL = """select distinct tab1.id, tab2.id, tab3.id from
                (select distinct b.id, b.i0, b.j0, texto, filename from public.hoja h
                    inner join bloque b on h.id =b.idhoja
                    inner join texto te on b.hash = te.idbloque
                    where texto like 'PROCESADO' )
                tab1
                full join
                (select distinct b.id, b.i0, b.j0, texto, filename from public.hoja h
                    inner join bloque b on h.id =b.idhoja
                    inner join texto te on b.hash = te.idbloque
                    where (texto like 'DEP%' and texto like '%I') or (texto like 'DEP') or (texto like 'DEP.') )
                tab2 on tab1.filename = tab2.filename 
                full join
                (select distinct b.id, b.i0, b.j0, texto, filename from public.hoja h
                    inner join bloque b on h.id =b.idhoja
                    inner join texto te on b.hash = te.idbloque
                    where texto like '%I' )
                tab3 on tab1.filename = tab3.filename
                where ((abs(tab1.i0 - tab2.i0) < 250) and (abs(tab1.j0 - tab2.j0) < 250)) and
                    ((abs(tab1.i0 - tab3.i0) < 250) and (abs(tab1.j0 - tab3.j0) < 250))
                """
    else:
        avoid_blocksSQL = """select distinct tab1.hashid, tab2.hashid, tab3.hashid from	
                (select distinct b.hashid, b.i0, b.j0, texto, filename from public.hoja h
                    inner join bloque b on h.hash =b.hashhoja
                    inner join texto te on b.hashid = te.hashidbloque
                    where texto like 'PROCESADO' )
                tab1
                full join
                (select distinct b.hashid, b.i0, b.j0, texto, filename from public.hoja h
                    inner join bloque b on h.hash =b.hashhoja
                    inner join texto te on b.hashid = te.hashidbloque
                    where (texto like 'DEP%' and texto like '%I') or (texto like 'DEP') or (texto like 'DEP.') )
                tab2 on tab1.filename = tab2.filename 
                full join
                (select distinct b.hashid, b.i0, b.j0, texto, filename from public.hoja h
                    inner join bloque b on h.hash =b.hashhoja
                    inner join texto te on b.hashid = te.hashidbloque
                    where texto like '%I' )
                tab3 on tab1.filename = tab3.filename
                where ((abs(tab1.i0 - tab2.i0) < 250) and (abs(tab1.j0 - tab2.j0) < 250)) and
                    ((abs(tab1.i0 - tab3.i0) < 250) and (abs(tab1.j0 - tab3.j0) < 250))
                """

    cur.execute(avoid_blocksSQL)
    avoid_blocks = cur.fetchall()

    avoid_blocks_set = {""}
    for i in range(0, len(avoid_blocks)):
        avoid_blocks_set.add(avoid_blocks[i][0])
        avoid_blocks_set.add(avoid_blocks[i][1])
        avoid_blocks_set.add(avoid_blocks[i][2])
    return avoid_blocks_set


def preocessSheet(sheet,joined_words_number, final_words_to_join_dict):
    traduccion = ""
    cantBloquesNoTraducidos = 0
    cantBloquesTraducidos = 0

    # cantBloquesCorrectos = 0
    # cantBloquesIncorrectos = 0

    try:
        # Conectarse a la base de datos
        connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (
            PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
        conn = psycopg2.connect(connstr)
        # Abrir un cursor para realizar operaciones sobre la base de datos
        cur = conn.cursor()

        # Obtener distintas hojas de la base
        sqlqueryHojas = """select  distinct filename, id from hoja """
        if sheet:
            sqlqueryHojas= sqlqueryHojas + "where filename = '" +sheet +"'"""


        cur.execute(sqlqueryHojas)
        hojas = cur.fetchall()


        correctJoin = 0
        incorrectJoin = 0
        correctList = []
        incorrectList = []
        nested_split_dictionary = {}


        for hoja in range(0, len(hojas)):
        # for hoja in range(0, 100):

            traduccion = ""

            sqlquery = ""
            if (dbType == "2"):
                sqlquery = """select distinct b.id, b.i0, b.j0, b.i1, b.j1, h.filename from public.hoja h
                    inner join bloque b on h.id =b.idhoja
                    inner join texto te on b.hash = te.idbloque
                    where h.filename = '""" + hojas[hoja][0] + """' 
                    and texto <> ''
                    and not texto  in('','@')
                    order by b.i0, b.j0 ASC;"""
            else:
                sqlquery = """select distinct b.hashid, b.i0, b.j0, b.i1, b.j1, h.filename from public.hoja h
                inner join bloque b on h.hash =b.hashhoja
                inner join texto te on b.hashid = te.hashidbloque
                where h.filename = '""" + hojas[hoja][0] + """' 
                and not texto  in('','@')
                order by b.i0, b.j0 ASC;"""
            cur.execute(sqlquery)
            bloques = cur.fetchall()
            print("bloques en hoja")
            print(len(bloques))
            #bloques con sello
            avoid_blocks_set = get_blocks_to_avoid()

            # Si el bloque fue traducido, se agrega el resultado mas común a la traducción
            continue_process_block = True
            # print(hojas[hoja][0])

            len_avoid_word = 0
            for i in range(0, len(bloques)):

                bloqueActual = bloques[i][0]

                # Se detectó que una palabra fue dividida en varios bloques y se debe evitar agregar partes siguientes de la palabra
                if (len_avoid_word == 0):
                    len_avoid_word, joined_word = len_join_word(hojas[hoja][1], bloqueActual,final_words_to_join_dict)
                    # Se detectó que una palabra fue dividida en varios bloques
                    if (len_avoid_word > 0):
                        len_avoid_word = len_avoid_word -1
                        bloque_transalte = remove_stamp(joined_word)
                        traduccion = traduccion + " " + bloque_transalte
                        joined_words_number += 1
                        cantBloquesTraducidos += len_avoid_word

                    #No es parte de una palabra dividida por bloques
                    else:
                        bloqueSiguiente = ""
                        for m in range(i+1,len(bloques)):
                            if (existTranslate(bloques[m][0])):
                                bloqueSiguiente = bloques[m][0]
                                break
                        if (continue_process_block and existTranslate(bloqueActual) and not charOccur(caracteresAFiltrar, most_common_dict[bloqueActual])):

                            #Se intenta procesar 2 bloques a la vez
                            if (i < len(bloques)-1) and existTranslate(bloqueSiguiente) and not charOccur(caracteresAFiltrar, most_common_dict[bloqueSiguiente]):

                                #Unir palabras divididas por "-" y salto de linea
                                if (ARGS.Join_Split_Word):
                                    #Voy a agregar la palabra a la traduccion
                                    jsw = join_split_word(bloqueActual, bloqueSiguiente)
                                    if (jsw!= None and have_errors(jsw,vocabulary)):
                                        incorrectJoin += 1
                                        # split_dict['incorrect_nr'] += 1
                                        # if jsw not in split_dict['incorrect_frequency_dict']:
                                        #     split_dict['incorrect_frequency_dict'][jsw] = 0
                                        # split_dict['incorrect_frequency_dict'][jsw] += 1
                                        incorrectList.append(jsw)
                                    elif(jsw!= None):
                                        correctJoin += 1
                                        # split_dict['correct_nr'] += 1
                                        # if jsw not in split_dict['correct_frequency_dict']:
                                        #     split_dict['correct_frequency_dict'][jsw] = 0
                                        # split_dict['correct_frequency_dict'][jsw] += 1
                                        correctList.append(jsw)

                                    if (not jsw == None):

                                        # Es una palabra partida a la mitad con un guión
                                        traduccion = traduccion + " " + jsw
                                        continue_process_block = False
                                        cantBloquesTraducidos += 2

                            #Se intenta procesar 1 bloques a la vez, solo si no se pudo procesar de a 2
                            if (continue_process_block):
                                bloque_transalte = most_common_dict[bloqueActual]
                                if ( bloqueActual in avoid_blocks_set):
                                    bloque_transalte = remove_stamp(most_common_dict[bloqueActual])
                                traduccion = traduccion + " " + bloque_transalte
                                cantBloquesTraducidos += 1

                        else:
                            cantBloquesNoTraducidos += 1
                            if (existTranslate(bloqueActual)):
                                continue_process_block = True
                else:
                    len_avoid_word = len_avoid_word -1

                # SE AGREGA SALTO DE LINEA?
                traduccion = add_new_line_if_is_needed(bloques,i,traduccion)

            total = cantBloquesNoTraducidos + cantBloquesTraducidos
            # print("Bloques no traducidos: "+str(cantBloquesNoTraducidos) + "/"+str(total))

            # SE LIMPIA EL TEXTO
            textoResultante = cleanText(traduccion)
            # print(traduccion)
            # print(textoResultante)
            # f = open("./scripts/textFromBlocks/"+PSQL_DB+"/"+hojas[hoja][0]+".txt", "w+")
            # f.write(textoResultante)
            # f.close()

            # print(hojas[hoja][0])

            file_name = hojas[hoja][0].replace("Rollo ","").replace("rollo ","")
            # print("va a guardar")
            fh.write_file('local_luisa_traductions', file_name+".txt", textoResultante)

        cur.close()
        conn.close()
        return joined_words_number

    except BaseException as error:
        print("El error es:")
        if (existTranslate(error)):
            print(most_common_dict[error])
        print(error)
        return joined_words_number


def add_new_line_if_is_needed(bloques,i,traduction):
    if ((i < len(bloques)-1) and (bloques[i+1][1] > bloques[i][1])):
        traduction += '\n'
    return traduction

def get_parts_luisa_split_word(pixel):

    query = ""

    if dbType == "2":
        query = """select distinct * 
                from
                (select distinct h.id idhoja1,h.filename hoja1,
                b.id idb1, b.i0 alfai0,b.i1 alfai1,b.j0 alfaj0,b.j1 alfaj1
                    from public.hoja h 
                    inner join public.bloque b on h.id =b.idhoja 
                        inner join public.texto te 
                        on b.hash = te.idbloque 
                        ) alfa
                inner join        
                (select distinct h2.id idhoja2, h2.filename hoja2,
                b2.id idb2, b2.i0 betai0,b2.i1 betai1,b2.j0 betaj0,b2.j1 betaj1
                    from public.hoja h2
                    inner join public.bloque b2 on h2.id =b2.idhoja 
                        ) beta
                        --beta es la segunda palabra
                on (betai0 = alfai0 and betai1 = alfai1) and (betaj0 - alfaj1 <= """ + str(pixel) + """ and (alfaj0 < betaj0 )) 
                and alfa.idb1 <> beta.idb2 and alfa.idhoja1 = beta.idhoja2
                order by idhoja1, betai0, betaj0 asc
               """
    else:
        query = """select distinct * 
                    from
                    (select distinct h.hash hashhoja1,h.filename hoja1,
                    b.hashid idb1, b.i0 alfai0,b.i1 alfai1,b.j0 alfaj0,b.j1 alfaj1
                        from public.hoja h 
                        inner join public.bloque b on h.hash =b.hashhoja 
                            ) alfa
                    inner join        
                    (select distinct h2.hash hashhoja2, h2.filename hoja2,
                    b2.hashid idb2, b2.i0 betai0,b2.i1 betai1,b2.j0 betaj0,b2.j1 betaj1
                        from public.hoja h2
                        inner join public.bloque b2 on h2.hash =b2.hashhoja 
                            ) beta
                    on (betai0 = alfai0 and betai1 = alfai1) and (betaj0 - alfaj1 <= """ + str(pixel) + """ and (alfaj0 < betaj0 )) 
                    and alfa.idb1 <> beta.idb2 and alfa.hashhoja1 = beta.hashhoja2
                    order by hashhoja1, betai0, betaj0 asc
                   """

    try:
        # Conectarse a la base de datos
        connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (
            PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
        conn = psycopg2.connect(connstr)
        # Abrir un cursor para realizar operaciones sobre la base de datos
        cur = conn.cursor()

        # Obtener distintas hojas de la base

        cur.execute(query)
        bloques = cur.fetchall()

        listoflists = []
        word_list = []

        for i in range(0, len(bloques)):

            bloqueActual = bloques[i]

            #mismo X y Y con diferencia menor o igual a 3
            if ((bloqueActual[3]== bloqueActual[10] and bloqueActual[4]== bloqueActual[11]) and (bloqueActual[12] - bloqueActual[6]<= int(pixel))):
                # inserto id bloque actual
                word_list.append(bloqueActual[2])

                if (i+1< len(bloques)):
                    bloqueSiguiente = bloques[i+1]

                    if (bloqueActual[9] != bloqueSiguiente[2]):
                        #inserto la segunda parte del bloque actual
                        word_list.append(bloqueActual[9])
                        listoflists.append([bloqueActual[0],word_list])
                        word_list = []
                else:
                    #inserto la segunda parte del bloque actual
                    word_list.append(bloqueActual[9])
                    listoflists.append([bloqueActual[0],word_list])
                    word_list = []

        return listoflists

    except BaseException as error:
        print("El error es:"+ str(error))
        return []

def remove_first_last_non_alpha_char(join_word,words_not_empty):
    result = join_word
    len_words = len(words_not_empty)

    if (result != '' and not result[0].isalpha() and most_common_dict[words_not_empty[0]] != result[0]):
        result = result[1:]
    if ( result != '' and not result[-1].isalpha() and most_common_dict[words_not_empty[len_words-1]] != result[-1]):
        result = result[:len(result)-1]
    return result

def get_info_luisa_split_word(result,undefined_corrects, corrects, wrongs, undefined_wrongs):
    # undefined_corrects = []
    # corrects = []
    # wrongs = []
    # undefined_wrongs = []

    for pair_words in result:
        joined_parts = ''
        words_most_common = []
        words_ids = []
        words_not_empty = list(filter(lambda p: existTranslate(p), pair_words[1]))
        for parts in words_not_empty:

            if existTranslate(parts):
                joined_parts += most_common_dict[parts]
                words_most_common.append(most_common_dict[parts])
                words_ids.append(parts)

        if (joined_parts != '' and len(words_most_common)>1):

            are_joined_parts_in_voc = remove_first_last_non_alpha_char(joined_parts,words_not_empty) in vocabulary or remove_first_last_non_alpha_char(joined_parts.lower(), words_not_empty) in vocabulary
            parts_in_voc = list(filter(lambda p: remove_first_last_non_alpha_char(p,words_not_empty).lower() in vocabulary, words_most_common))
            amount_of_parts_in_voc = len(parts_in_voc)
            results_to_print = {
                'parts': words_most_common,
                'joined_parts': joined_parts,
                'are_joined_parts_in_voc': are_joined_parts_in_voc,
                'amount_of_parts_in_voc': amount_of_parts_in_voc,
                'parts_in_voc': parts_in_voc,
                'sheet_id': pair_words[0],
                'block_id_list': words_ids,
            }

            if are_joined_parts_in_voc and amount_of_parts_in_voc>0 :
                undefined_corrects.append(results_to_print)
            elif are_joined_parts_in_voc:
                corrects.append(results_to_print)
            elif amount_of_parts_in_voc>0:
                wrongs.append(results_to_print)
            else:
                undefined_wrongs.append(results_to_print)

def create_words_to_join_dict(undefined_corrects,corrects, dict_join_words):

    pepe = 0
    # Se agrega la palabra cuando las partes son erroneas y la union correcta
    for word in corrects:
        if not (word["sheet_id"] in dict_join_words):
            sheet_list = []
        else:
            sheet_list = dict_join_words[word["sheet_id"]]
        sheet_list.append(word)
        dict_join_words[word["sheet_id"]] = sheet_list

    # Se agrega la palabra cuando al menos una de las partes es erronea y la union correcta
    for word in undefined_corrects:

        if (len(word["parts_in_voc"]) < len(word["parts"])):
            if not (word["sheet_id"] in dict_join_words):
                sheet_list = []
            else:
                sheet_list = dict_join_words[word["sheet_id"]]

            sheet_list.append(word)
            dict_join_words[word["sheet_id"]] = sheet_list
        else:
            pepe +=1


def len_join_word(sheet_id, block_id,dict_join_words):

    if(sheet_id in dict_join_words):
        for word in dict_join_words[sheet_id]:
            for part in word["block_id_list"]:
                if (part == block_id):
                    return len(word["parts"]), word["joined_parts"]
    return 0,""

def count_word_in_dict(dict_join_words):
    n = 0
    for sheet in dict_join_words:
        for word in dict_join_words[sheet]:
            n +=1
    return n

def word_part_in_set(set_of_word, word):
    in_set = False
    for part in word["block_id_list"]:
        if (part in set_of_word):
            in_set = True
    return in_set


def join_words_to_join_dict(dict_join_words3px,dict_join_words4px):

    set_definitivo = set()
    final_words_to_join_dict = {}
    palabras4 = 0
    palabras3 = 0
    palabrasNo = 0

    for key in dict_join_words4px.keys():
        final_words_to_join_dict[key] = dict_join_words4px[key]
        for word in dict_join_words4px[key]:
            palabras4+= 1
            for idbloque in word["block_id_list"]:
                set_definitivo.add(idbloque)

    for key in dict_join_words3px.keys():
        for word in dict_join_words3px[key]:
            if (not word_part_in_set(set_definitivo,word)):
                palabras3+= 1
                if not (key in final_words_to_join_dict.keys()):
                    final_words_to_join_dict[key] = []
                final_words_to_join_dict[key].append(word)
                for idbloque in word["block_id_list"]:
                    set_definitivo.add(idbloque)
            else:

                for word4 in dict_join_words4px[word["sheet_id"]]:
                    if word["block_id_list"][0] in word4["block_id_list"]:
                        # print(word4["parts"])
                        break
                palabrasNo+= 1

    return final_words_to_join_dict

def diff_words(dict_join_words_1,dict_join_words_2):
    set_diff = set()
    final_words_to_join_dict = {}
    palabras1 = 0
    palabras2 = 0
    palabrasSi = 0

    #dict_1 es 6 y dict_2 es 8
    for key in dict_join_words_1.keys():
        for word in dict_join_words_1[key]:
            palabras1+= 1
            for idbloque in word["block_id_list"]:
                set_diff.add(idbloque)

    for key in dict_join_words_2.keys():
        for word in dict_join_words_2[key]:
            if (not word_part_in_set(set_diff,word)):
                palabras2+= 1
                if not (key in final_words_to_join_dict.keys()):
                    final_words_to_join_dict[key] = []
                final_words_to_join_dict[key].append(word)
                for idbloque in word["block_id_list"]:
                    set_diff.add(idbloque)
            else:
                palabrasSi+= 1
    return final_words_to_join_dict

def main():
    load_dotenv()

    global post
    post = Postprocessor()

    # Postgres
    global PSQL_HOST
    global PSQL_PORT
    global PSQL_USER
    global PSQL_PASS
    global PSQL_DB
    global dbType
    global most_common_dict
    global caracteresAFiltrar
    PSQL_HOST = os.getenv("PSQL_HOST")
    PSQL_PORT = os.getenv("PSQL_PORT")
    PSQL_USER = os.getenv("PSQL_USER")
    PSQL_PASS = os.getenv("PSQL_PASS")

    # File helper
    global fh
    fh = imp.load_source('module.name', os.getenv('LOCAL_FILE_HELPER_PATH'))

    if ARGS.tanda:
        PSQL_DB = ARGS.tanda
    else:
        PSQL_DB = "tanda1"

    if ARGS.dbType:
        dbType = ARGS.dbType
    else:
        dbType = "1"

    if ARGS.filterChar:
        caracteresAFiltrar = ARGS.filterChar
    else:
        caracteresAFiltrar = '|'

    global sym_spell
    global vocabulary
    vocabulary = load_vocabulary(sym_spell, config.vocabulary)

    txtGenerator = TxtGenerator(1,PSQL_DB,vocabulary)
    most_common_dict = txtGenerator.get_most_common(dbType)

    # Listas resultados palabras separadas

    undefined_corrects3px = []
    corrects3px = []
    wrongs3px = []
    undefined_wrongs3px = []
    dict_join_words3px = {}
    undefined_corrects4px = []
    corrects4px = []
    wrongs4px = []
    undefined_wrongs4px = []
    dict_join_words4px = {}

    undefined_corrects8px = []
    corrects8px = []
    wrongs8px = []
    undefined_wrongs8px = []
    dict_join_words8px = {}

    undefined_corrects12px = []
    corrects12px = []
    wrongs12px = []
    undefined_wrongs12px = []
    dict_join_words12px = {}

    undefined_corrects16px = []
    corrects16px = []
    wrongs16px = []
    undefined_wrongs16px = []
    dict_join_words16px = {}

    undefined_corrects20px = []
    corrects20px = []
    wrongs20px = []
    undefined_wrongs20px = []
    dict_join_words20px = {}

    undefined_corrects24px = []
    corrects24px = []
    wrongs24px = []
    undefined_wrongs24px = []
    dict_join_words24px = {}


    #Se cargan las listas con las plabras divididas en varios bloques distintos

    #3p
    result = get_parts_luisa_split_word("3")
    get_info_luisa_split_word(result,undefined_corrects3px,corrects3px,wrongs3px, undefined_wrongs3px)
    create_words_to_join_dict(undefined_corrects3px,corrects3px,dict_join_words3px)

    #4px
    result = get_parts_luisa_split_word("4")
    get_info_luisa_split_word(result, undefined_corrects4px,corrects4px,wrongs4px, undefined_wrongs4px)
    create_words_to_join_dict(undefined_corrects4px,corrects4px,dict_join_words4px)

    #8px
    result = get_parts_luisa_split_word("8")
    get_info_luisa_split_word(result, undefined_corrects8px,corrects8px,wrongs8px, undefined_wrongs8px)
    create_words_to_join_dict(undefined_corrects8px,corrects8px,dict_join_words8px)

    #12px
    result = get_parts_luisa_split_word("12")
    get_info_luisa_split_word(result, undefined_corrects12px,corrects12px,wrongs12px, undefined_wrongs12px)
    create_words_to_join_dict(undefined_corrects12px,corrects12px,dict_join_words12px)

    #16px
    result = get_parts_luisa_split_word("16")
    get_info_luisa_split_word(result, undefined_corrects16px,corrects16px,wrongs16px, undefined_wrongs16px)
    create_words_to_join_dict(undefined_corrects16px,corrects16px,dict_join_words16px)

    #20px
    result = get_parts_luisa_split_word("20")
    get_info_luisa_split_word(result, undefined_corrects20px,corrects20px,wrongs20px, undefined_wrongs20px)
    create_words_to_join_dict(undefined_corrects20px,corrects20px,dict_join_words20px)

    #24px
    result = get_parts_luisa_split_word("24")
    get_info_luisa_split_word(result, undefined_corrects24px,corrects24px,wrongs24px, undefined_wrongs24px)
    create_words_to_join_dict(undefined_corrects24px,corrects24px,dict_join_words24px)

    #join de 20px y 24px
    final_words_to_join_dict_20_24  = join_words_to_join_dict(dict_join_words20px,dict_join_words24px)

    #join de 20_24px y 16px
    final_words_to_join_dict_16_20_24 = join_words_to_join_dict(dict_join_words16px,final_words_to_join_dict_20_24)

    #join de 16_20_24px y 12px
    final_words_to_join_dict_12_16_20_24 = join_words_to_join_dict(dict_join_words12px,final_words_to_join_dict_16_20_24)

    #join de 12_16_20_24px y 8px
    final_words_to_join_dict_8_12_16_20_24 = join_words_to_join_dict(dict_join_words8px,final_words_to_join_dict_12_16_20_24)

    #join de 4_8_12_16_20_24px y 4px
    final_words_to_join_dict_4_8_12_16_20_24 = join_words_to_join_dict(dict_join_words4px,final_words_to_join_dict_8_12_16_20_24)

    #join de 3_4_8_12_16_20px y 24px
    final_words_to_join_dict_3_4_8_12_16_20_24 = join_words_to_join_dict(dict_join_words3px,final_words_to_join_dict_4_8_12_16_20_24)

    word_in_dict = count_word_in_dict(final_words_to_join_dict_3_4_8_12_16_20_24)

    word_in_dict3 = count_word_in_dict(dict_join_words3px)
    word_in_dict4 = count_word_in_dict(dict_join_words4px)

    word_in_dict8 = count_word_in_dict(dict_join_words8px)

    word_in_dict12 = count_word_in_dict(dict_join_words12px)

    word_in_dict16 = count_word_in_dict(dict_join_words16px)

    word_in_dict20 = count_word_in_dict(dict_join_words20px)

    word_in_dict24 = count_word_in_dict(dict_join_words24px)

    joined_words_number = preocessSheet(ARGS.image,0,final_words_to_join_dict_3_4_8_12_16_20_24)


ARGS = build_script_arguments()
main()
