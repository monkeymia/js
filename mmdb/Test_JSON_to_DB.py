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

import JSON_to_DB
import JSONLoadError
# cString has no unicode support
import cStringIO
import unittest
import StringIO


class Test_JSON_to_DB(unittest.TestCase):

    db_name = "unit_test_json_to_db"

    def setUp(self):
        self.jtd = JSON_to_DB.JSON_to_DB()
        d = """
[
    { "table" : "General"
    , "columns" :
        [ { "name" : "doc"
          , "type" : "INT"
          , "doc"  : "user visible documentation."
          }
        , { "name" : "test1"
          , "type" : "VARCHAR(255)"
          , "doc"  : "user visible documentation."
          }
        , { "name" : "test2"
          , "type" : "VARCHAR(255)"
          , "doc"  : "user visible documentation."
          }
        ]
    }
]
"""

        self.data = StringIO.StringIO(d)
    # end def

    def test_convert(self):
        result = self.jtd.convert(self.data, self.db_name)
        self.assertTrue(result)
        result = self.jtd.db.pwd_db()
        self.assertTrue(result)
        self.assertEqual(result.singleton(), self.db_name)
        result = self.jtd.db.ls_cols("General")
        self.assertTrue("test1" in result.rows)
    # end def

    def test_convert_e1(self):
        self.assertRaises(
            JSONLoadError.JSONLoadError, self.jtd.convert, None, self.db_name
            )
    # end def

    def test_convert_e2(self):
        d = cStringIO.StringIO("[]")
        self.assertRaises(
            JSONLoadError.JSONLoadError, self.jtd.convert, d, self.db_name
            )
    # end def

    def test_load_from_file(self):
        result = self.jtd.load_from_file(self.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(isinstance(result[0], dict))
    # end def

    def test_load_from_file_e1(self):
        self.assertRaises(
            JSONLoadError.JSONLoadError, self.jtd.load_from_file, None
            )
    # end def

    def tearDown(self):
        self.jtd.db.rm_db(self.db_name)
    # end def

# end class

if __name__ == '__main__':
    unittest.main()
# __END__
