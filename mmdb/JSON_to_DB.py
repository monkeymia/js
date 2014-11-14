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

import DB_Interface
import DB_Query_Result
import JSONLoadError
import codecs
import json
import sys
import StringIO


class JSON_to_DB(object):

    def __init__(self, db=None):
        if db is None:
            self.db = DB_Interface.DB_Interface()
        else:
            self.db = db
    # end def

    def convert(self, fname, db_name):
        res = DB_Query_Result.DB_Query_Result()
        try:
            result = self.load_from_file(fname)
        except JSONLoadError.JSONLoadError:
            raise
        if result:
            res = self.db.mk_db(db_name)
            if res:
                res = self.db.use_db(db_name)
                for table_entry in result:
                    table = table_entry["table"]
                    columns = table_entry["columns"]
                    if res:
                        res = self.db.mk_table(table, columns)
        else:
            raise JSONLoadError.JSONLoadError(
                "File empty. No info loaded. Details:(%s)" % fname
                )
        return res
    # end def

    def load_from_file(self, fname):
        result = None
        f = None
        # cStringIO is a C Wrapper and isinstance does not work as expected
        if (
           isinstance(fname, StringIO.StringIO)
           or (
                fname.__class__.__name__ in ("StringIO", "StringO", "StringI")
                )
           ):
            f = fname
        else:
            try:
                f = codecs.open(fname, encoding="utf-8")
            except (IOError, TypeError), e:
                raise JSONLoadError.JSONLoadError(
                    "Cannot load %s. Details: %s" % (fname, e)
                    )
        if f:
            try:
                try:
                    result = json.load(f, "utf-8")
                    # result = self.cvt_enc (result)
                except (IOError, ValueError), e:
                    raise JSONLoadError.JSONLoadError(
                        "Cannot decode %s. Details: %s" % (fname, e)
                        )
            finally:
                if f:
                    f.close()
        return result
    # end def

    def cvt_enc(self, input):
        # Javascript knows only unicode and therefore JSON parser returns
        # always unicode.
        # If you need python text with default encoding:
        # http://stackoverflow.com/questions/956867/
        # how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
        if isinstance(input, dict):
            if sys.version_info < (3, 0):
                return dict(
                    [(self.cvt_enc(key), self.cvt_enc(value))
                        for key, value in input.iteritems()
                     ]
                    )
            else:
                return {
                    self.cvt_enc(key): (
                        self.cvt_enc(value)
                        for (key, value) in input.iteritems()
                        )
                    }
        elif isinstance(input, list):
            return [self.cvt_enc(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    # end def

# end class

if __name__ == "__main__":
    pass
    # JSON_to_DB().convert("/var/www/html/py/database.json", "foo", sys.stdout)
# __END__
