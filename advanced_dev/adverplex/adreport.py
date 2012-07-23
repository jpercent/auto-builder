#!/usr/bin/env python

import logging
import logging.config

try:
    logging.config.fileConfig('logger.config')
except:
    pass
logging.config.string

import re
import csv
import sys
import datetime
from optparse import OptionParser

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

def set_logger_level(log_level):
    logger.setLevel(log_level)

def to_cents(s):
    s = s.split('$')
    if len(s) != 2:
        logger.error('to_cents: formatting error')
        assert False
    s = s[1].split('.')
    if len(s) != 2:
        logger.error('to_cents: decimal error')
        assert False
    cents = int(s[0]+s[1])
    logger.debug('to_cents: '+str(cents))
    return cents

def to_pkey(s):
    if s == '':
        logger.error('pkey_str: primary key cannot be empty')
        assert False
    return str(s).lower() 

def to_int(s):
    return int(s)

def default_format():
    # inputformat = ((name, converstion function), ... )
    df = (('ad_group', to_pkey) , ('ad_name', to_pkey), ('impressions', to_int),
        ('clicks', to_int), ('crt', None), ('total_cost_in_cents', to_cents))
    return df

class Parameters:
    def __init__(self):
        self.args = None
        self.options = None
        self.format = None
        self.input = None
        self.output_file = None        
        self.parser = OptionParser(version="%prog 1.3.37")

        format_file_help = 'optional file that overides the default file format'
        input_file_help = 'file to use as input; uses standard in by default'
        output_file_help = 'file to use as output; uses standard out by default'
        loglevel_help = 'set the logging level; valid values are debug, info, '\
                        'warn, error and critical; defaults to warning'

        self.parser.add_option("-f", "--format-file", default='', type=str,
                               dest="format_file", metavar="FORMAT", 
                               help=format_file_help)
        self.parser.add_option("-i", "--input-file", default='', type=str,
                               dest="input_file", metavar="INPUT", 
                               help=input_file_help)
        self.parser.add_option("-o", "--output-file", default='', type=str,
                               dest="output_file", metavar="OUTPUT", 
                               help=output_file_help)        
        self.parser.add_option('-l', '--logging-level', dest='loglevel',
                               metavar='LEVEL', help=loglevel_help)

        (self.options, self.args) = self.parser.parse_args()
        
        valid_levels = { 'debug' : logging.DEBUG, 'info' : logging.INFO,
                         'warn' : logging.WARN, 'error' : logging.ERROR,
                         'critical' : logging.CRITICAL}          
          
        if self.options.loglevel != None and self.options.loglevel in valid_levels:
            set_logger_level(valid_levels[self.options.loglevel])
        else:
            if self.options.loglevel:
                logger.error('Invalid log level: '+self.options.loglevel+ \
                             ' using default, which is WARN')
            set_logger_level(logging.WARN)

        if self.options.format_file != '':
            logger.debug(self.options.format_file)
            try:
               self.format = open(self.options.format_file, 'r+').readlines()                
            except:
                logger.debug('error opening format file = '+str(self.format))            
                self.format = None
        
        if not self.format or self.format:
            logger.debug('format file not supported yet; using default')
            self.format = default_format()
            logger.debug('format = '+str(self.format))            
            
            
        if self.options.input_file != '':
            logger.debug(self.options.input_file)
            try:
                self.input = open(self.options.input_file, 'rb').readlines()
            except:
                logger.debug('exception opening input file; using stdin')
                self.input = None
                
        if not self.input:
            self.input = sys.stdin.readlines()
        logger.debug('input = '+str(self.input))
            
        if self.options.output_file != '':
            try:
                self.output_file = open(self.options.output_file, 'wb')
            except:
                self.output_file = sys.stdout                
        else:
            self.output_file = sys.stdout
        #self.output_file.write('awwwwwwwwww yeah')
        
class AdReport:
    # check for a valid date
    def date(self, dstr):
        dstr = dstr.split(':')
        if len(dstr) != 2:
            return False, None
        if re.search('date', dstr[0].lower()) and len(dstr[1].split('/')) == 3:
            dstr = dstr[1].split('/')
            logger.debug(dstr)
            try:
                b = int(dstr[0])
                b = int(dstr[1])
                b = int(dstr[2])
                date = dstr[2].strip()+'-'+dstr[0].strip()+'-'+dstr[1].strip()
            except:
                logger.debug('AdReport.date: failed parsing date:' + str(dstr))
                return False, None
        return True, date
            
    def scrub_attr(self, raw_attr, format, line):
        if not format[1]:
            return True
        try:
            assert format[1]
            field = format[1](raw_attr)
        except:
            logger.warn('AdReport.scrub_attr: formatting exception '+\
                        str(raw_attr)+str(format))
            return False
        line.append(field)
        return True
            
    def parse(self, format, input):
        csv_reader = csv.reader(input)
        date_found = False
        output = []
        for tuple in csv_reader:
            line = []
            line.append('date place holder')
            if len(tuple) == 1 and not date_found:
                date_found, date = self.date(tuple[0])
                line = None
                continue
                
            elif len(tuple) != len(format):
                logger.warn('AdReport.parse: attribute count '+str(len(tuple))+\
                            ', but expected '+str(len(format))+\
                            '; skipping malformed line')
                line = None
                continue
                
            for index in range(0, len(tuple)):
                valid = self.scrub_attr(tuple[index], format[index], line)
                if not valid:
                    line = None
                    break
            if line:
                output.append(line)
            
        if not date_found:
            date = str(datetime.date.today())
            logger.warn('AdReport.parse: date not given, using today\'s date = '+\
                        date)
        for row in output:
            row[0] = date
            logger.debug(row)
        return output
        
    def write(self, output, format, output_file):
        csv_writer = csv.writer(output_file, lineterminator='\n')
        # python 2.6 doesn't support csv_writer.writeheader and the header is
        # written differently then the rows, so the header is written "by hand."
        header = []
        header = '\xef\xbb\xbfreport_date'
        for i in format:
            if i[1]:
                header += ', '+ i[0]
        header += '\n'
        #csv_writer.writerow(header)
        output_file.write(header)
        csv_writer.writerows(output)        

if __name__ == '__main__':
    p = Parameters()
    adreport = AdReport()
    output = adreport.parse(p.format, p.input)
    adreport.write(output, p.format, p.output_file)
    


