import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import s2
from s2 import api, models
from s2.db import JsonS2PaperDB, JsonS2AuthorDB
from s2.store import JsonDS
from s2.graph import S2Graph
from s2.graph import (GraphHopper, MaxHopHopper, MaxPaperHopper, BowtieHopper,
                      LivingLitReviewHopper)
from s2.graph import S2GraphBuilder
from pathlib import Path


def rm_tree(pth: Path):
    """ Utility for removing directory recursively"""
    pth = Path(pth)
    if pth.exists():
        if pth.is_file():
            pth.unlink()
        else:
            for child in pth.glob('*'):
                if child.is_file():
                    child.unlink()
                else:
                    rm_tree(child)
            pth.rmdir()