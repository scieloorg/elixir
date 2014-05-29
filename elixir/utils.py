from io import StringIO


class MemoryFileLike(object):

    def __init__(self, file_name, content=None):

        if not isinstance(file_name, str):
            raise TypeError('file_name must be a string')

        self._file_name = file_name
        self._content = StringIO()

        if content:
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
