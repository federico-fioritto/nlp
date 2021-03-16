from pathlib import Path as OriginalPath, PurePosixPath
import os
import csv
from enum import Enum
import pandas as pd
from functools import reduce
import pdb

########################################################################
########################### VALIDATIONS ################################
########################################################################

def validate_env_variables():
    if (not os.getenv('LOCAL_TESSERACT_EVALUATION_OUTPUTS_PATH')
        or not os.getenv('LOCAL_TESSERACT_TRAINING_OUTPUTS_PATH')
        or not os.getenv('LOCAL_LUISA_TRADUCTIONS_PATH')
        or not os.getenv('LOCAL_STEP_1_OUTPUTS_PATH')
        or not os.getenv('LOCAL_STEP_2_OUTPUTS_PATH')
        or not os.getenv('LOCAL_RESULTS_EVALUATION_PATH')):
        raise Exception(
            """No seteaste todas las variables del env o te olvidaste de cargarlo
                Para cargarlo:
                from dotenv import load_dotenv
                load_dotenv()"""
            )

def validate_directory(dirname):
    if dirname not in DIRECTORIES: raise Exception(f'Invalid directory: {dirname}')

def validate_file_exists(dirname, filename):
    f = DIRECTORIES[dirname] / filename
    if not f.exists(): raise Exception(f'File {filename} does not exists')
    if not f.is_file(): raise Exception(f'The path {dirname + filename} is not a file')

########################################################################
########################## FORK DE PATH ################################
########################################################################

class Path(type(OriginalPath())):
    # Fork de la librería para poder tener appends.
    def append_text(self, data, encoding=None, errors=None):
        """
        Open the file in text mode, append to it, and close the file.
        """
        if not isinstance(data, str):
            raise TypeError('data must be str, not %s' %
                            data.__class__.__name__)
        with self.open(mode='a', encoding=encoding, errors=errors) as f:
            return f.write(data)

########################################################################
########################### DIRECTORIES ################################
########################################################################

validate_env_variables()

DIR_CURRENT = Path(os.path.dirname(__file__))
DIR_CORPUS = DIR_CURRENT / Path('../docs/corpus')
DIR_MANUAL_CORRECTIONS = DIR_CURRENT / Path('../docs/manual_corrections')
DIR_OUTPUTS = DIR_CURRENT / Path('../docs/outputs')
DIR_POST_PROCESSED = DIR_CURRENT / Path('../docs/post_processed')
DIR_VOCABULARIES = DIR_CURRENT / Path('../docs/vocabularies')
DIR_RESULTS = DIR_CURRENT / Path('../docs/results')
DIR_IMPROVED_OUTPUTS = DIR_CURRENT / DIR_OUTPUTS / Path('./improved')
DIR_POST_PROCESSED_GOOGLE = DIR_CURRENT / DIR_POST_PROCESSED / Path('./google')
DIR_POST_PROCESSED_WIKI = DIR_CURRENT / DIR_POST_PROCESSED / Path('./wiki')

DIR_LOCAL_TESSERACT_EVALUATION_OUTPUTS = Path(os.getenv('LOCAL_TESSERACT_EVALUATION_OUTPUTS_PATH'))
DIR_LOCAL_TESSERACT_TRAINING_OUTPUTS = Path(os.getenv('LOCAL_TESSERACT_TRAINING_OUTPUTS_PATH'))
DIR_LOCAL_LUISA_TRADUCTIONS = Path(os.getenv('LOCAL_LUISA_TRADUCTIONS_PATH'))
DIR_LOCAL_STEP_1_OUTPUTS = Path(os.getenv('LOCAL_STEP_1_OUTPUTS_PATH'))
DIR_LOCAL_STEP_2_OUTPUTS = Path(os.getenv('LOCAL_STEP_2_OUTPUTS_PATH'))
DIR_LOCAL_STEP_RESULTS_EVALUATION = Path(os.getenv('LOCAL_RESULTS_EVALUATION_PATH'))

DIRECTORIES = {
    'corpus': DIR_CORPUS,
    'manual_corrections': DIR_MANUAL_CORRECTIONS,
    'outputs': DIR_OUTPUTS,
    'improved_outputs': DIR_IMPROVED_OUTPUTS,
    'vocabularies': DIR_VOCABULARIES,
    'results': DIR_RESULTS,
    'post_processed': DIR_POST_PROCESSED,
    'post_processed_google': DIR_POST_PROCESSED_GOOGLE,
    'post_processed_wiki': DIR_POST_PROCESSED_WIKI,
    'local_tesseract_evaluation_outputs': DIR_LOCAL_TESSERACT_EVALUATION_OUTPUTS,
    'local_tesseract_training_outputs': DIR_LOCAL_TESSERACT_TRAINING_OUTPUTS,
    'local_luisa_traductions': DIR_LOCAL_LUISA_TRADUCTIONS,
    'local_step_1_outputs': DIR_LOCAL_STEP_1_OUTPUTS,
    'local_step_2_outputs': DIR_LOCAL_STEP_2_OUTPUTS,
    'local_results_evaluation': DIR_LOCAL_STEP_RESULTS_EVALUATION
}

########################################################################
########################### PUBLIC FUNCTIONS ###########################
########################################################################

def merge_csvs(dirname, file_names=[], merge_on_column='merge_column', **kwargs):
    if not file_names:
        file_names = read_directory_files(dirname, file_extension='.csv')

    def do_merge(acc, df):
        return pd.merge(acc, df, on=merge_on_column)

    if 'configurations_comp.csv' in file_names: file_names.remove('configurations_comp.csv')

    dataframes = [ read_csv_file(dirname, f, **kwargs) for f in file_names ]

    merged_results = reduce(do_merge, dataframes)
    merged_results.columns = ['filename'] + file_names

    return merged_results

def read_file(dirname, filename, encoding='utf-8-sig'):
    """Lee el contenido del archivo indicado.
    Devuelve el resultado como string.
    """
    validate_directory(dirname)
    validate_file_exists(dirname, filename)

    f = DIRECTORIES[dirname] / filename
    return f.read_text(encoding, errors='ignore')

def read_csv_file(dirname, filename, **kwargs):
    """Lee el contenido del archivo indicado como csv.
    """
    validate_directory(dirname)
    validate_file_exists(dirname, filename)

    f = DIRECTORIES[dirname] / filename
    return pd.read_csv(f,  **kwargs)

def write_file(dirname, filename, content, encoding='utf-8'):
    """Escribe el contenido en el archivo.
    Crea el archivo si no existe uno con ese nombre.
    """
    validate_directory(dirname)

    f = DIRECTORIES[dirname] / filename
    f.write_text(content, encoding, errors='ignore')

def write_csv_file(dirname, filename, columns, data, encoding='utf-8'):
    """Escribe el contenido en el archivo como csv.
    Recibe las columnas ['column1', 'column2'] y la data { 'column1': 1, 'column2': 2 }
    a escribir.
    Crea el archivo si no existe uno con ese nombre.
    """
    validate_directory(dirname)

    f = DIRECTORIES[dirname] / filename
    with f.open(mode='w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for data in data:
            writer.writerow(data)

def append_file(dirname, filename, content, encoding='utf-8'):
    """Apendea el contenido en el archivo.
    Si no existe el archivo indicado devuelve error.
    """
    validate_directory(dirname)
    validate_file_exists(dirname, filename)

    f = DIRECTORIES[dirname] / filename
    f.append_text(content, encoding, errors='ignore')

def read_directory_files(dirname, file_extension=None):
    """Retorna una lista con los nombres de todos los
    archivos dentro del directorio indicado.
    """
    def check_extension_if_passed(file):
        return  file.suffix == file_extension if file_extension else True

    validate_directory(dirname)

    return [ f.name for f in DIRECTORIES[dirname].iterdir() if f.is_file() and check_extension_if_passed(f)]

########################################################################
########################### EXAMPLES OF USAGE ##########################
########################################################################

# Primero importar el helper
# import helpers.file as fh

# manual_correction = fh.read_file('manual_corrections', 'example_1.txt')
# fh.write_file('manual_corrections', 'test.txt', 'works!')
# fh.append_file('manual_corrections', 'test.txt', ' yay!')
