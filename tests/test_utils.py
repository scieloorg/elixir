import unittest
import os
import zipfile

from elixir import utils

source_dir = None


def setupModule():
    global document_xml, document_json, source_dir

    source_dir = os.path.dirname(__file__) + '/files'


class UtilsTests(unittest.TestCase):

    def test_wrap_files_when_instanciating(self):

        wrap_files = utils.WrapFiles(
            source_dir+'/html/rsp/v40n6/en_07.htm',
            source_dir+'/pdf/rsp/v40n6/07.pdf',
            source_dir+'/pdf/rsp/v40n6/en_07.pdf',
            source_dir+'/img/rsp/v40n6/07f1.gif',
        )

        self.assertTrue('en_07.htm' in wrap_files.thezip.namelist())
        self.assertTrue('07.pdf' in wrap_files.thezip.namelist())
        self.assertTrue('en_07.pdf' in wrap_files.thezip.namelist())
        self.assertTrue('07f1.gif' in wrap_files.thezip.namelist())

    def test_wrap_files(self):

        wrap_files = utils.WrapFiles()
        in_memory = wrap_files.append(
            source_dir+'/html/rsp/v40n6/en_07.htm',
            source_dir+'/pdf/rsp/v40n6/07.pdf',
            source_dir+'/pdf/rsp/v40n6/en_07.pdf',
            source_dir+'/img/rsp/v40n6/07f1.gif',
        )

        self.assertTrue('en_07.htm' in in_memory.namelist())
        self.assertTrue('07.pdf' in in_memory.namelist())
        self.assertTrue('en_07.pdf' in in_memory.namelist())
        self.assertTrue('07f1.gif' in in_memory.namelist())

    def test_wrap_files_with_file_like_object(self):
        flo = utils.MemoryFileLike('blaus.txt', 'picles content')

        wrap_files = utils.WrapFiles()
        in_memory = wrap_files.append(
            source_dir+'/html/rsp/v40n6/en_07.htm',
            source_dir+'/pdf/rsp/v40n6/07.pdf',
            flo,
            source_dir+'/img/rsp/v40n6/07f1.gif',
        )

        self.assertTrue('en_07.htm' in in_memory.namelist())
        self.assertTrue('07.pdf' in in_memory.namelist())
        self.assertTrue('blaus.txt' in in_memory.namelist())
        self.assertTrue('07f1.gif' in in_memory.namelist())

    def test_wrap_files_invalid_path(self):

        with self.assertRaises(FileNotFoundError):
            wrap_files = utils.WrapFiles()
            wrap_files.append(
                source_dir+'/html/rsp/v40n6/en_07.htm',
                source_dir+'/invalid/pdf/rsp/v40n6/07.pdf'
            )


class MemoryFileLikeTests(unittest.TestCase):

    def test_instanciating(self):

        self.assertEqual(
            utils.MemoryFileLike('picles.txt')._file_name,
            'picles.txt'
        )

    def test_instanciating(self):

        with self.assertRaises(TypeError):
            self.assertEqual(utils.MemoryFileLike(123))

    def test_read(self):

        flo = utils.MemoryFileLike('picles.txt', 'content')

        self.assertEqual(flo.read(), 'content')

    def test_write_read(self):

        flo = utils.MemoryFileLike('picles.txt', 'content')

        flo.write('blaus')

        self.assertEqual(flo.read(), 'contentblaus')

    def test_writeln_read(self):

        flo = utils.MemoryFileLike('picles.txt', 'content')

        flo.writelines('blaus')

        self.assertEqual(flo.read(), 'content\r\nblaus')

    def test_writeln_read(self):

        flo = utils.MemoryFileLike('picles.txt', 'content')

        flo.writelines('blaus', 'picles')

        self.assertEqual(flo.read(), 'content\r\nblaus\r\npicles')

    def test_name_read(self):

        flo = utils.MemoryFileLike('picles.txt', 'content')

        flo.write('blaus')

        self.assertEqual(flo.name, 'picles.txt')