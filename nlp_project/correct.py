from dotenv import load_dotenv
load_dotenv()

from modules.preprocessor import Preprocessor
from modules.postprocessor import Postprocessor
from modules.language_model import LanguageModel
from modules.process_format_errors import ProcessFormatError
import helpers.final_text_generator as text_generator
import modules.results_evaluator as results_evaluator
from symspellpy.symspellpy import SymSpell, Verbosity
from nltk import word_tokenize, sent_tokenize
import time
import argparse
from nltk.corpus import cess_esp
import os
import helpers.file as fh
import helpers.utils as utils
import config

lm = None
post = None
pfe = None

# Private
def build_script_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--document", required=False)
    return arg_parser.parse_args()

def process_file(filename):
    ocr_output = fh.read_file(dir_ocr_outputs, filename)

    result_after_regex = post.process_with_regex(ocr_output)

    text_to_procces = result_after_regex

    #USO DE FLAG process_split_word_by_newline
    flag_pswbn = config.process_split_word_by_newline
    if flag_pswbn in ("split","join"):
        result_after_pfe = pfe.correct_split_word_by_newline(result_after_regex, flag_pswbn, lm)
        results_evaluator.save_correct_split_word_by_newline_results(dir_step_2, filename, result_after_pfe)
        text_to_procces = text_generator.generate_text_split_words_by_newline(result_after_regex, result_after_pfe['tokens'])


    text_for_split_word_process = text_to_procces

    #USO DE FLAG correct_split_word
    flag_csw = config.correct_split_word
    if (flag_csw in ("any_line","same_line")):
        result_after_pfe_2 = pfe.correct_split_word(text_for_split_word_process)
        text_to_procces = text_generator.generate_text_split_words(text_for_split_word_process, result_after_pfe_2['tokens'])


    fh.write_file(dir_step_1, f'improved_{filename}', text_to_procces)

    result = post.correct_errors_process(text_to_procces, lm)

    results_evaluator.save_postprocessor_results(dir_step_2, filename, result, text_to_procces)

def evaluate_results():
    results = results_evaluator.get_similarity_between_directories(dir_ground_truth, dir_step_2)
    results_evaluator.save_similarities_results(dir_results_evaluation, results)

def process_all_files():
    filenames = fh.read_directory_files(dir_ocr_outputs)
    print('procesando todos los archivos con la config')
    print(config.correct_upper_case, config.correct_upper_case_first_letter, config.process_split_word_by_newline, config.context_direction, config.language_model, config.correct_split_word, config.vocabulary)
    print('cantidad de archivos a procesar: ' + str(len(filenames)))
    for filename in filenames:
        print('archivo: ' + filename + '\n')
        process_file(filename)

# ------------------------------------------------------------------------------- #
def main():
    global lm
    global post
    global pfe
    global dir_step_1
    global dir_step_2
    global dir_ocr_outputs
    global dir_ground_truth
    global dir_results_evaluation

    lm = LanguageModel()
    lm.load_model()

    post = Postprocessor()
    pfe = ProcessFormatError(post, lm)

    dir_step_1 = 'local_step_1_outputs'
    dir_step_2 = 'local_step_2_outputs'
    dir_ocr_outputs = 'local_tesseract_training_outputs'
    dir_ground_truth = 'local_luisa_traductions'
    dir_results_evaluation = 'local_results_evaluation'

    post.load_vocabulary(config.vocabulary)

    # Si no se especifica el archivo a procesar se procesan todos los del directorio de outputs.
    process_file(ARGS.document) if ARGS.document else process_all_files()

    # Evalúa similitud entre todos los archivos
    evaluate_results()

ARGS = build_script_arguments()
main()


