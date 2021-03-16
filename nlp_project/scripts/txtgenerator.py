try:
    from PIL import Image
except ImportError:
    import Image
import psycopg2
from collections import Counter
import os
from dotenv import load_dotenv



class TxtGenerator:
    def __init__(self, MINIMUM_TRANSCRIPTIONS=1,PSQL_DB="tanda0", VOCABULARY = None):
        load_dotenv()
        self.MINIMUM_TRANSCRIPTIONS = MINIMUM_TRANSCRIPTIONS
        self.PSQL_HOST = os.getenv("PSQL_HOST")
        self.PSQL_PORT = os.getenv("PSQL_PORT")
        self.PSQL_USER = os.getenv("PSQL_USER")
        self.PSQL_PASS = os.getenv("PSQL_PASS")
        self.PSQL_DB = PSQL_DB
        self.vocabulary = VOCABULARY

    def groupBy(self,list):
        res = {}
        for elem in list:
            if elem[0] in res:
                res[elem[0]].append(elem[1])
            else:
                res[elem[0]] = [elem[1]]
        return res



    def desempate(self, palabras_empatadas):
        con_signo_final = []
        sin_signo_final = []
        for word in palabras_empatadas:
            if word[-2:] == '.-' and word[:-2].lower() in self.vocabulary:
                con_signo_final.append(word)
            if word.lower() in self.vocabulary: # si ya encontramos alguna  con .- no consideramos estas
                sin_signo_final.append(word)

        if len(con_signo_final)>0: # doy prioridad a las que tenian .-
            return con_signo_final[0]
        elif len(sin_signo_final)>0: # despues devuelvo las que no tenian punto
            return sin_signo_final[0]
        else:
            return None
            # si llego aca es porque no habíá palabra correcto

    def most_frequent(self,list,count_changed_word):
        # return max(set(list), key=list.count)
        data = Counter(list)
        most_freq_ocurrences = data.most_common(len(list))[0][1]
        # most_freq_ocurrences = data.most_common(1)[0][1]
        most_freq_value_list = data.most_common(len(list))


        most_freq_value = most_freq_value_list[0][0]
        most_freq_ocurrences = most_freq_value_list[0][1]

        #Lista de palabras con la mayor ocurrencia
        most_occurs_value_list = []
        for pair in most_freq_value_list:
            if (pair[1] == most_freq_ocurrences):
                most_occurs_value_list.append(pair[0])
        desempatada = self.desempate(most_occurs_value_list)

        if desempatada != None:
            most_freq_value = desempatada


        # most_freq_value = data.most_common(1)[0][0]
        if (len(list) >= self.MINIMUM_TRANSCRIPTIONS):
            # if (most_freq_ocurrences > len(list)*0.9 and len(list) >= MINIMUM_TRANSCRIPTIONS):
            return most_freq_value
        else:
            return None

    def get_most_common(self,dbType):
        # Conectarse a la base de datos
        connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (
            self.PSQL_HOST, self.PSQL_PORT, self.PSQL_USER, self.PSQL_PASS, self.PSQL_DB)
        conn = psycopg2.connect(connstr)
        # Abrir un cursor para realizar operaciones sobre la base de datos
        cur = conn.cursor()

        # Se obtienen todos los bloques y sus traducciones
        sqlquery = ""
        if (dbType == "2"):
            sqlquery = """select b.id, urldecode_arr(te.texto) from public.hoja h
                inner join public.bloque b on h.id =b.idhoja
                inner join public.texto te on b.hash = te.idbloque
                where te.texto is not null and te.texto <> '' and ((not te.texto like '%\%40%') or 
                not te.texto = '@') """
        else:
            sqlquery = """select b.hashid, REPLACE(urldecode_arr(te.texto), '@', '') from public.hoja h
                inner join public.bloque b on h.hash =b.hashhoja
                inner join public.texto te on b.hashid = te.hashidbloque
                where te.texto is not null and te.texto <> '' and ((not te.texto like '%\%40%') or 
                not te.texto = '@') """

        cur.execute(sqlquery)
        result = cur.fetchall()

        # Cerrar la conexión con la base de datos
        cur.close()
        conn.close()

        result = self.groupBy(result)

        final_result = {}
        cant = 0
        cantFrec = 0
        count_changed_word = 0
        for key, value in result.items():
            most_freq = self.most_frequent(value,count_changed_word)
            cant += 1
            if(most_freq):
                cantFrec += 1
                final_result[key] = most_freq
        print("Cantidad palabras en vocabulario para desempatar:")
        print(count_changed_word)
        return final_result
