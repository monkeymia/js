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


class DB_Query_Result(object):

    cols = ()
    rows = ()
    rowcount = 0
    error = ()
    zero_is_valid_rowcount = False

    def __init__(self, count=0, zero_is_valid_rowcount=False):
        self.rowcount = count
        self.cols = []
        self.rows = []
        self.errors = []
        self.zero_is_valid_rowcount = zero_is_valid_rowcount
    # end def

    def __nonzero__(self):
        # indicate if valid (no error) has occured.
        if self.errors:
            return False
        elif self.rowcount == 0 and not self.zero_is_valid_rowcount:
            return False
        else:
            return True
    # end def

    def __str__(self):
        return (
            "lc=%s,lr=%s,rc=%s,le=%s" % (
                len(self.cols),
                len(self.rows),
                self.rowcount,
                len(self.errors)
                )
            )
    # end def

    def singleton(self):
        # return first element of first row
        if len(self.rows):
            r = self.rows[0]
            if isinstance(r, list):
                res = r[0]
            elif isinstance(r, tuple):
                res = r[0]
            else:
                # flat result
                res = r
        else:
            raise NotImplementedError("This cannot work %s" % self.rows)
        return res
    # end def

# end class
# __END__
