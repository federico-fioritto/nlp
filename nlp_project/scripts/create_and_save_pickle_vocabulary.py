from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append("..")
# from modules.postprocessor import Postprocessor
from modules.postprocessor import Postprocessor

VOCABULARY = 'vocabulary1.5.txt'
PICKLE_NAME = 'vocabulary1.5.pkl'


post = Postprocessor()
post.load_vocabulary(VOCABULARY)
post.save_sysmspell(PICKLE_NAME)
