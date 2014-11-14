#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# https://github.com/monkeymia/
#
# Copyright (c) 2014, monkeymia, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library
#

import DB_Query_Result
import unittest


class Test_DB_Query_Result(unittest.TestCase):

    def setUp(self):
        pass
    # end def

    def test_init(self):
        dbq = DB_Query_Result.DB_Query_Result()
        self.assertEqual(str(dbq), "lc=0,lr=0,rc=0,le=0")
    # end def

    def test_init2(self):
        dbq = DB_Query_Result.DB_Query_Result(1)
        self.assertEqual(str(dbq), "lc=0,lr=0,rc=1,le=0")
    # end def

    def test_col(self):
        dbq = DB_Query_Result.DB_Query_Result()
        dbq.cols = [1, 2, 3]
        self.assertEqual(str(dbq), "lc=3,lr=0,rc=0,le=0")
    # end def

    def test_row(self):
        dbq = DB_Query_Result.DB_Query_Result()
        dbq.rows = [1, 2, 3]
        self.assertEqual(str(dbq), "lc=0,lr=3,rc=0,le=0")
    # end def

    def test_errors(self):
        dbq = DB_Query_Result.DB_Query_Result()
        dbq.errors = [1, 2, 3]
        self.assertEqual(str(dbq), "lc=0,lr=0,rc=0,le=3")
    # end def

    def test_singleton(self):
        dbq = DB_Query_Result.DB_Query_Result()
        dbq.rows = [("11", "12", "13"), ]
        self.assertEqual(dbq.singleton(), "11")
    # end def

    def test_singleton1(self):
        dbq = DB_Query_Result.DB_Query_Result()
        dbq.rows = []
        self.assertRaises(NotImplementedError, dbq.singleton)
    # end def

    def test_nonzero(self):
        dbq = DB_Query_Result.DB_Query_Result()
        self.assertFalse(dbq)
        dbq.rowcount = 1
        self.assertTrue(dbq)
    # end def

    def tearDown(self):
        pass
    # end def

# end class

if __name__ == '__main__':
    unittest.main()
# __END__
