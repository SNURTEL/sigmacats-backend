from os.path import dirname, basename, isfile, join
import glob

"""
This files contains all the necessary setup for models to work correctly
"""

# this allows to do `from app.models import *`
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
