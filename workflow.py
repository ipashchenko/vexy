#!/usr/bin/python2
# -*- coding: utf-8 -*-

from vex import Vex
from datetime import timedelta, datetime
#from insert import insert
import ftplib


def get_vex_for_exp(obscode, host=None, username=None, passwd=None,
                    remote_dir='/schedule/grtsched'):
    """
    Function that fetches all vex-files from user-specified directories and
    it's subdirectories.
    """

    def find_subdirs():
        """
        Function that returns subdirs of current directory.
        """
        dirs = list()

        def _lambda(line):
            if line[0] == 'd':
                dirs.append(line.split()[-1])

        ftp.dir('-d', _lambda)
        try:
            dirs.remove('.')
            dirs.remove('..')
        except ValueError:
            pass
        if not dirs:
            print 'No sudirectories in ' + ftp.pwd()
        return dirs

    def get_vex_from_curdir():
        """
        Function that finds fex-files in current directory.
        """
        # Find vex-files in current directory and in it's subdirectories
        cwd_files = ftp.nlst()
        # Check for vex-files among cwd_files
        vex_files = [file_ for file_ in cwd_files if '.vex' in file_]
        if not vex_files:
            print 'No vex-files in directory ' + ftp.pwd()
        else:
            # Get found vex-files
            for file_ in vex_files:
                print 'Downloading ' + file_
                with open(file_, "wb") as vexfile:
                    ftp.retrbinary('RETR %s' % file_, vexfile.write)

    def get_vex_from_nested_dirs(directory):
        ftp.cwd(directory)
        curdir = directory
        get_vex_from_curdir()
        dirs = find_subdirs()
        print 'Found subdirectories:'
        print dirs
        if not dirs:
            pass
        else:
            for dir_ in dirs:
                curdir = directory + '/' + dir_
                print 'Go to ' + curdir
                ftp.cwd(curdir)
                get_vex_from_nested_dirs(curdir)

    ftp = ftplib.FTP(host, username, passwd)
    get_vex_from_nested_dirs(remote_dir)


def parse_vex(fname):
    """
    Function that parses vex-files and returns data to be inserted to ra_db.
    """

    out = Vex(fname)

    # Find experiment code and check it is one
    assert(len(out['EXPER'].items()) == 1)
    obscode = out['EXPER'].items()[0][0]

    scans = list()
    # Populate list of scan#
    for key in out['SCHED'].iterkeys():
        scans.append(key)

    # Populate each scan with info
    # Loop for earch scan
    for scan in scans:
        mode = out['SCHED'][scan]['mode']
        start = out['SCHED'][scan]['start']
        source = out['SCHED'][scan]['source']

        # Loop for each telescope in scan
        for tel in [tel[0] for tel in
                    out['SCHED'][scan].getall('station')]:
            length = [station[2] for station in
                      out['SCHED'][scan].getall('station') if station[0] ==
                      tel][0]
            freq_setup = [freq[0] for freq in out['MODE'][mode].getall('FREQ')
                          if freq[1] == tel][0]
            if_setup = [freq[0] for freq in out['MODE'][mode].getall('IF')
                          if freq[1] == tel][0]
            bbc = [bbcs[0] for bbcs in out['MODE'][mode].getall('BBC') if
                   bbcs[1] == tel][0]
            # IF = [res[0] for res in out['MODE'][mode].getall('IF') if res[1]
            #       == tel]
            # Loop for each channel
            for chan in [chans_info[4] for chans_info in
                         out['FREQ'][freq_setup].getall('chan_def')]:
                chan_frequency =\
                            [chans_info[1] for chans_info in
                                    out['FREQ'][freq_setup].getall('chan_def')
                                    if chans_info[4] == chan][0]
                chan_LU = [chans_info[2] for chans_info in
                                    out['FREQ'][freq_setup].getall('chan_def')
                                    if chans_info[4] == chan][0]
                chan_BW = [chans_info[3] for chans_info in
                                    out['FREQ'][freq_setup].getall('chan_def')
                                    if chans_info[4] == chan][0]
                chan_BBC = [chans_info[5] for chans_info in
                                    out['FREQ'][freq_setup].getall('chan_def')
                                    if chans_info[4] == chan][0]

                # Decrypt BBC:
                num, IF_type = [(res[1], res[2]) for res in
                                out['BBC'][bbc].getall('BBC_assign') if
                                res[0] == chan_BBC][0]
                pol = [res[2] for res in out['IF'][if_setup].getall('if_def')
                       if res[0] == IF_type][0]
                # It isn't U/L
                #ul = [res[4] for res in out['IF'][if_setup].getall('if_def') if res[0] == IF_type][0]

                #print scan, tel, start, length, freq_setup, if_setup, bbc,\
                        #        chan, chan_frequency, chan_LU, chan_BW, chan_BBC, num, IF_type,\
                        #pol
                result = list()

                # Obscode is ``string``
                obscode_str = obscode
                # Scan number to ``int``
                scan_int = int(scan[2:])
                # source is ``string``
                source_str = source
                # Telescope is ``string``
                tel_str = tel
                # Starttime of scan to ``datetime``
                fmt = '%Yy%jd%Hh%Mm%Ss'
                start_dt = datetime.strptime(start, fmt)
                #start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                # Length of scan to timedelta
                length_dt = timedelta(seconds=float(length.split()[0]))
                # Channel # to ``int``
                chan_int = int(chan[-1])
                # Sky frequency to float
                chan_frequency_fl = float(chan_frequency.split()[0])
                # Lower/Upper channelis ``string``
                chan_LU_str = chan_LU
                # Channel bandwidth to ``float``
                chan_BW_fl = float(chan_BW.split()[0])
                # Polarization is ``string``
                pol_str = pol

                result = obscode_str, source_str, tel_str, scan_int, start_dt,\
                    length_dt, chan_frequency_fl, chan_BW_fl, chan_int,\
                    chan_LU_str, pol_str
    return result
