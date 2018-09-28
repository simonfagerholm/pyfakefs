#!/usr/bin/env python
"""
test to verify correct time updates
"""
from __future__ import print_function
from collections import namedtuple
import os
import tempfile
import time
import unittest

from pyfakefs.fake_filesystem_unittest import TestCase

FileTime = namedtuple('FileTime', 'st_ctime, st_atime, st_mtime')

SLEEP_TIME = 0.01


class BaseTestTime(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        for path in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, path))
        os.rmdir(self.test_dir)
        if os.path.exists(self.test_dir):
            print('Cleanup failed')

    @staticmethod
    def stat_time(path):
        stat = os.stat(path)
        # sleep a bit so in the next call the time has changed
        time.sleep(SLEEP_TIME)
        return FileTime(st_ctime=stat.st_ctime,
                        st_atime=stat.st_atime,
                        st_mtime=stat.st_mtime)

    def create_file(self, path, content=''):
        with open(path, 'w') as handle:
            handle.write(content)
        self.assertTrue(os.path.exists(path))


class TestModeW(BaseTestTime):
    def test_open_close_new_file(self):
        """
        When a file is opened with 'w' mode and it doesn't not exist
        the timestamps are not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'w')
        created = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, closed.st_mtime)

    def test_open_write_close_new_file(self):
        """
        When a file is opened with 'w' mode and it doesn't not exist and
        the file is written to the timestamps are updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'w')
        created = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_close(self):
        """
        When a file is opened with 'w' mode and it does already exist
        st_ctime and st_mtime is updated on open (trucating)
        but is not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w')
        opened = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, closed.st_mtime)

    def test_open_write_close(self):
        """
        When a file is opened with 'w' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_flush_close(self):
        """
        When a file is opened with 'w' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w')
        opened = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_write_flush_close(self):
        """
        When a file is opened with 'w' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and flush, but not when written to or when closed.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_read_raises(self):
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        with open(file_path, 'w') as handle:
            with self.assertRaises(IOError):
                handle.read()


class TestModeWPlus(BaseTestTime):
    def test_open_close_new_file(self):
        """
        When a file is opened with 'w+' mode and it doesn't not exist
        the timestamps are not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'w+')
        created = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, closed.st_mtime)

    def test_open_write_close_new_file(self):
        """
        When a file is opened with 'w+' mode and it doesn't not exist and
        the file is written to the timestamps are updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'w+')
        created = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_read_close_new_file(self):
        """
        When a file is opened with 'w+' mode and it doesn't not exist and
        the file is written to the timestamps are updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'w+')
        created = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, closed.st_ctime)

        # st_atime
        self.assertLess(created.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, closed.st_mtime)

    def test_open_close(self):
        """
        When a file is opened with 'w+' mode and it does already exist
        st_ctime and st_mtime is updated on open (trucating)
        but is not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w+')
        opened = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, closed.st_mtime)

    def test_open_write_close(self):
        """
        When a file is opened with 'w+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w+')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_read_close(self):
        """
        When a file is opened with 'w+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w+')
        opened = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertLess(opened.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, closed.st_mtime)

    def test_open_flush_close(self):
        """
        When a file is opened with 'w+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w+')
        opened = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_write_flush_close(self):
        """
        When a file is opened with 'w+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and flush, but not when written to or when closed.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'w+')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertLess(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertLess(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)


class TestModeA(BaseTestTime):
    def test_open_close_new_file(self):
        """
        When a file is opened with 'a' mode and it doesn't not exist
        the timestamps are not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'a')
        created = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, closed.st_mtime)

    def test_open_write_close_new_file(self):
        """
        When a file is opened with 'a' mode and it doesn't not exist and
        the file is written to the timestamps are updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'a')
        created = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_close(self):
        """
        When a file is opened with 'a' mode and it does already exist
        st_ctime and st_mtime is updated on open (trucating)
        but is not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a')
        opened = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, closed.st_mtime)

    def test_open_write_close(self):
        """
        When a file is opened with 'a' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_flush_close(self):
        """
        When a file is opened with 'a' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a')
        opened = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_write_flush_close(self):
        """
        When a file is opened with 'a' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and flush, but not when written to or when closed.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_read_raises(self):
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        with open(file_path, 'a') as handle:
            with self.assertRaises(IOError):
                handle.read()


class TestModeAPlus(BaseTestTime):
    def test_open_close_new_file(self):
        """
        When a file is opened with 'a+' mode and it doesn't not exist
        the timestamps are not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'a+')
        created = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, closed.st_mtime)

    def test_open_write_close_new_file(self):
        """
        When a file is opened with 'a+' mode and it doesn't not exist and
        the file is written to the timestamps are updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'a+')
        created = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(created.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_read_close_new_file(self):
        """
        When a file is opened with 'a+' mode and it doesn't not exist and
        the file is written to the timestamps are updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        handle = open(file_path, 'a+')
        created = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(created.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, closed.st_ctime)

        # st_atime
        self.assertLess(created.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(created.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, closed.st_mtime)

    def test_open_close(self):
        """
        When a file is opened with 'a+' mode and it does already exist
        st_ctime and st_mtime is updated on open (trucating)
        but is not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a+')
        opened = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, closed.st_mtime)

    def test_open_write_close(self):
        """
        When a file is opened with 'a+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a+')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_read_close(self):
        """
        When a file is opened with 'a+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a+')
        opened = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertLess(opened.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, closed.st_mtime)

    def test_open_flush_close(self):
        """
        When a file is opened with 'a+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a+')
        opened = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_write_flush_close(self):
        """
        When a file is opened with 'a+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and flush, but not when written to or when closed.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'a+')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)


class TestModeR(BaseTestTime):
    def test_open_close(self):
        """
        When a file is opened with 'r' mode and it does already exist
        st_ctime and st_mtime is updated on open (trucating)
        but is not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r')
        opened = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, closed.st_mtime)

    def test_open_read_close(self):
        """
        When a file is opened with 'r' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r')
        opened = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertLess(opened.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, closed.st_mtime)

    def test_open_flush_close(self):
        """
        When a file is opened with 'r' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r')
        opened = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_read_flush_close(self):
        """
        When a file is opened with 'r' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and flush, but not when written to or when closed.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r')
        opened = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertLess(opened.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_not_existing_raises(self):
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        with self.assertRaises(IOError):
            with open(file_path, 'r') as handle:
                pass


class TestModeRPlus(BaseTestTime):
    def test_open_close(self):
        """
        When a file is opened with 'r+' mode and it does already exist
        st_ctime and st_mtime is updated on open (trucating)
        but is not updated on close.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r+')
        opened = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, closed.st_mtime)

    def test_open_read_close(self):
        """
        When a file is opened with 'r+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r+')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, closed.st_mtime)

    def test_open_write_close(self):
        """
        When a file is opened with 'r+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r+')
        opened = self.stat_time(file_path)

        handle.read()
        read = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, read.st_ctime)
        self.assertEquals(read.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertLess(opened.st_atime, read.st_atime)
        self.assertEquals(read.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, read.st_mtime)
        self.assertEquals(read.st_mtime, closed.st_mtime)

    def test_open_flush_close(self):
        """
        When a file is opened with 'r+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and again on close (flush), but not when written to.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r+')
        opened = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_write_flush_close(self):
        """
        When a file is opened with 'r+' mode and it does already exist
        and is then written to st_ctime and st_mtime is updated on open
        (trucating) and flush, but not when written to or when closed.
        """
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')
        self.create_file(file_path)

        # test
        before = self.stat_time(file_path)

        handle = open(file_path, 'r+')
        opened = self.stat_time(file_path)

        handle.write('foo')
        written = self.stat_time(file_path)

        handle.flush()
        flushed = self.stat_time(file_path)

        handle.close()
        closed = self.stat_time(file_path)

        # results
        # st_ctime
        self.assertEquals(before.st_ctime, opened.st_ctime)
        self.assertEquals(opened.st_ctime, written.st_ctime)
        self.assertLess(written.st_ctime, flushed.st_ctime)
        self.assertEquals(flushed.st_ctime, closed.st_ctime)

        # st_atime
        self.assertEquals(before.st_atime, opened.st_atime)
        self.assertEquals(opened.st_atime, written.st_atime)
        self.assertEquals(written.st_atime, flushed.st_atime)
        self.assertEquals(flushed.st_atime, closed.st_atime)

        # st_mtime
        self.assertEquals(before.st_mtime, opened.st_mtime)
        self.assertEquals(opened.st_mtime, written.st_mtime)
        self.assertLess(written.st_mtime, flushed.st_mtime)
        self.assertEquals(flushed.st_mtime, closed.st_mtime)

    def test_open_not_existing_raises(self):
        # setup
        file_path = os.path.join(self.test_dir, 'some_file')

        # test
        with self.assertRaises(IOError):
            with open(file_path, 'r+') as handle:
                pass

