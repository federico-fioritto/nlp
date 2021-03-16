import os
import itertools as it
import re
import pdb
from difflib import SequenceMatcher

"""
Return a measure of the sequences' similarity as a float in the range [0, 1].

Where T is the total number of elements in both sequences, and M is the number of matches, this is 2.0*M / T. Note that this is 1.0 if the sequences are identical, and 0.0 if they have nothing in common.
"""

DIR = '/home/dlabs/tesis-local-files/important-files/ratio_evaluation/'
CANT_OF_TESTS = 15
IGNORED_ELEMENTS = " \t\r\n"
STYLE = ['\\textbf{\\textcolor{red}', '\\textbf{\\textcolor{red}']

def test_names(test_number):
    return f'test_{test_number}_a', f'test_{test_number}_b', f'test_{test_number}_desc'

def test_contents(test_number):
    test_name_a, test_name_b, test_name_desc = test_names(test_number)
    test_cont_a = open(DIR+test_name_a, "r").read()
    test_cont_b = open(DIR+test_name_b, "r").read()
    test_desc = open(DIR+test_name_desc, "r").read()
    return test_cont_a, test_cont_b, test_desc

def should_ignore_element(elem):
    return elem in IGNORED_ELEMENTS

def calculate_ratio(cont_1, cont_2):
    seq.set_seqs(cont_1, cont_2)
    return seq.ratio()

def calculate_matching_blocks(cont_a, cont_b):
    matches = seq.get_matching_blocks()
    matches_in_a = cont_a
    matches_in_b = cont_b
    carriage = 0
    for idx, match in enumerate(matches):
        if match.size == 0: continue
        begin_a = match.a + carriage
        begin_b = match.b + carriage
        end_a = match.a + match.size + carriage
        end_b = match.b + match.size + carriage
        style = STYLE[idx%2]
        matches_in_a = matches_in_a[0:begin_a] + style + '{' + matches_in_a[begin_a:end_a] + '}}' + matches_in_a[end_a:]
        matches_in_b = matches_in_b[0:begin_b] + style + '{' + matches_in_b[begin_b:end_b] + '}}' + matches_in_b[end_b:]
        carriage += len(style) + 3

    matches_in_a = matches_in_a.replace(" ", "\hspace{5bp}")
    matches_in_a = matches_in_a.replace("\n", "\\\\")
    matches_in_a = matches_in_a.replace("\t", "\hspace{5bp}")
    matches_in_b = matches_in_b.replace(" ", "\hspace{5bp}")
    matches_in_b = matches_in_b.replace("\n", "\\\\")
    matches_in_b = matches_in_b.replace("\t", "\hspace{5bp}")

    return matches, matches_in_a, matches_in_b

def create_test_files(initial_test_number, final_test_number):
    for i in range(initial_test_number, final_test_number + 1):
        os.mknod(f"{DIR}test_{i}_a")
        os.mknod(f"{DIR}test_{i}_b")

def create_test_descriptions(initial_test_number, final_test_number):
    for i in range(initial_test_number, final_test_number + 1):
        os.mknod(f"{DIR}test_{i}_desc")




def main():
    global seq
    seq = SequenceMatcher(isjunk=None, autojunk=False)

    examples = os.listdir(DIR)

    for test_number in range(1, CANT_OF_TESTS + 1):
        test_cont_a, test_cont_b, test_desc = test_contents(test_number)

        diff = calculate_ratio(test_cont_a, test_cont_b)
        mblocks, matches_in_a, matches_in_b = calculate_matching_blocks(test_cont_a, test_cont_b)


        print("test " + str(test_number) + ": " + test_desc)
        # print(test_cont_a)
        # print(test_cont_b)
        print(diff)
        print(matches_in_a)
        print("\n")
        print(matches_in_b)
        print("\n")
        print(mblocks)
        print('----------')

main()
# create_test_files(11, 15)
# create_test_descriptions(1, 15)
