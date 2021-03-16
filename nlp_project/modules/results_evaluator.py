from difflib import SequenceMatcher
import helpers.file as fh
import helpers.utils as utils
import time
import helpers.final_text_generator as text_generator
import plotly.graph_objects as go
from functools import reduce
import pdb
from tabulate import tabulate
import matplotlib.pyplot as plt

COLORS = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
]

########################################################################
####################### SIMILARITY MEASURES ############################
########################################################################

def ratio_measure(str1, str2):
    """2.0 * Número total de elementos en cada string / Número de coincidencias
    """
    seq = SequenceMatcher(isjunk=None, autojunk=False)
    seq.set_seqs(str1, str2)
    return seq.ratio()

def jaccard_measure(str1, str2):
    """Tamaño de la intersección de ambos strings / Tamaño de la unión de ambos strings
    """
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

MEASURES = {
    'ratio': ratio_measure,
    'jaccard': jaccard_measure
}

########################################################################
########################### VALIDATIONS ################################
########################################################################

def validate_measure(measure_type):
    if measure_type not in MEASURES: raise Exception('Invalid measure')

########################################################################
############################ AUX FUNCTIONS #############################
########################################################################

def format_ngrams(tokens):
    errors = ''
    corrects = ''

    def get_suggestions(s_list):
        terms = ''
        if s_list:
            for s in s_list:
                terms += '\t' + str(s['value']) + ' - ' + str(s['distance']) + ' - ' + str(s['score']) + '\n'
        return terms

    for t in tokens:
        if t['isError']:
            errors += f'error -> {t["value"]}\n'
            errors += f'correction -> {t["correction"]}\n'
            errors += f'context -> {" ".join(t["previous_words"])}\n'
            errors += f'context -> {" ".join(t["forwards_words"])}\n'
            errors += get_suggestions(t["suggestions"])
            errors += '\n'

    return errors

########################################################################
############################ PUBLIC FUNCTIONS ##########################
########################################################################

def get_similarity_between_files(dirname1, filename1, dirname2, filename2, measure_type):
    """Calcula la similitud entre los archivos indicados.
    """
    if measure_type: validate_measure(measure_type)

    str1 = fh.read_file(dirname1, filename1)
    str2 = fh.read_file(dirname2, filename2)

    return MEASURES[measure_type](str1, str2)

def get_similarity_between_directories(dirname1, dirname2):
    """Calcula la similitud entre todos los archivos con el mismo nombre
    pertenecientes a los directorios indicados.
    Devuelve los resultados como un diccionario de la forma:
        { filename: 'ex.txt', ratio: 123, jaccard: 123 }
    """

    files_in_dir1 = fh.read_directory_files(dirname1)
    files_in_dir2 = fh.read_directory_files(dirname2)

    files_in_common = utils.intersection(files_in_dir1, files_in_dir2)

    similarities = []
    for f in files_in_common:
        ratio = get_similarity_between_files(dirname1, f, dirname2, f, 'ratio')
        jaccard = get_similarity_between_files(dirname1, f, dirname2, f, 'jaccard')
        similarities.append({ 'filename': f, 'ratio': ratio, 'jaccard': jaccard })

    return similarities

def save_similarities_results(dirname, results, filename=None):
    """Guarda los resultados de la similitud.
    Asume que los datos siguen el formato devuelto por get_similarity_between_directories().
    Si no recibe nombre del archivo en el cual guardar genera uno con el timestamp actual.
    """
    filename = filename if filename else f'{int(time.time() * 100)}.csv'
    fh.write_csv_file(dirname, filename, ['filename', 'ratio', 'jaccard'], results)

def save_postprocessor_results(dirname, filename, result, original_text):
    """Guarda los resultados del postprocessor.
    Espera recibir un objeto con la misma estructura que el devuelto por las funciones de
    procesamiento.
    """
    # corrected_text = result["corrected_text"]
    corrected_text = text_generator.generate_text(original_text, result['tokens'])
    ngrams_result = format_ngrams(result['tokens'])

    fh.write_file(dirname, filename, corrected_text)
    fh.write_file(dirname, f'ngrams_{filename}', ngrams_result)

def save_correct_split_word_by_newline_results(dirname, filename, result):
    """Guarda los resultados del correct_bigram.
    Espera recibir un objeto con la misma estructura que el devuelto por las funciones de
    procesamiento.
    """
    changes = ''

    first_word = ''
    find_first_word = False
    second_word = ''
    find_second_word = False
    for elem in result['tokens']:
        if elem['isFirstPart']:
            first_word = elem['value']
            find_first_word = True
        if elem['isSecondPart']:
            second_word = elem['value']
            find_second_word = True
            correction_word = elem['correction']
        if find_first_word and find_second_word:
            changes += f'first_word -> {first_word}\n'
            changes += f'second_word -> {second_word}\n'
            changes += f'correction -> {correction_word}\n'
            changes += '\n'
            find_first_word = False
            find_second_word = False
            first_word = ''
            second_word = ''

    fh.write_file(dirname, f'correct_split_word_by_newline_{filename}', changes)

def get_column_means(dirname, filename, columns=[1,2]):
    # Lee el csv
    df = fh.read_csv_file(dirname, filename)

    means = {}
    for column_index in columns:
        means.update({df.columns[column_index]: None})



def csv_to_latex_table(dirname, filename, columns_to_compare=[1,2], columns_to_show=[0,1,2]):
    df = fh.read_csv_file(dirname, filename, dtype="object")
    return dataframe_to_latex_table(df, columns_to_compare)

def dataframe_to_latex_table(df, columns_to_compare=[1,2], columns_to_show=[0,1,2]):

    for row_index, row in df.iterrows():
        row_values = [ (df.columns[column_index], row[df.columns[column_index]])  for column_index  in columns_to_compare ]

        best_row_score = max(row_values, key=lambda item: item[1])[1]

        for res in row_values:
            if res[1] == best_row_score:
                df.at[row_index, res[0]] = "\cellcolor{yellow!60}" + str(round(float(res[1]), 6))


    headers = [ df.columns[column_index] for column_index in columns_to_show]
    not_show = utils.difference(df.columns, headers)
    df = df.drop(columns=not_show)

    latex_table = tabulate(df, headers=headers, tablefmt='latex_raw', showindex=False)

    fh.write_file('local_results_evaluation', 'comp_all_in_one_latex.txt', latex_table)

    return latex_table



def get_best_columns(dirname, filename, columns_to_compare=[1,2], output_filename='comp_most_wins.csv'):
    # Lee el csv
    df = fh.read_csv_file(dirname, filename)

    best_results = {}
    for column_index in columns_to_compare:
        best_results.update({df.columns[column_index]: 0})

    for index, row in df.iterrows():
        row_values = [ (df.columns[column_index], row[df.columns[column_index]])  for column_index  in columns_to_compare ]

        best_row_score = max(row_values, key=lambda item: item[1])[1]

        for res in row_values:
            if res[1] == best_row_score:
                best_results[res[0]] += 1

    if 'filename' in df.columns:
        df = df.drop(columns=['filename'])
        df.astype('float64')

    fh.write_csv_file(dirname, output_filename, df.columns.tolist(), [best_results])

def plot_csv_file(dirname, filename, columns_to_compare=[1,2]):
    """Grafica un csv como gráfica de barras.
       El eje X será el número de fila.
       El eje Y serán los valores de las columnas a comparar.
    """

    # Lee el csv
    df = fh.read_csv_file(dirname, filename)

    # Define el eje X como una lista de enteros igual al número de filas
    number_of_rows = df.shape[0]
    x_values = list(range(0, number_of_rows))

    # Genera una gráfica de barras para cada columna indicada del csv
    bar_charts = []
    for i, column_index in enumerate(columns_to_compare):
        column_name = df.columns[column_index]
        y_values = df[column_name]
        color=COLORS[i]

        bar_charts.append(go.Bar(
            x=x_values,
            y=y_values,
            name=column_name,
            marker_color=color
        ))

    # Se genera la figura en dónde se renderizarán las gráficas
    fig = go.Figure()

    # Se agregan las gráficas de barras generadas previamente
    for bc in bar_charts:
        fig.add_trace(bc)

    # Se renderiza el gráfico completo
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.show()


def compare_configurations(file_names=[], output_file_name='comp_all_in_one.csv'):
    df = fh.merge_csvs(
        dirname='local_results_evaluation',
        file_names=file_names,
        merge_on_column='filename',
        usecols=['filename', 'ratio'],
        dtype='object'
    )

    fh.write_file('local_results_evaluation', output_file_name, df.to_csv(index=False))
    return df

def describe_results(filename, output_filename='comp_all_in_one_metrics.csv'):
    df = fh.read_csv_file('local_results_evaluation', filename)
    # pdb.set_trace()
    fh.write_file('local_results_evaluation', output_filename, df.describe().to_csv())

def plot_describe(fileanme):
    df = fh.read_csv_file('local_results_evaluation', fileanme)
    # pdb.set_trace()
    df.describe().iloc[1].plot()
    df.describe().iloc[1].to_csv
    plt.show()

def write_file(dirname, filename, content):
    fh.write_file(dirname, filename, content)

def compare_line_by_line(source, target):
    os.system(os.getcwd() + '../../Bleualign/bleualign.py -s ' + source + ' -t ' + target + '-o ' + source)
