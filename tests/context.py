import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import s2
from s2 import api, models
from s2.db.json import JsonS2PaperDB, JsonS2AuthorDB