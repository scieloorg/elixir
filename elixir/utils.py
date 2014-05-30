from io import StringIO, BytesIO
from zipfile import ZipFile
import codecs
import logging


def wrap_files(*args):

    thezip = ZipFile(BytesIO(), 'w')

    for item in args:

        if isinstance(item, MemoryFileLike):
            x = item
        else:
            x = codecs.open(item, 'r', encoding='iso-8859-1')

        name = x.name.split('/')[-1]
        try:
            thezip.writestr(name, x.read())
        except FileNotFoundError:
            logging.info('Unable to prepare zip file, file not found (%s)' % item)
            raise

    logging.info('Zip file prepared')

    return thezip


class MemoryFileLike(object):

    def __init__(self, file_name, content=None):

        if not isinstance(file_name, str):
            raise TypeError('file_name must be a string')

        self._file_name = file_name
        self._content = StringIO()

        if len(content):
            self._content.write(str(content).strip())

    @property
    def name(self):
        return self._file_name

    def write(self, content):
        self._content.write(str(content).strip())

    def writelines(self, *args):
        for line in args:
            self._content.write('\r\n%s' % str(line).strip())

    def read(self):
        return self._content.getvalue()

    def close(self):
        self._content.close()
