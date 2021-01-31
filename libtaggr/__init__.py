''' this does most of the parsing and editing work '''
import re
import sys

__version__ = '0.2.8'
__doc__ = ''
__all__ = []

from . import pytaggr
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(pytaggr.main())
