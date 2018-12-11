import sys
from pathlib import Path
import site
import pdb

path=Path(__file__).resolve()
docs_dir=path.parent.parent
sys.path.insert(0,path.parent)

