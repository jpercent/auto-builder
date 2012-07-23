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

auto_builder.set_logger_level(logging.WARN)

class TestFileWriter:
    def __init__(self):
        self.files = {}
        self.current = None
        self.closed = {}
        
    def get_cwd(self):
        assert self.current
        return 'test-home'
        
    def create_build_file(self, root_dir):
        self.current = root_dir
        self.files[self.current] = ''
        self.closed[self.current] = False
        
    def write(self, value):
        assert self.current
        self.files[self.current] += value
        
    def close_build_file(self):
        self.closed[self.current] = True
        self.current = None
        
class AntGeneratorTest(unittest.TestCase):
    
    # '\t<target name="test" depends="compile">\n'
    # '\t\t<junit fork="yes" haltonfailure="yes">\n'
    # '\t</target>\n'
    
    minerva = '<?xml version="1.0"?>\n'+\
    '<project name="org.syndeticlogic.minerva" default="compile" basedir="test-home">\n'+\
        '\t<property name="lib" value="test-home/lib" />\n'+\
        '\t<property name="src" value="../minerva/src" />\n'+\
        '\t<property name="build" value="../minerva/bin" />\n'+\
        '\t<property name="manifest" value="../minerva/META-INF/MANIFEST.MF" />\n'+\
        '\t<property name="metainf" value="../minerva/META-INF" />\n'+\
        '\t<property name="bundle" value="test-home/lib/org.syndeticlogic.minerva_1.3.jar" />\n'+\
        '\t<path id="classpath">\n'+\
            '\t\t<pathelement location="../minerva/bin"/>\n'+\
            '\t\t<pathelement location="../libs/org.eclipse.osgi.jar"/>\n'+\
        '\t</path>\n'+\
        '\t<target name="init" depends="clean">\n'+\
            '\t\t<tstamp />\n'+\
            '\t\t<mkdir dir="${build}" />\n'+\
        '\t</target>\n'+\
        '\t<target name="clean" description="clean up">\n'+\
            '\t\t<delete dir="${build}" />\n'+\
        '\t</target>\n'+\
        '\t<target name="compile" depends="init">\n'+\
            '\t\t<javac srcdir="${src}" destdir="${build}" classpathRef="classpath"/>\n'+\
        '\t</target>\n'+\
        '\t<target name="test" depends="compile">\n'+\
            '\t\t<junit fork="yes" haltonfailure="yes">\n'+\
                '\t\t\t<test name="minerva.test.minervaJunitTest.java" />\n'+\
                '\t\t\t<test name="minerva.test.api.minervaJunitTest1.java" />\n'+\
                '\t\t\t<formatter type="plain" usefile="false" />\n'+\
                '\t\t\t<classpath refid="classpath" />\n'+\
            '\t\t</junit>\n'+\
        '\t</target>\n'+\
        '\t<target name="package" depends="compile">\n'+\
            '\t\t<jar destfile="${bundle}" basedir="${build}" manifest="${manifest}">\n'+\
                    '\t\t\t<metainf dir="${metainf}"/>\n'+\
            '\t\t</jar>\n'+\
        '\t</target>\n'+\
    '</project>\n'
    
    minerva_tools = '<?xml version="1.0"?>\n'+\
    '<project name="org.syndeticlogic.minerva.tools" default="compile" basedir="test-home">\n'+\
            '\t<property name="lib" value="test-home/lib" />\n'+\
            '\t<property name="src" value="../minerva.tools/src" />\n'+\
            '\t<property name="build" value="../minerva.tools/bin" />\n'+\
            '\t<property name="manifest" value="../minerva.tools/META-INF/MANIFEST.MF" />\n'+\
            '\t<property name="metainf" value="../minerva.tools/META-INF" />\n'+\
            '\t<property name="bundle" value="test-home/lib/org.syndeticlogic.minerva.tools_1.3.1.jar" />\n'+\
            '\t<path id="classpath">\n'+\
                '\t\t<pathelement location="../minerva/minerva.jar/bin"/>\n'+\
                '\t\t<pathelement location="../minerva/bin"/>\n'+\
                '\t\t<pathelement location="../libs/org.eclipse.osgi.jar"/>\n'+\
            '\t</path>\n'+\
            '\t<target name="init" depends="clean">\n'+\
                    '\t\t<tstamp />\n'+\
                    '\t\t<mkdir dir="${build}" />\n'+\
            '\t</target>\n'+\
            '\t<target name="clean" description="clean up">\n'+\
                    '\t\t<delete dir="${build}" />\n'+\
            '\t</target>\n'+\
            '\t<target name="compile" depends="init">\n'+\
                    '\t\t<javac srcdir="${src}" destdir="${build}" classpathRef="classpath"/>\n'+\
            '\t</target>\n'+\
            '\t<target name="test" depends="compile">\n'+\
            '\t</target>\n'+\
            '\t<target name="package" depends="compile">\n'+\
                    '\t\t<jar destfile="${bundle}" basedir="${build}" manifest="${manifest}">\n'+\
                            '\t\t\t<metainf dir="${metainf}"/>\n'+\
                    '\t\t</jar>\n'+\
            '\t</target>\n'+\
        '</project>\n'
    
    master = '<?xml version="1.0"?>\n'+\
    '<project name="test" default="compile" basedir=".">\n'+\
            '\t<property name="lib" value="./lib" />\n'+\
            '\t<target name="init">\n'+\
                    '\t\t<delete dir="${lib}" />\n'+\
                    '\t\t<mkdir dir="${lib}" />\n'+\
            '\t</target>\n'+\
            '\t<target name="clean" description="clean up">\n'+\
                    '\t\t<ant dir="../minerva" target="clean" />\n'+\
                    '\t\t<ant dir="../minerva.tools" target="clean" />\n'+\
            '\t</target>\n'+\
            '\t<target name="compile">\n'+\
                    '\t\t<ant dir="../minerva" target="compile" />\n'+\
                    '\t\t<ant dir="../minerva.tools" target="compile" />\n'+\
            '\t</target>\n'+\
            '\t<target name="test">\n'+\
                '\t\t<ant dir="../minerva" target="test" />\n'+\
                '\t\t<ant dir="../minerva.tools" target="test" />\n'+\
            '\t</target>\n'+\
            '\t<target name="lint" description="run lint" >\n'+\
                    '\t\t<ant dir="../minerva" target="lint" />\n'+\
                    '\t\t<ant dir="../minerva.tools" target="lint" />\n'+\
            '\t</target>\n'+\
            '\t<target name="package" description="packages bundles" depends="init">\n'+\
                    '\t\t<ant dir="../minerva" target="package" />\n'+\
                    '\t\t<ant dir="../minerva.tools" target="package" />\n'+\
                    '\t\t<copy file="../libs/org.eclipse.osgi.jar" todir="${lib}" overwrite="true" />\n'+\
            '\t</target>\n'+\
    '</project>\n'
    

    def generate_stubs(self):
        src = []
        jars = []
        target_platform = []
        v = Version()
        v.set_major(1)
        
        v1 = Version()
        v1.set_major(1)
        v1.set_minor(3)
        
        v2 = Version()
        v2.set_major(1)
        v2.set_minor(3)
        v2.set_micro(1)
        
        v3 = Version()
        v3.set_major(2)
        
        p = Package('org.eclipse.osgi')
        p.set_version_range(v, True, v1, False)
        
        p1 = Package('org.syndeticlogic.minerva')
        p1.set_version_range(v, True, v3, True)

        p2 = Package('org.syndeticlogic.minerva.tools')        
        p2.set_version_range(v, True, v1, True)
        
        p3 = Package('org.syndeticlogic.minerva.adapters')
        p3.set_version_range(v2, True, v3, False)
        
        p4 = Package('org.syndeticlogic.minerva.test')

        b = Bundle()
        b.sym_name = p.name
        b.root = '../libs'
        b.file = 'org.eclipse.osgi.jar'
        b.version = v1
        b.is_binary_bundle = True
        
        b1 = Bundle()
        b1.sym_name = p1.name
        b1.root = '../minerva'
        b1.file = 'minerva.jar'
        b1.version = v1
        b1.add_epackage(p1)
        b1.add_required_bundle_lookup_info(p1)
        b1.add_dep(b)
        b1.junit_tests.append((b1.root, 'minerva.test', 'minervaJunitTest.java'))
        b1.junit_tests.append((b1.root, 'minerva.test.api', 'minervaJunitTest1.java'))
        
        b2 = Bundle()
        b2.sym_name = p2.name
        b2.root = '../minerva.tools'
        b2.file = 'minerva.tools.jar'
        b2.version = v2
        b2.add_epackage(p2)
        b2.add_ipackage(p1)
        b2.add_dep(b1)
        target_platform = {}
        target_platform[join(b.root, b.file)] = (b.root, b.file, False)
        writer = TestFileWriter()
        
        jars.append(b)
        src.append(b1)
        src.append(b2)
        
        return (jars, src, target_platform, writer)
    
    # XXX - this isn't the test i am most proud of, and it could be refactored.
    # however, it has helped me to find 3 regressions as I made other changes
    # to the code base.  it works and has been helpful; it certainly isn't
    # pretty.
    def test_generator(self):
        #print 'test generator'
        jars, src, target_platform, writer = self.generate_stubs()
        gen = AntGenerator("test", src, target_platform, './', writer)
        gen.generate_build_files()
        top = True
        
        #print self.master
        #print 80*'#'
        #print writer.files['../minerva']
        
        self.assertTrue('../minerva' in writer.files)
        self.assertTrue('../minerva.tools' in writer.files)
        self.assertTrue('./' in writer.files)

        #str = ''
        #for i in range(0, len(self.minerva_tools)):
        #    if self.minerva_tools[i] == writer.files['../minerva.tools'][i]:
        #        str += self.minerva_tools[i]
        #    else:
        #        break
        #print str
        #return

        
        self.assertEquals(self.minerva, writer.files['../minerva'])
        
        self.assertEquals(self.minerva_tools, writer.files['../minerva.tools'])
        self.assertEquals(self.master, writer.files['./'])

if __name__ == '__main__':
    unittest.main()
    
