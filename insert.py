#!/usr/bin/python2
# -*- coding: utf-8 -*-

import psycopg2
from workflow import parse_vex


def insert(values, columns='obscode, source, telescope, scan, start, duration, freq, bw, chan, bbc, pol',
           database='ra_db', user=None, password=None,
           table='database_vex', host='odin.asc.rssi.ru', port='5432'):
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

    cur.execute("INSERT INTO database_vex (obscode, source, telescope, scan,\
            start, duration, freq, bw, chan, bbc, pol) VALUES (%s, %s, %s, %s,\
                    %s, %s, %s, %s, %s, %s, %s)", tuple(values))
    connection.commit()


class VexInserter(object):

    def __init__(self, database='ra_db', user=None, password=None,
                 table='database_vex', host='odin.asc.rssi.ru', port='5432',
                 columns='obscode, source, telescope, scan, start, duration,\
                         freq, bw, chan, bbc, pol'):
        self._connection = psycopg2.connect(database=database, user=user,
                                  password=password, host=host, port=port)
        self._cur = self._connection.cursor()

    def insert_1vex(self, fname, commit=False):

        values = parse_vex(fname)
        self._cur.execute("INSERT INTO database_vex (obscode, source, telescope, scan,\
            start, duration, freq, bw, chan, bbc, pol) VALUES (%s, %s, %s, %s,\
                    %s, %s, %s, %s, %s, %s, %s)", tuple(values))
        if commit:
            self._connection.commit()

    def insert_vexes(self, fnames):

        for fname in fnames:
            self.insert_1vex(fname)

        self._connection.commit()
