from dotenv import load_dotenv
load_dotenv()
from modules.postprocessor import Postprocessor

post = Postprocessor()

post.load_vocabulary("vocabulary1.4.txt")

post.save_sysmspell("vocabulary1.4.pkl")