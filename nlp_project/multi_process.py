from dotenv import load_dotenv
load_dotenv()


import importlib
import argparse
import os
import csv
import helpers.file as fh
import helpers.utils as utils
import helpers.final_text_generator as text_generator
import modules.results_evaluator as results_evaluator

lm = None
post = None
pfe = None

# Variables para almacenar los directorios dependiendo si usamos los ejemplos subidos
# o los ejemplos que tenemos locales.
dir_step_1 = None
dir_step_2 = None
dir_ocr_outputs = None
dir_ground_truth = None
dir_results_evaluation = None

# Private
def build_script_arguments():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("-d", "--document", required=False)
  arg_parser.add_argument("-l", "--language", required=False)
  arg_parser.add_argument("-use_examples", "--use_uploaded_examples", required=False, action='store_true')
  arg_parser.add_argument("-v", "--vocabulary", required=False)
  # arg_parser.add_argument("-sw", "--split_word", required=False, action='store_true')
  # arg_parser.add_argument("-jsw", "--join_split_word", required=False, action='store_true')
  return arg_parser.parse_args()

def process_file(filename):
  import config
  from modules.process_format_errors import ProcessFormatError
  importlib.reload(config)

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
  return results_evaluator.get_similarity_between_directories(dir_ground_truth, dir_step_2)
  # results_evaluator.save_similarities_results(dir_results_evaluation, results)

def process_all_files():
    filenames = fh.read_directory_files(dir_ocr_outputs)
    print('procesando todos los archivos')
    print(len(filenames))


    for filename in filenames:
      print(filename)
      if filename.endswith('.txt'):
        process_file(filename)
      else:
        print('no proceso file')

def save_csv(data, dire):
  with open (dire, mode='w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['filename', 'ratio', 'jaccard'])
    writer.writeheader()
    for data in data:
      writer.writerow(data)
# ------------------------------------------------------------------------------- #
def main():
  if (os.path.exists(os.getcwd() + '/multi_process/fin.txt')) :
    print('LISTO')
  else :
    global lm
    global post
    global pfe
    global dir_step_1
    global dir_step_2
    global dir_ocr_outputs
    global dir_ground_truth
    global dir_results_evaluation

    os.system('mkdir ' + os.getcwd() + '/docs/outputs/step1/')
    os.system('mkdir ' + os.getcwd() + '/docs/outputs/step2/')
    os.system('mkdir ' + os.getcwd() + '/multi_process/results/')

    from modules.language_model import LanguageModel
    from modules.process_format_errors import ProcessFormatError
    first = [f for f in os.listdir(os.getcwd() + '/multi_process/configs/') if not f.startswith('.')][0]
    print(first)
    filename = first.split('/')[-1].split('.')[0]
    os.system('cp multi_process/configs/' + filename + '.py config.py')

    import config
    print(config.correct_upper_case, config.correct_upper_case_first_letter, config.process_split_word_by_newline, config.context_direction, config.language_model, config.correct_split_word, config.vocabulary)
    importlib.reload(config)
    from modules.postprocessor import Postprocessor
    lm = LanguageModel()
    lm.load_model()
    post = Postprocessor()
    pfe = ProcessFormatError(post, lm)


    if ARGS.use_uploaded_examples:
      dir_step_1 = 'improved_outputs'
      dir_step_2 = 'post_processed_wiki' if config.use_own_language_model else 'post_processed_google'
      dir_ocr_outputs = 'outputs'
      dir_ground_truth = 'manual_corrections'
      dir_results_evaluation = 'results'
    else:
      dir_step_1 = 'local_step_1_outputs'
      dir_step_2 = 'local_step_2_outputs'
      dir_ocr_outputs = 'local_tesseract_training_outputs'
      dir_ground_truth = 'local_luisa_traductions'
      dir_results_evaluation = 'local_results_evaluation'

    post.load_vocabulary(config.vocabulary)

    for filepath in os.listdir(os.getcwd() + '/multi_process/configs/'):
      if filepath.endswith('.py'):
        filename = filepath.split('/')[-1].split('.')[0]

        result_filename = os.getcwd() + '/multi_process/results/' + filename + '.csv'

        # SI NO EXISTE El ARCHIVO
        if not os.path.exists(result_filename):
          os.system('cp multi_process/configs/' + filename + '.py config.py')



          importlib.reload(config)

          print('CONFIG:')
          print(config.correct_upper_case, config.correct_upper_case_first_letter, config.process_split_word_by_newline, config.context_direction, config.language_model, config.correct_split_word, config.vocabulary)
          # lm = LanguageModel()
          # post = Postprocessor()
          # pfe = ProcessFormatError(post, lm)

          print('--------------------------')
          print('Inicio ' + filename)

          process_all_files()

          # Evalúa similitud entre todos los archivos
          results = evaluate_results()
          save_csv(results, result_filename)

          # Guardo archivos step1 y step2 por config
          os.system('mkdir ' + os.getcwd() + '/multi_process/' + filename + '_step1/')
          os.system('mkdir ' + os.getcwd() + '/multi_process/' + filename + '_step2/')
          os.system('mv ' + os.getcwd() + '/docs/outputs/step1/* ' + os.getcwd() + '/multi_process/' + filename + '_step1/')
          os.system('mv ' + os.getcwd() + '/docs/outputs/step2/* ' + os.getcwd() + '/multi_process/' + filename + '_step2/')

          print('Fin ' + filename)

    os.system('touch multi_process/fin.txt')

ARGS = build_script_arguments()
main()
