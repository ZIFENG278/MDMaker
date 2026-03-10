from utils.build_db import BuildDB
from setting import *
a = BuildDB(repo_docs_path)
a.forward(api=True, show_db=False)
