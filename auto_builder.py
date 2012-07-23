#!/usr/bin/env python
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

import logging
import logging.config
try:
    logging.config.fileConfig('logger.config')
except:
    pass
logging.config.string

import os
import sys
import manifest
import subprocess
import dependencies
import generator

from optparse import OptionParser
from os.path import join, abspath
from generator import AntGenerator, FileWriter
from dependencies import BinaryBundleFinder
from dependencies import SourceBundleFinder
from dependencies import Dependencies

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
                    
def set_logger_level(log_level):
    logger.setLevel(log_level)
    dependencies.set_logger_level(log_level)
    generator.set_logger_level(log_level)
    manifest.set_logger_level(log_level)
  #  persist.set_logger_level(log_level)

class Parameters:
    def __init__(self):
        self.args = None
        self.options = None
        self.parser = OptionParser(version="%prog 1.3.37")

        display_jars_help = 'display binary bundles found on the library_path'
        display_src_help = 'display source bundles found on the source_path'
        check_dep_help = 'validate dependencies without generating build artifacts'
        build_gen_help = 'validate dependencies and generate build artifacts; set'\
                         ' by default if no other options are set.'
        loglevel_help = 'set the logging level; valid values are debug, info, '\
                        'warn, error and critical'
        
        lib_path_help = 'colon separated list of valid root directories to search '\
                        'for binary bundles (in PDE speak: the search '\
                        'path for the target platform); overrides the '\
                        'library_path defined in conf.py'
        
        src_path_help = 'colon separated list of valid root directories to search '\
                        'for source bundles; overrides the '\
                        'source_path defined in conf.py'
        
        project_name_help = 'specifies the name to use in the generated '\
                                 'content; overrides the project_name defined '\
                                 'in conf.py'
        #recreate_db_help = 'recreate the database'
                
        #; if no options are given, '\
        #                 'then this command is executed; supported values'\
        #                 ' are: ant, make, maven; default value is: ant.'
        self.parser.add_option('-l', '--logging-level', dest='loglevel',
                               metavar='LEVEL', help=loglevel_help)
        self.parser.add_option("-j", "--display-jars", action="store_true",
                                default=False, dest="display_jars",
                                help=display_jars_help)
        self.parser.add_option("-d", "--display-src", action="store_true",
                                default=False, dest="display_src",
                                help=display_src_help)
        self.parser.add_option("-c", "--check-dep", action="store_true",
                               default=False, dest="check_dep",
                               help=check_dep_help)
        self.parser.add_option("-b", "--build-gen", action="store_true",
                               default=False, dest="build_gen",
                               help=build_gen_help)
        self.parser.add_option("-p", "--lib-path", default='', type=str,
                               dest="library_path", metavar="PATH", 
                               help=lib_path_help)
        self.parser.add_option("-s", "--source-path", default='', type=str,
                               dest="source_path", metavar="PATH", 
                               help=src_path_help)
        self.parser.add_option("-n", "--project-name", default='', type=str,
                               dest="project_name", metavar="NAME", 
                               help=project_name_help)
        #self.parser.add_option('-z', action='store_true', default=False, dest='z')
        #self.parser.add_option('-r','--recreate', action='store_true',
        #                       default=False, dest='recreate')
        #self.parser.add_option("-g", "--gen-build",
        #              dest="gen_build", metavar="BUILD-TYPE", type=str,
        #              default='ant', help=gen_build_help)
                        
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

        cwd = os.getcwd()
        sys.path.append(cwd)
        try:
            import conf
            conf_defined = True
        except:
            conf_defined = False
        
        if self.options.library_path != '':
            self.options.jar_path = self.options.library_path.split(':')
            print self.options.jar_path
        else:
            if not conf_defined:
                logger.critical('Library path is not defined and there is not a '+\
                                'valid conf file defined; library path must '+\
                                'be defined in a conf file or on the command line.')
                raise Exception('Library path is not defined; exiting')
            
            try:
                self.options.jar_path = conf.library_path
            except:
                logger.critical('Library path is not defined; library path must '+\
                                'be defined in a conf file or on the command line.')
                self.parser.print_help()
                raise Exception('Library path is not defined; exiting.')
        
        if not self.validate('library path', self.options.jar_path):
            logger.critical('All library path directories must be valid; exiting')
            raise Exception('All library path directories must be valid; exiting')
        
        if self.options.source_path != '':
            self.options.src_path = self.options.source_path.split(':')
            print self.options.src_path
        else:
            
            if not conf_defined:
                logger.critical('Source path is not defined and there is not a '+\
                                'valid conf file defined; source path must '+\
                                'be defined in a conf file or on the command line.')
                raise Exception('Source path is not defined; exiting')
            
            try:
                self.options.src_path = conf.source_path
            except:
                logger.critical('Source path is not defined; exiting.')
                self.parser.print_help()
                raise Exception('Source path is not defined; exiting.')
 
        if not self.validate('source path', self.options.src_path):
            logger.critical('All source path directories must be valid; exiting')
            raise Exception('All source path directories must be valid; exiting')
        
        if self.options.project_name == '':
            try:
                self.options.project_name = conf.project_name
            except:
                logger.info('Project name is not defined.')
    
    def validate(self, name, path):
        print path
        for dir in path:
            if not os.path.isdir(dir):
                logger.error('Invalid directory on the '+name+': '+dir)
                return False
        return True

class AutoBuilder:
    
    def __init__(self):
        self.jfinder = BinaryBundleFinder()
        self.sfinder = SourceBundleFinder()
        self.params = Parameters()
        
        self.jfinder.find(self.params.options.jar_path)
        self.jfinder.load()            
        self.sfinder.find(self.params.options.src_path)
        self.sfinder.load()

        self.dependencies = Dependencies(self.jfinder, self.sfinder,
                                         self.jfinder.target_platform)
 
#    def convert_paths(self, jar_path, src_path):
#        index = 0
#        for path in jar_path:
#            jar_path[index] = abspath(path)
#            index += 1
#        index = 0
#        for path in src_path:
#            src_path[index] = abspath(path)
#            index += 1
        
    def run(self):        
        cmd_set = False        
        dependencies_resolved = False
        
        #if self.params.options.recreate:
        #    try:
        #        os.remove('auto-build.db')
        #    except OSError, error:
        #        import re
        #        if re.search('No such file', error.__str__()):
        #            logger.info(error)
        #        else:
        #            raise error
        
        if self.params.options.display_jars:
            print '-'*80
            self.jfinder.display()
            cmd_set = True
            
        if self.params.options.display_src:
            if not cmd_set:
                print '-'*80    
            self.sfinder.display()
            cmd_set = True
            
        if self.params.options.check_dep:
            assert self.dependencies.resolve()
            assert self.dependencies.sort()
            cmd_set = True
            dependencies_resolved = True
        
        #if self.params.options.z:
        #    cmd_set = True
        #    db_path = 'auto-build.db'
        #    r = persist.RelationManager(db_path)
        #    r.create_relations()
        #    for bundle in self.sfinder.bundles:
        #        r.add_bundle(bundle)
        #        break
        #    d = persist.Dependencies(db_path)
        #    d.resolve()
        
        if self.params.options.build_gen or not cmd_set:
            if dependencies_resolved == False:
                assert self.dependencies.resolve()
                assert self.dependencies.sort()
                
            writer = FileWriter()
            ant_generator = AntGenerator(self.params.options.project_name,
                               self.dependencies.src.bundles,
                               self.dependencies.target_platform, '.', writer)
            ant_generator.generate_build_files()
