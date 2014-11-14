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
# To make it work in Ubuntu:
# sudo apt-get install python-pip
# sudo apt-get install python-dev
# sudo pip install coverage
# sudo pip install nose
# sudo pip install flake8
#
# run tests with:
# nosetests --with-coverage Test*.py
# flake8 *.py --show-source --statistics --select=E
#
# run tests with html output:
# nosetests --with-coverage --cover-html Test*.py
#
# Delete trailing whitespaces: sed -i.bak 's/[[:blank:]]*$//' "$1"
#
#

import DB_Interface
import unittest
import StringIO


class Test_DB_Interface(unittest.TestCase):

    db_name = "unit_test_db_interface"
    table_name = "table_test_db_interface"

    def setUp(self):
        self.db = DB_Interface.DB_Interface()
        self.req = StringIO.StringIO()
        res = self.db.clear_dbs()
        self.assertTrue(res)
        res = self.db.mk_db(self.db_name)
        self.assertTrue(res)
        res = self.db.use_db(self.db_name)
        self.assertTrue(res)
        col = []
        col.append({"type": "INT", "name": "col1"})
        col.append({"type": "INT", "name": "col2"})
        col.append({"type": "INT", "name": "col3"})
        res = self.db.mk_table(self.table_name, col)
        self.assertTrue(res)
    # end def

    def test_close(self):
        self.db.close()
        self.assertEqual(self.db.__class__._connection, None)
    # end def

    def test_clear(self):
        self.db.clear_dbs()
        result = self.db.ls_dbs()
        self.assertTrue(result.rowcount > 0)
        self.assertTrue(result)
    # end def

    def test_del_row(self):
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        res = self.db.new_row(self.table_name, "foo", test_vals)
        self.assertTrue(res)
        res = self.db.new_row(self.table_name, "foo1", test_vals)
        self.assertTrue(res)
        res = self.db.del_row(self.table_name, "foo")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertEqual(str(res), "lc=4,lr=1,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.del_row(self.table_name, "foo1")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertEqual(str(res), "lc=4,lr=0,rc=0,le=0")
        self.assertTrue(res)
    # end def

    def test_del_row_all(self):
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        res = self.db.new_row(self.table_name, "foo", test_vals)
        self.assertTrue(res)
        res = self.db.new_row(self.table_name, "foo1", test_vals)
        self.assertTrue(res)
        res = self.db.del_row(self.table_name, None, del_all=True)
        self.assertEqual(str(res), "lc=0,lr=0,rc=2,le=0")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertEqual(str(res), "lc=4,lr=0,rc=0,le=0")
        self.assertTrue(res)
    # end def

    def test_del_row_e1(self):
        # check what happens if no row
        self.assertRaises(
            NotImplementedError, self.db.del_row, self.table_name, "foo")
    # end def

    def test_get_row(self):
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        res = self.db.new_row(self.table_name, "foo", test_vals)
        self.assertEqual(str(res), "lc=4,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertTrue("foo" in res.rows[0])
        self.assertTrue(res)
        res = self.db.get_row(self.table_name, "foo")
        self.assertEqual(str(res), "lc=0,lr=1,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.get_row(self.table_name, "foo", cols=["col1"])
        self.assertEqual(str(res), "lc=1,lr=1,rc=1,le=0")
        self.assertTrue(res)
    # end def

    def test_get_row_e1(self):
        # check what happens if no row
        res = self.db.get_row(self.table_name, "foo")
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=0")
        self.assertFalse(res)
    # end def

    def test_has_row_e1(self):
        # check what happens if no row
        res = self.db.has_row(self.table_name, "foo")
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=0")
        self.assertFalse(res)
    # end def

    def test_ls_layouts_e1(self):
        self.db.extension_json = "invalid_unrealistic_extension"
        res = self.db.ls_layouts()
        self.assertEqual(str(res), "lc=1,lr=0,rc=0,le=0")
        self.assertTrue(res)
    # end def

    def test_ls_dbs(self):
        res = self.db.ls_dbs()
        self.assertTrue(len(res.rows) > 0)
        self.assertTrue(self.db_name in res.rows)
        self.assertTrue(res)
    # end def

    def test_ls_cols(self):
        res = self.db.ls_cols(self.table_name)
        self.assertEqual(str(res), "lc=1,lr=4,rc=4,le=0")
        self.assertTrue("col1" in res.rows)
        self.assertTrue("col2" in res.rows)
        self.assertTrue("col3" in res.rows)
        self.assertTrue(res)
    # end def

    def test_ls_cols_e1(self):
        res = self.db.ls_cols("invalid")
        self.assertEqual(str(res), "lc=1,lr=0,rc=0,le=0")
        self.assertFalse("col1" in res.rows)
        self.assertFalse("col2" in res.rows)
        self.assertFalse("col3" in res.rows)
        self.assertTrue(res)
    # end def

    def test_ls_rows(self):
        res = self.db.ls_rows(self.table_name)
        self.assertEqual(len(res.rows), 0)
        self.assertEqual(str(res), "lc=4,lr=0,rc=0,le=0")
        self.assertTrue(res)
    # end def

    def test_ls_tables(self):
        res = self.db.ls_tables()
        self.assertEqual(len(res.rows), 1)
        self.assertEqual(str(res.singleton()), self.table_name)
        self.assertTrue(res)
    # end def

    def test_mk_db(self):
        res = self.db.mk_db("test2")
        self.assertEqual(str(res), "lc=0,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), self.db_name)
        self.assertTrue(res)
        res = self.db.use_db("test2")
        self.assertTrue(res)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), "test2")
        self.assertTrue(res)
        res = self.db.rm_db("test2")
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=0")
        self.assertTrue(res)
        res = self.db.pwd_db()
        self.assertEqual(res.singleton(), None)
        self.assertTrue(res)
    # end def

    def test_mk_tables(self):
        n = "test_asdf"
        res = self.db.mk_table(n, [])
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=0")
        self.assertTrue(res)
        res = self.db.ls_cols(n)
        self.assertEqual(len(res.rows), 1)  # primary key
        self.assertTrue(res)
        res = self.db.rm_table(n)
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=0")
        self.assertTrue(res)
    # end def

    def test_new_db_e1(self):
        res = self.db.new_db("foo", "invalid_unrealistic_layout")
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
    # end def

    def test_new_row(self):
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        res = self.db.new_row(self.table_name, "foo", test_vals)
        self.assertEqual(str(res), "lc=4,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.has_row(self.table_name, "foo")
        self.assertTrue(res)
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertEqual(str(res), "lc=4,lr=1,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.del_row(self.table_name, "foo")
        self.assertEqual(str(res), "lc=0,lr=0,rc=1,le=0")
        self.assertTrue(res)
    # end def

    def test_new_row_e1(self):
        # if key is too long the new command fails silent.
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        key = "f" * 100
        res = self.db.new_row(self.table_name, key, test_vals)
        self.assertEqual(str(res), "lc=4,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.has_row(self.table_name, key)
        self.assertFalse(res)
        self.assertFalse(res)
    # end def

    def test_set_row(self):
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        res = self.db.set_row(self.table_name, "foo", test_vals)
        self.assertEqual(str(res), "lc=4,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.has_row(self.table_name, "foo")
        self.assertTrue(res)
        self.assertTrue(res)
        res = self.db.del_row(self.table_name, "foo")
        self.assertEqual(str(res), "lc=0,lr=0,rc=1,le=0")
        self.assertTrue(res)
    # end def

    def test_set_row_1(self):
        test_vals = {"col1": 1, "col2": 2, "col3": 3}
        res = self.db.set_row(self.table_name, "foo", test_vals)
        self.assertEqual(str(res), "lc=4,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertTrue("foo" in res.rows[0])
        self.assertTrue(3 in res.rows[0])
        self.assertTrue(res)
        test_vals = {"col1": 1, "col2": 2, "col3": 4}
        res = self.db.set_row(self.table_name, "foo", test_vals)
        self.assertEqual(str(res), "lc=0,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertTrue(4 in res.rows[0])
        self.assertTrue(res)
        test_vals = {"col1": 5, "col2": 6}
        res = self.db.set_row(self.table_name, "foo", test_vals)
        self.assertEqual(str(res), "lc=0,lr=0,rc=1,le=0")
        self.assertTrue(res)
        res = self.db.ls_rows(self.table_name)
        self.assertTrue(4 in res.rows[0])
        self.assertTrue(5 in res.rows[0])
        self.assertTrue(6 in res.rows[0])
        self.assertTrue(res)
    # end def

    def test_pwd_db(self):
        res = self.db.pwd_db()
        self.assertEqual(str(res), "lc=1,lr=1,rc=1,le=0")
        self.assertEqual(str(res.singleton()), self.db_name)
        self.assertTrue(res)
    # end def

    def test_use_db(self):
        res = self.db.use_db(self.db_name)
        self.assertEqual(res.errors, [])
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=0")
        self.assertTrue(res)
        res = self.db.pwd_db()
        self.assertEqual(str(res), "lc=1,lr=1,rc=1,le=0")
        self.assertTrue(res)
    # end def

    def test_use_db_e1(self):
        # Invalid Table name will not change current used table.
        res = self.db.use_db(self.db_name)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), self.db_name)
        self.assertTrue(res)
        res = self.db.use_db(self.table_name)
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), self.db_name)
        self.assertTrue(res)
    # end def

    def test_use_db_e2(self):
        # Invalid Table name will not change current used table.
        res = self.db.use_db(self.db_name)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), self.db_name)
        self.assertTrue(res)
        res = self.db.use_db(None)
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), self.db_name)
        self.assertTrue(res)
    # end def

    def test_use_db_e3(self):
        # check which function works if no selected table.
        db_name = "unit_test_e3"
        table_name = "unit_test_e3_table"
        res = self.db.mk_db(db_name)
        self.assertTrue(res)
        res = self.db.use_db(db_name)
        self.assertTrue(res)
        res = self.db.rm_db(db_name)
        self.assertTrue(res)
        res = self.db.pwd_db()
        self.assertEqual(str(res.singleton()), str(None))
        self.assertTrue(res)
        res = self.db.mk_table(table_name, {})
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
        res = self.db.ls_rows(table_name)
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
        res = self.db.ls_cols(table_name)
        self.assertEqual(str(res), "lc=1,lr=0,rc=0,le=0")
        self.assertTrue(res)
        res = self.db.ls_tables()
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
        res = self.db.rm_table(table_name)
        self.assertEqual(str(res), "lc=0,lr=0,rc=0,le=1")
        self.assertFalse(res)
    # end def

    def tearDown(self):
        # res = self.db.rm_db(self.db_name)
        pass
    # end def

# end class

if __name__ == '__main__':
    unittest.main()
# __END__
