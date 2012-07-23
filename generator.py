#!/usr/bin/env python
#
#    Author: James Percent (james@empty-set.net)
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
from os import getcwd, chdir
from os.path import join

logger = logging.getLogger(__name__)
def set_logger_level(logLevel):
    logger.setLevel(logLevel)

class AntGenerator:
    def __init__(self, project_name, source_bundles, target_platform,
                 master_build_file_root, build_writer):
            
        self.project_name = project_name
        self.src = source_bundles
        self.target_platform = target_platform
        self.master_root = master_build_file_root
        self.master_build_file = ''
        self.master_complie = ''
        self.master_test = ''
        self.master_package = ''
        self.master_lint = ''
        self.master_clean = ''
        self.writer = build_writer
        
    def __build_classpath__(self, bundle):
        if bundle.classpath == None:
            bundle.classpath = {}
               
            for lib in bundle.extra_libs.keys():
                bundle.classpath[lib] = lib

            if bundle.binary_bundle_dir:    
                for lib in bundle.classpath_jars:
                    qlib = join(bundle.root, bundle.file, lib)
                    bundle.classpath[qlib] = qlib
            
            for dep in bundle.deps:
                if dep.classpath == None:
                    self.__build_classpath__(dep)
                    
                for clazz1 in dep.classpath.keys():
                    bundle.classpath[clazz1] = clazz1
                    
                clazz = ''              
                clazz += join(dep.root, dep.file)
                if not dep.is_binary_bundle:
                    clazz = join(clazz, 'bin')
                    
                if not (clazz in bundle.classpath):
                    bundle.classpath[clazz] = clazz
                    
        if len(bundle.junit_tests) > 0:
            clazz = join(bundle.root, 'bin')
            bundle.classpath[clazz] = clazz
                    
    def __write_preamble__(self, build_xml, home, bundle):
        f = '<?xml version="1.0"?>\n'
        f += '<project name="'+str(bundle.sym_name)+'" default="compile" basedir="'+str(home)+'">\n'
        build_xml.write(f)
        
    def __write_properties__(self, build_xml, home, bundle):
        f = '\t<property name="lib" value="'+str(home)+'/lib" />\n'
        f += '\t<property name="src" value="'+str(bundle.root)+'/src" />\n'
        f += '\t<property name="build" value="'+str(bundle.root)+'/bin" />\n'
        f += '\t<property name="manifest" value="'+str(bundle.root)+'/META-INF/MANIFEST.MF" />\n'
        f += '\t<property name="metainf" value="'+str(bundle.root)+'/META-INF" />\n'
        f += '\t<property name="bundle" value="'+str(home)+'/lib/'+\
                     str(bundle.sym_name)+'_'+bundle.version.__str__()+'.jar" />\n'
        build_xml.write(f)

    def __write_classpath_target__(self, build_xml, bundle):
        f = '\t<path id="classpath">\n'
        for location in bundle.classpath.keys():
            f += '\t\t<pathelement location="'+str(location)+'"/>\n'
        f += '\t</path>\n'
        build_xml.write(f)
    
    def __write_init_target__(self, build_xml):
        f = '\t<target name="init" depends="clean">\n'
        f += '\t\t<tstamp />\n'
        f += '\t\t<mkdir dir="${build}" />\n'
        f += '\t</target>\n'
        build_xml.write(f)
        
    def __write_clean_target__(self, build_xml):
        f = '\t<target name="clean" description="clean up">\n'
        f += '\t\t<delete dir="${build}" />\n'
        f += '\t</target>\n'
        build_xml.write(f)

    def __write_compile_target__(self, build_xml):
        f = '\t<target name="compile" depends="init">\n'
        f += '\t\t<javac srcdir="${src}" destdir="${build}" classpathRef="classpath"/>\n'
        f += '\t</target>\n'
        build_xml.write(f)
        
    def __write_test_target__(self, build_xml, bundle):
              
        f = '\t<target name="test" depends="compile">\n'
        if len(bundle.junit_tests) > 0:
            f += '\t\t<junit fork="yes" haltonfailure="yes">\n'
            tests = False
            for i in bundle.junit_tests:
                tests = True
                f += '\t\t\t<test name="'+i[1]+'.'+i[2]+'" />\n'
                    
            if tests:
                f += '\t\t\t<formatter type="plain" usefile="false" />\n'
                f += '\t\t\t<classpath refid="classpath" />\n'
                
            f += '\t\t</junit>\n'
        f += '\t</target>\n'
        build_xml.write(f)        
        
    def __write_lint_target__(self, build_xml):
        f = '\t<target name="lint" depends="init">\n'
        f += '\t\t<javac srcdir="${src}" destdir="${build}" classpathRef="classpath">\n'
        f += '\t\t\t<compilerarg value="-Xlint"/>\n'
        f += '\t\t</javac>\n'
        f +='\t</target>\n'
        build_xml.write(f)
        
    def __write_jar_target__(self, build_xml, bundle):            
            f = '\t<target name="package" depends="compile">\n'
            # extra_libs are jar files that are not OSGi bundles, which must be
            # compiled.  However, all jar files should be converted to OSGi
            # bundles.
            extra_libs = False
            for i in bundle.extra_libs:
                f += '\t\t<mkdir dir="tmp1"/>\n'
                f += '\t\t<unjar src="'+i+'" dest="tmp1" />\n'
                extra_libs = True
            
            if extra_libs:    
                f += '\t\t<delete dir="'+join('tmp1', 'META-INF')+'"/>\n'
                f += '\t\t<copy todir="${build}">\n'
                f += '\t\t\t<fileset dir="tmp1"><include name="**"/></fileset>\n'
                f += '\t\t</copy>\n'
                f += '\t\t<delete dir="tmp1"/>\n'

            f += '\t\t<jar destfile="${bundle}" basedir="${build}" manifest="${manifest}">\n'
            f += '\t\t\t<metainf dir="${metainf}"/>\n'
            f += '\t\t</jar>\n'
            f += '\t</target>\n'
            build_xml.write(f)
            
    def __create_master_build_file_header__(self):
        self.master_build_file = '<?xml version="1.0"?>\n'
        self.master_build_file += '<project name="'+str(self.project_name)+'" default="compile" basedir=".">\n'
        self.master_build_file += '\t<property name="lib" value="./lib" />\n'        
        self.master_build_file += '\t<target name="init">\n'
        self.master_build_file += '\t\t<delete dir="${lib}" />\n'
        self.master_build_file += '\t\t<mkdir dir="${lib}" />\n'
        self.master_build_file += '\t</target>\n'
        self.master_compile = '\t<target name="compile">\n'
        self.master_test = '\t<target name="test">\n'
        self.master_clean = '\t<target name="clean" description="clean up">\n'
        self.master_lint = '\t<target name="lint" description="run lint" >\n'
        self.master_package = '\t<target name="package" description="packages bundles" depends="init">\n'        
    
    def __append_to_master_build_file__(self, bundle):
        self.master_compile += '\t\t<ant dir="'+bundle.root+'" target="compile" />\n'
        self.master_test += '\t\t<ant dir="'+bundle.root+'" target="test" />\n'
        self.master_clean += '\t\t<ant dir="'+bundle.root+'" target="clean" />\n'
        self.master_lint += '\t\t<ant dir="'+bundle.root+'" target="lint" />\n'
        self.master_package += '\t\t<ant dir="'+bundle.root+'" target="package" />\n'
        
            
    def __write_master_build_file__(self, build_xml):
        self.master_compile += '\t</target>\n'
        self.master_test += '\t</target>\n'        
        self.master_clean += '\t</target>\n'
        self.master_lint += '\t</target>\n'

        for root, file, is_dir in self.target_platform.values():
            #master_package += '\t\t<echo> copying '+join(root,file)+' </echo>\n'
            if is_dir:
                logger.debug(join(root, file))
                self.master_package+= '\t\t<mkdir dir="${lib}/'+file+'"/>\n'
                self.master_package += '\t\t<copy todir="${lib}/'+file+\
                                  '"><fileset dir="'+join(root,file)+\
                                  '"/></copy>\n'
            else:
                self.master_package += '\t\t<copy file="'+join(root,file)+\
                                  '" todir="${lib}" overwrite="true" />\n'
        self.master_package += '\t</target>\n'
        
        self.master_build_file += self.master_clean
        self.master_build_file += self.master_compile
        self.master_build_file += self.master_test
        self.master_build_file += self.master_lint
        self.master_build_file += self.master_package
        
        self.master_build_file += '</project>\n'
        build_xml.create_build_file(self.master_root)
        build_xml.write(self.master_build_file)
        
    def generate_build_files(self):
        self.__create_master_build_file_header__()
        for bundle in self.src:
            assert bundle.root != ''
                
            self.__append_to_master_build_file__(bundle)
            
            self.writer.create_build_file(bundle.root)

            logger.debug(bundle)
            self.__build_classpath__(bundle)
                
            self.__write_preamble__(self.writer, self.writer.get_cwd(), bundle)
            self.__write_properties__(self.writer, self.writer.get_cwd(), bundle)
            self.__write_classpath_target__(self.writer, bundle)
            self.__write_init_target__(self.writer)
            self.__write_clean_target__(self.writer)
            self.__write_compile_target__(self.writer)
            self.__write_test_target__(self.writer, bundle)
            self.__write_jar_target__(self.writer, bundle)
            
            self.writer.write('</project>\n')
            self.writer.close_build_file()
            
        self.__write_master_build_file__(self.writer)
            

class FileWriter:
    def __init__(self):
        self.home_dir = None
        self.build_xml = None
    
    def get_cwd(self):
        assert self.home_dir
        return self.home_dir
    
    def create_build_file(self, root_dir):
        self.home_dir = getcwd()
        chdir(root_dir)
        self.build_xml = open('build.xml', 'w')
            
    def write(self, value):
        assert self.build_xml and self.home_dir
        self.build_xml.write(value)
        
    def close_build_file(self):
        assert self.build_xml and self.home_dir
        self.build_xml.close()
        chdir(self.home_dir)
        self.home_dir = None
        self.build_xml = None



