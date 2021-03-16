# NLP

### Instalación y ejecución

#### 1- Configurar .env

Una vez descargado el repositorio, estando parados en la raíz de este ejecutar el siguiente comando:

```
cp nlp_project/.env.example nlp_project/.env
```

Esto creará una copia del archivo `.env.example` en el archivo `.env`. Aquí se guardarán parejas clave-valor necesarias para la ejecución de los procesos.
Se deben completar los valores en `.env` según corresponda.

#### 2- Seleccionar archivos a corregir

El siguiente paso será colocar los archivos de texto generados por el OCR que se quieran corregir en el directorio asociado a la variable `LOCAL_TESSERACT_EVALUATION_OUTPUTS_PATH` del `.env`.
Por otro lado, los archivos utilizados como "Ground Truth" deben ir en el directorio asociado a `LOCAL_LUISA_TRADUCTIONS_PATH`. En el proyecto se utilizaron las reconstrucciones de texto a partir de datos de la plataforma Luisa para este punto.
_Es importante recalcar que los nombres de los archivos entre estos dos directorios deben coincidir para poder evaluar resultados al final._ Es decir, si se tiene un archivo de texto a corregir (generado por el OCR) llamado `sample-1` en `LOCAL_TESSERACT_EVALUATION_OUTPUTS_PATH` deberá existir un archivo de igual nombre en `LOCAL_LUISA_TRADUCTIONS_PATH`.

#### Modelo de Lenguaje

##### 3.1- Google N-grams

Por defecto el sistema utiliza una API provista por google como modelo de lenguaje. Esta solución fue la que mejor resultados obtuvo.
Si se desea utilizar esta integración, será necesario correr de forma paralela la aplicación escrita en node ubicada en el directorio `nlp_project/async_requests`.
Para ello primero será necesario instalar las dependencias necesarias:

```
cd nlp_project/async_requests/
npm i
```

Posteriormente se pone a correr la aplicación (por defecto correrá en el puerto 5111)

```
node index.js
```

Y eso es todo en este paso.

##### 3.2- Modelo de Lenguaje 1-Billion Corpus

Este es un modelo creado a partir del corpus del idioma español conocido como 1-Billion y es un paso alternativo al 3.1 visto anteriormente.
Para utilizarlo será necesario contar con el archivo del modelo (pesa unos 8 GB).
Y se deberá editar la variable `language_model` del archivo `nlp_project/config.py` de forma que tenga el valor de `1_billion`.
Si no se realiza este paso el sistema utilizará por defecto la integración con google del paso 3.1.

#### 4- Ejecutar corrección

Finalmente el procesamiento puede realizarse mediante el comando que veremos a continuación (parados en la raíz del proyecto).
Esto leerá todos los archivos que se encuentren en el directorio asociado a la variable `LOCAL_TESSERACT_EVALUATION_OUTPUTS_PATH` del `.env`

```
python3 nlp_project/correct.py
```

Se puede pasar una flag `-d nombre_de_documento` si se quisiera procesar un texto en específico y no todo el directorio.

#### 5- Resultados

El proceso de corrección generará para cada archivo corregido:

- Un texto con resultados intermedios en `LOCAL_STEP_1_OUTPUTS_PATH`
- Un texto con los resultados finales `LOCAL_STEP_2_OUTPUTS_PATH`
- Un archivo con los n-gramas y contextos utilizados en `LOCAL_STEP_2_OUTPUTS_PATH`
- Un archivo con las palabras procesadas que estaban cortadas por salto de linea en `LOCAL_STEP_2_OUTPUTS_PATH`
- Una entrada en el .csv de resultados final en `LOCAL_RESULTS_EVALUATION_PATH`. En este csv se comparan los archivos utilizando dos medidas distintas.

##### Extra: Configuraciones

En el archivo `nlp_project/config.py` encontrarán varias flags que permiten tomar decisiones sobre distintos elementos a la hora de procesar los textos. Estas flags por defecto tienen los valores que mejor resultados obtuvieron, pero pueden ser cambiadas a gusto por los valores allí indicados.

### 6- Script para reconstruir LUISA
Para poder ejecutar correctamente el script que reconstruye LUISA se debe tener configurado las siguientes constantes en el archivo .env.

- PSQL_HOST = (ej. localhost)
- PSQL_PORT = (ej. 5432)
- PSQL_USER = (ej. postgres)
- PSQL_PASS = (ej. postgres)
- LOCAL_LUISA_TRADUCTIONS_PATH= (ej. /path/LOCAL_LUISA_TRADUCTIONS_PATH)

El script se llama "createBlocks.py" y se encuentra en la ruta "nlp/nlp_project/scripts/".
Se le pueden pasar distintas flags para utilizar diferentes configuraciones. Se espera tener una base de datos con determinada estructura que en nuestro caso fué brindada por la Facultad de Ingeniería.

#### Flags posibles:

 "-t" o "--tanda"       		..Es el nombre de la base a la que se quiere conetar.
 
 "-i" o "--image"       		..El nombre de una hoja a procesar(si no se pasa la flag se procesa todas las hojas de la tanda o base).
 
 "-fc" o "--filterChar" 		..Caracteres a eliminar de la salida.
 
 "-Join_Split_Word"		      ..Unir o no las palabras dividas con '-' y salto de linea (si está la flag activa se unen).
 
 "-d" o "--dbType"		      ..Valor "1" para base con formato nuevo (en nuestro caso la tanda 2 tenía distinta estructura de datos que        la tanda 0), valor "2" para base con formato anterior (sin la flag se toma valor "1" por defecto).
 
 #### Las tablas y columnas principales de la estructura de datos para la flag "dbType" en resumen es:
 
 ##### dbType=1
 
 TABLA (columnas,,)
 
 - HOJA (id, rollo, filename, hash)
 
 - BLOQUE (i0,j0,i1,j1,hashid,apariciones,hashhoja)
 
 - TEXTO (id, texto, hashidbloque)
 
 ##### dbType=2
 
 TABLA (columnas,,)
 
 - HOJA (id, rollo, filename, hash)
 
 - BLOQUE (id, idhoja, i0,j0,i1,j1,hash)
 
 - TEXTO (id, texto, idbloque)
 
 
 
 #### Ejemplos de ejecucion:
 
python3 createBlocks.py -Join_Split_Word -t=tanda2 

python3 createBlocks.py -Join_Split_Word -t=tanda0 -d=2

python3 createBlocks.py -t=tanda2 -i="r421_0028.1984"

python3 createBlocks.py -t=tanda0 -d=2 -fc="@"

- Las salidas se guardan en el path configurado para la constante "LOCAL_LUISA_TRADUCTIONS_PATH".
