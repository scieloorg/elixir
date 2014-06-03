from io import StringIO, BytesIO
from zipfile import ZipFile
import codecs
import logging


class WrapFiles(object):
    def __init__(self, *args):
        self.memory_zip = BytesIO()
        self.thezip = ZipFile(self.memory_zip, 'a')

        if len(args) > 0:
            self.append(*args)

    def append(self, *args):

        for item in args:

            if isinstance(item, MemoryFileLike):
                x = item
            else:
                x = codecs.open(item, 'rb')

            name = x.name.split('/')[-1]
            try:
                self.thezip.writestr(name, x.read())
            except FileNotFoundError:
                logging.info('Unable to prepare zip file, file not found (%s)' % item)
                raise

        logging.info('Zip file prepared')

        return self.thezip

    def read(self):
        self.thezip.close()
        self.memory_zip.seek(0)
        return self.memory_zip.read()


class MemoryFileLike(object):

    def __init__(self, file_name, content=None, encoding='utf-8'):

        if not isinstance(file_name, str):
            raise TypeError('file_name must be a string')

        self._encoding = encoding
        self._file_name = file_name
        self._content = StringIO(encoding)

        if len(content):
            self._content.write(content.strip())

    @property
    def name(self):
        return self._file_name

    def write(self, content):
        self._content.write(content.strip())

    def writelines(self, *args):
        for line in args:
            self._content.write('\r\n%s' % str(line).strip())

    def read(self):
        return self._content.getvalue()

    def close(self):
        self._content.close()
