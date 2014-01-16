#!/usr/bin/python2
# -*- coding: utf-8 -*-

import psycopg2


def insert(columns, values, database='ra_db', user=None, password=None,
           table=None, host='odin.asc.rssi.ru', port='5432'):
    """
    Function to insert the form data 'values' into table 'table' according
    to the columns in 'column'.

    Parameters:

        ``columns`` - iterable of string(s) that are name(s) of the table
            columns,

        ``values`` - iterable of string(s) that are value(s) of the columns.
    """

    connection = psycopg2.connect(database=database, user=user,
                                  password=password, host=host, port=port)
    cur = connection.cursor()

    statement = 'INSERT INTO ' + table + ' (' + columns + ') VALUES (' +\
                values + ')'
    cur.execute(statement)
    connection.commit()
