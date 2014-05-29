import unittest
import os
import zipfile

from elixir import utils


class MemoryFileLikeTests(unittest.TestCase):

    def test_instanciating(self):

        self.assertEqual(utils.MemoryFileLike('picles.txt')._file_name, 'picles.txt')

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