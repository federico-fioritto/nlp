
import os
config = """from symspellpy.symspellpy import Verbosity 
  
max_edit_distance_dictionary = 6
 
def edc(word_len):
    if word_len <= 3: return 1
    if word_len <= 6: return 2
    if word_len <= 10: return 3
    return 4

edit_distance_conf = edc

suggestion_verbosity = Verbosity.CLOSEST

ngram = 3

parallel_phrasefinder_requests = 1000

"""
i = 1
original_config = config

os.system('mkdir ./configs')
os.system('mkdir ./configs/luisa_split')
os.system('mkdir ./configs/luisa_join')
os.system('mkdir ./configs/luisa_split/google')
os.system('mkdir ./configs/luisa_split/billion')
os.system('mkdir ./configs/luisa_join/google')
os.system('mkdir ./configs/luisa_join/billion')
os.system('mkdir ./configs/luisa_split/google/elmo_voc')
os.system('mkdir ./configs/luisa_split/google/own_voc')
os.system('mkdir ./configs/luisa_split/billion/elmo_voc')
os.system('mkdir ./configs/luisa_split/billion/own_voc')
os.system('mkdir ./configs/luisa_join/google/elmo_voc')
os.system('mkdir ./configs/luisa_join/google/own_voc')
os.system('mkdir ./configs/luisa_join/billion/elmo_voc')
os.system('mkdir ./configs/luisa_join/billion/own_voc')


for voc in ['vocabulary1.5.pkl', 'elmo_vocabulary.pkl']:
    for cuc in ['False','True']:
        for cucfl in ['False','True']:
            for pswbn in ['split','join','not_process']:
                for cd in ['forward','previous','middle','all']:
                    for lm in ['google','1_billion']:
                        for csw in ['any_line','same_line','not_process']:
                            config += "vocabulary = '" + voc + "'\n\n"
                            config += "correct_upper_case = " + cuc + "\n\n"
                            config += "correct_upper_case_first_letter = " + cucfl + "\n\n"
                            config += "process_split_word_by_newline = \"" + pswbn + "\"\n\n"
                            config += "context_direction = \"" + cd + "\"\n\n"
                            config += "language_model = \"" + lm + "\"\n\n"
                            config += "correct_split_word = \"" + csw + "\""

                            # fAll = open("./configs/config"+ str(i)+".py", "w+")
                            # fAll.write(config)
                            # fAll.close()

                            if (pswbn == "join"):
                                if (lm == 'google'):
                                    if voc == "vocabulary1.5.pkl":
                                        f = open("./configs/luisa_join/google/own_voc/config"+ str(i)+".py", "w+")    
                                    else: 
                                        f = open("./configs/luisa_join/google/elmo_voc/config"+ str(i)+".py", "w+")
                                else:
                                    if voc == "vocabulary1.5.pkl":
                                        f = open("./configs/luisa_join/billion/own_voc/config"+ str(i)+".py", "w+")    
                                    else: 
                                        f = open("./configs/luisa_join/billion/elmo_voc/config"+ str(i)+".py", "w+")
                                f.write(config)
                                f.close()
                            else:
                                if (lm == 'google'):
                                    if voc == "vocabulary1.5.pkl":
                                        f = open("./configs/luisa_split/google/own_voc/config"+ str(i)+".py", "w+")    
                                    else: 
                                        f = open("./configs/luisa_split/google/elmo_voc/config"+ str(i)+".py", "w+")
                                else:
                                    if voc == "vocabulary1.5.pkl":
                                        f = open("./configs/luisa_split/billion/own_voc/config"+ str(i)+".py", "w+")    
                                    else: 
                                        f = open("./configs/luisa_split/billion/elmo_voc/config"+ str(i)+".py", "w+")
                                f.write(config)
                                f.close()
                            i += 1
                            config = original_config