#!/usr/bin/env python
#
#    This module contains the unit tests for the auto builder tools.
#
#    Authtor: James Percent (james@empty-set.net)
#    Copyright 2010, 2011 James Percent
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
import pdb
import sys
from os.path import join

sys.path.append('../.')

import auto_builder
import dependencies
import generator
import manifest
from auto_builder import *
from dependencies import *
from manifest import *
from generator import *
#import conf

auto_builder.set_logger_level(logging.WARN)

class ParametersTest(unittest.TestCase):
    def testLogLevels(self):
        import conf
        conf.library_path = [os.getcwd()]
        conf.source_path = [os.getcwd()]        
        params = auto_builder.Parameters()
        self.assertEquals(logging.WARN, auto_builder.logger.getEffectiveLevel())
        
        sys.argv = [sys.argv[0], '-l', 'debug']
        params = auto_builder.Parameters()
        self.assertEquals(logging.DEBUG, auto_builder.logger.getEffectiveLevel())
        
        sys.argv = [sys.argv[0], '-l', 'info']
        params = auto_builder.Parameters()
        self.assertEquals(logging.INFO, auto_builder.logger.getEffectiveLevel())
        
        sys.argv = [sys.argv[0], '-l', 'warn']
        params = auto_builder.Parameters()
        self.assertEquals(logging.WARN, auto_builder.logger.getEffectiveLevel())
        
        sys.argv = [sys.argv[0], '-l', 'error']
        params = auto_builder.Parameters()
        self.assertEquals(logging.ERROR, auto_builder.logger.getEffectiveLevel())
        
        sys.argv = [sys.argv[0], '-l', 'critical']
        params = auto_builder.Parameters()
        self.assertEquals(logging.CRITICAL, auto_builder.logger.getEffectiveLevel())
    
        sys.argv = [sys.argv[0], '-l', 'notaloglevel']
        params = auto_builder.Parameters()
        self.assertEquals(logging.WARN, auto_builder.logger.getEffectiveLevel())
        
        sys.argv = [sys.argv[0], '-l', 'stillnotaloglevel']
        params = auto_builder.Parameters()
        self.assertEquals(logging.WARN, auto_builder.logger.getEffectiveLevel())
    
    def testConfException(self):
        sys.argv = [sys.argv[0], '-p', '.:../', '-s', '.']
        params = auto_builder.Parameters()
        self.assertEquals('.:../', params.options.library_path)
        self.assertEquals('.', params.options.source_path)
        self.assertEquals(['.', '../'], params.options.jar_path)
        self.assertEquals(['.'], params.options.src_path)

        caught = False
        try:
            sys.argv = [sys.argv[0], '-p', '.']
            params = auto_builder.Parameters()
        except Exception as e:
            caught = True
        self.assertEquals(True, caught)

        caugth = False
        try:
            sys.argv = [sys.argv[0], '-s', '.']
            params = auto_builder.Parameters()
        except Exception as e:
            caught = True
        self.assertEquals(True, caught)
        
        import conf
        conf.library_path = ['testlib']
        conf.source_path = ['fuckedpath']
        sys.argv = [sys.argv[0], '-s', str(os.getcwd())]
        params = auto_builder.Parameters()
        self.assertEquals('', params.options.library_path)
        self.assertEquals(str(os.getcwd()), params.options.source_path)
        self.assertEquals(['testlib'], params.options.jar_path)
        self.assertEquals([str(os.getcwd())], params.options.src_path)
        
    def testOptions(self):
        import conf
        conf.library_path = [os.getcwd()]
        conf.source_path = [os.getcwd()]
        conf.project_name = ''
        sys.argv = [sys.argv[0], '-j']
        params = auto_builder.Parameters()
        self.assertEquals(True, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(False, params.options.build_gen)
        self.assertEquals('', params.options.library_path)
        self.assertEquals('', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-j', '-d']
        params = auto_builder.Parameters()
        self.assertEquals(True, params.options.display_jars)
        self.assertEquals(True, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(False, params.options.build_gen)
        self.assertEquals('', params.options.library_path)
        self.assertEquals('', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-c']
        params = auto_builder.Parameters()
        self.assertEquals(False, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(True, params.options.check_dep)
        self.assertEquals(False, params.options.build_gen)
        self.assertEquals('', params.options.library_path)
        self.assertEquals('', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-b']
        params = auto_builder.Parameters()
        self.assertEquals(False, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(True, params.options.build_gen)
        self.assertEquals('', params.options.library_path)
        self.assertEquals('', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-b', '-p', '.']
        params = auto_builder.Parameters()
        self.assertEquals(False, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(True, params.options.build_gen)
        self.assertEquals('.', params.options.library_path)
        self.assertEquals('', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-j', '-s', '.']
        params = auto_builder.Parameters()
        self.assertEquals(True, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(False, params.options.build_gen)
        self.assertEquals('', params.options.library_path)
        self.assertEquals('.', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-j', '-s', '.', '-p', '.']
        params = auto_builder.Parameters()
        self.assertEquals(True, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(False, params.options.build_gen)
        self.assertEquals('.', params.options.library_path)
        self.assertEquals('.', params.options.source_path)
        self.assertEquals('', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-b', '-n', 'james-r0x0rz']
        params = auto_builder.Parameters()
        self.assertEquals(False, params.options.display_jars)
        self.assertEquals(False, params.options.display_src)
        self.assertEquals(False, params.options.check_dep)
        self.assertEquals(True, params.options.build_gen)
        self.assertEquals('', params.options.library_path)
        self.assertEquals('', params.options.source_path)
        self.assertEquals('james-r0x0rz', params.options.project_name)
        
        sys.argv = [sys.argv[0], '-j']
        
        conf.library_path = 'lkjadslfjks#1@@!@!!%%(@*!*!()(0adflajjaldf'
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertTrue(caught)
        
        conf.library_path = '.'
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertFalse(caught)
        
        conf.source_path = 'lkjadslfjks#1@@!@!!%%(@*!*!()(0adflajjaldf'
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertTrue(caught)
        
        conf.source_path = '.'
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertFalse(caught)
        
        bad_name = 'alkdfjoi?##@!#*!?91039102*Ulkajdlfaj8ie'
        sys.argv = [sys.argv[0], '-j', '-s',
                    bad_name, '-p', '.']
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertTrue(caught)

        sys.argv = [sys.argv[0], '-j', '-s',
                    bad_name, '-p', bad_name]
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertTrue(caught)


        sys.argv = [sys.argv[0], '-j', '-s', '.', '-p', bad_name]
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertTrue(caught)

        sys.argv = [sys.argv[0], '-j', '-s', '.', '-p', '.']
        caught = False
        try:
            params = auto_builder.Parameters()
        except:
            caught = True
        self.assertFalse(caught)


if __name__ == '__main__':
    unittest.main()
    
