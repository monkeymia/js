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
import MySQLdb
import os
import os.path
import DB_Query_Result
import JSON_to_DB


# please read sql tutorial:
#  http://www.tutorialspoint.com/mysql/mysql-like-clause.htm
class DB_Interface(object):
    # Wrapper to encapsulate SQL Statements and SQL Server.
    # A wrapper helps to reduce the risk of unwanted SQL injections.
    #
    #
    # Assumptions:
    # * Somebody outside may change sql database - no cache
    # * primary key is table name lower case
    # * primary key is conform to ANSI-C variable format i.e string length 30
    # * value NULL forbidden - helps to make client code easier
    # * no protection against stupid client code. for example after creation
    #   use database must be called.
    #
    FORMAT_AS_HTML_TABLE = 1
    FORMAT_AS_CSV = 2
    FORMAT_AS_LEN = 3
    FORMAT_AS_USER = 4
    FORMAT_AS_REPR = 5
    FORMAT_AS_FIRST = 6
    FORMAT_AS_PY = 7
    # file extension of database description files
    extension_json = ".json"
    # holds sql server connection for all instances of DB interface
    _connection = None
    # enable sql query debugging - helps for unit test creation
    _debug_me = False
    # Hide SQL Server specific system tables
    _internal_dbs = ("information_schema", "mysql", "performance_schema")
    # defautl sql server language.
    _sql_lang = "MySQL"
    # avoid duplicate code. grep is your friend.
    _sql_pwd_db_cmd = "SELECT DATABASE();"

    def __init__(self, sql_lang=None):
        if sql_lang:
            self._sql_lang = sql_lang
        if self.__class__._connection is None:
            # it seems no utf8 in /usr/share/mysql/charsets/
            # charset='latin1',
            self.__class__._connection = MySQLdb.Connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                passwd="root",
                charset="utf8"
                )
    # end def

    def clear_dbs(self):
        # after this call no database is selected !
        result = self.ls_dbs()
        rows = result.rows
        for db in rows:
            if result:
                result = self.rm_db(db)
        return result
    # end

    def close(self):
        cmd = getattr(self.__class__._connection, "close")
        if callable(cmd):
            self.__class__._connection = None
            cmd()
    # end

    def del_row(self, table_name, key, del_all=False):
        if del_all:
            sql = "DELETE FROM %s;" % (table_name)
            return self._sql_runner(sql)
        else:
            pk = self._primary_key(table_name)
            if not self.has_row(table_name, key):
                raise NotImplementedError(
                    "Error (del_row): row does not exists (%s) (%s)"
                    % (table_name, key)
                    )
            sql = "DELETE FROM %s WHERE %s=\"%s\";" % (table_name, pk, key)
            return self._sql_runner(sql)
    # end def

    def get_row(self, table_name, key, cols=[]):
        pk = self._primary_key(table_name)
        if cols:
            sql = (
                "SELECT %s FROM %s WHERE %s=\"%s\";"
                % (",".join(cols), table_name, pk, key)
                )
        else:
            sql = "SELECT * FROM %s WHERE %s=\"%s\";" % (table_name, pk, key)
        return self._sql_runner(sql, cols=cols)
    # end def

    def has_row(self, table_name, key):
        pk = self._primary_key(table_name)
        sql = "SELECT %s FROM %s WHERE %s=\"%s\";" % (pk, table_name, pk, key)
        res = self._sql_runner(sql)
        return res
    # end def

    def ls_dbs(self):
        sql = "SHOW DATABASES;"
        result = self._sql_runner(sql, cols=["Database"], flat=True)
        for db in self._internal_dbs:
            try:
                result.rows.remove(db)
            except ValueError, e:
                result.errors.append(
                    "Error (ls_dbs): Cannot remove internal db %s (%s)."
                    % (db, e)
                    )
        return result
    # end def

    def ls_layouts(self):
        # return possible database definitions...
        result = DB_Query_Result.DB_Query_Result(zero_is_valid_rowcount=True)
        rows = []
        path = os.path.dirname(__file__)
        ext = self.extension_json.lower()
        try:
            for f in os.listdir(path):
                if f.lower().endswith(ext):
                    rows.append(str(f[:(-len(ext))]))
        except (OSError, IOError), e:
            result.errors.append(
                "Cannot list files (*.%s). - Details: %s"
                % (ext, e)
                )
        result.cols = ["layout"]
        result.rows = rows
        return result
    # end def

    def ls_cols(self, table_name):
        # sql = "SHOW COLUMNS FROM %s;" % (table_name, ) returns:
        # +------------+--------------+------+-----+---------+-------+
        # | Field      | Type         | Null | Key | Default | Extra |
        # +------------+--------------+------+-----+---------+-------+
        # | general_id | varchar(36)  | NO   | PRI | NULL    |       |
        # | doc        | int(11)      | NO   |     | NULL    |       |
        # | test1      | varchar(255) | NO   |     | NULL    |       |
        # | test2      | varchar(255) | NO   |     | NULL    |       |
        # +------------+--------------+------+-----+---------+-------+
        # MYSQL Specific !!!
        if self._sql_lang == "MySQL":
            sql = (
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "where TABLE_NAME = '%s'"
                % (table_name, )
                )
        else:
            raise NotImplementedError(
                "SQL Language (%s) is not supported!" % self._sql_lang)
        return self._sql_runner(
            sql, cols=["COLUMN_NAME"], flat=True, zero_is_valid=True)
    # end def

    def ls_rows(self, table_name, cols=[]):
        if not cols:
            result = self.ls_cols(table_name)
            if not result:
                return result
            cols = result.rows
        sql = "SELECT %s FROM %s;" % (",".join(cols), table_name, )
        return self._sql_runner(sql, cols=cols, zero_is_valid=True)
    # end def

    def ls_tables(self):
        sql = "SHOW TABLES;"
        return self._sql_runner(sql, cols=["TABLES"], flat=True)
    # end def

    def mk_db(self, db_name):
        res = self.rm_db(db_name, silent=True)
        if res:
            sql = "CREATE DATABASE %s;" % db_name
            res = self._sql_runner(sql)
        return res
    # end def

    def mk_table(self, table_name, columns):
        # MYSQL Specific !!!
        if self._sql_lang == "MySQL":
            pk = self._primary_key(table_name)
            s = "%s VARCHAR(36) NOT NULL," % (pk, )
            for col in sorted(columns):
                e = col["type"]
                n = col["name"]
                s += "%s %s NOT NULL," % (n, e)
            s += "PRIMARY KEY (%s)" % (pk, )
            sql = "CREATE TABLE %s(%s);" % (table_name, s)
        else:
            raise NotImplementedError(
                "SQL Language (%s) is not supported!" % self._sql_lang)
        return self._sql_runner(sql, zero_is_valid=True)
    # end def

    def new_db(self, db_name, layout):
        result = DB_Query_Result.DB_Query_Result(zero_is_valid_rowcount=True)
        path = os.path.dirname(__file__)
        fname = os.path.join(
            path, db_name, "%s%s" % (layout, self.extension_json))
        if os.path.exists(fname):
            jtd = JSON_to_DB.JSON_to_DB()
            result = jtd.convert(fname, layout)
        else:
            result.errors.append(
                "Error (new_db): file not found - Details : %s"
                % (fname, )
                )
        return result
    # end def

    def new_row(self, table_name, key, values_dct={}):
        if not values_dct:
            raise NotImplementedError(
                "Error (new_row): No Values specified. (%s) (%s)"
                % (table_name, key)
                )
        pk = self._primary_key(table_name)
        cols = [pk]
        vals = ["\"%s\"" % key]
        for k, v in sorted(values_dct.iteritems()):
            cols.append("%s" % k)
            vals.append("%s" % v)
        sql = (
            "INSERT INTO %s (%s) VALUES (%s);"
            % (table_name, ",".join(cols), ",".join(vals))
            )
        return self._sql_runner(sql, cols=cols)
    # end def

    def set_row(self, table_name, key, values_dct={}):
        if not values_dct:
            raise NotImplementedError(
                "Error (new_row): No Values specified. (%s) (%s)"
                % (table_name, key)
                )
        pk = self._primary_key(table_name)
        if not self.has_row(table_name, key):
            result = self.new_row(table_name, key, values_dct)
        else:
            cmd = []
            for k, v in sorted(values_dct.iteritems()):
                cmd.append("%s=%s" % (k, v))
            sql = (
                "UPDATE %s SET %s WHERE %s=\"%s\";"
                % (table_name, ",".join(cmd), pk, key)
                )
            result = self._sql_runner(sql)
        return result
    # end def

    def pwd_db(self):
        sql = self._sql_pwd_db_cmd
        return self._sql_runner(sql, cols=["Database()"], flat=True)
    # end def

    def rm_db(self, db_name, silent=False):
        sql = "DROP DATABASE %s %s;" % ("IF EXISTS" if silent else "", db_name)
        return self._sql_runner(sql, flat=True, zero_is_valid=True)
    # end def

    def rm_table(self, table_name):
        sql = "DROP TABLE %s;" % table_name
        return self._sql_runner(sql, zero_is_valid=True)
    # end def

    def use_db(self, db_name):
        sql = "USE %s;" % (db_name, )
        return self._sql_runner(sql, zero_is_valid=True)
    # end def

    def _format_tuples(self, cursor, req, fmt, **kw):
        row_start_hook = kw.get("row_start_hook", None)
        row_end_hook = kw.get("row_end_hook", None)
        col_hook = kw.get("col_hook", None)
        fetcher = getattr(cursor, "fetchall", None)
        if callable(fetcher):
            rows = cursor.fetchall()
        else:
            rows = cursor
        if fmt == self.FORMAT_AS_HTML_TABLE:
            for row in rows:
                req.write("  <tr>\n")
                for col in row:
                    req.write("    <td>" + str(col) + "<td>\n")
                req.write("  </tr>\n")
        elif fmt == self.FORMAT_AS_CSV:
            for row in rows:
                req.write("\"%s\n\"" % ",".join(col for col in row))
        elif fmt == self.FORMAT_AS_LEN:
            l = len(rows)
            req.write("%s" % l)
        elif fmt == self.FORMAT_AS_REPR:
            req.write(str(rows))
        elif fmt == self.FORMAT_AS_FIRST:
            for row in rows:
                for col in row:
                    req.write(str(col))
                    return
        elif fmt == self.FORMAT_AS_PY:
            for row in rows:
                r = []
                for col in row:
                    r.append(col)
                req.append(r)
        elif fmt == self.FORMAT_AS_USER:
            for row in rows:
                if callable(row_start_hook):
                    row_start_hook()
                for col in row:
                    if callable(row_start_hook):
                        col_hook(col)
                if callable(row_end_hook):
                    row_end_hook()
        else:
            raise NotImplementedError(fmt)
    # end def

    def _primary_key(self, table_name):
        return "%s_id" % (table_name.lower(), )
    # end def

    def _sql_runner(self, sql, cols=[], flat=False, zero_is_valid=False):
        result = DB_Query_Result.DB_Query_Result(
            zero_is_valid_rowcount=zero_is_valid)
        cursor = self.__class__._connection.cursor()
        try:
            if __debug__ and self.__class__._debug_me:
                print sql
            rowcount = cursor.execute(sql)
            valid = True
        except:
            valid = False
            rowcount = 0
            # avoid recursive calls:
            if self._sql_pwd_db_cmd not in sql:
                result_pwd = self.pwd_db()
                if result_pwd.singleton():
                    msg = (
                        "Error(sql_runner):execute sql failed - "
                        "Wrong syntax ? (%s)!!"
                        % (sql,)
                        )
                else:
                    msg = (
                        "Error(sql_runner):execute sql failed - "
                        "use database missing ?"
                        )
            else:
                msg = (
                    "Error(sql_runner):execute pwd_db failed. (%s)!!"
                    % (sql,)
                    )
            result.errors.append(msg)
        result.rowcount = rowcount
        if valid:
            result.cols = cols
            result.rows = []
            for row in cursor.fetchall():
                if flat:
                    result.rows.append(row and row[0])
                else:
                    result.rows.append(row)
                lr = len(row)
                lc = len(cols)
                if lc and lr != lc:
                    result.errors.append(
                        "Error(sql_runner):len rows  (%s) and len cols "
                        "(%s) do not match!" % (lr, lc)
                        )
        if __debug__ and self.__class__._debug_me:
            print "=>", str(result), str(result.cols), \
                str(result.rows), str(result.errors)
        return result
    # end def

# end class
# __END__
