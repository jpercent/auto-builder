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
from distutils.core import setup

setup(name='auto-builder',
      version='1.0',
      description='This is my rifle, this is my gun',
      license='GPL v3',
      author='James Percent',
      author_email='james@empty-set.net',
      url='http://code.google.com/p/auto-builder',
      data_files=[('', ['logger.config']) ],
      scripts=['auto-build'],
      py_modules=['auto_builder', 'manifest', 'dependencies', 'generator', 'parsetab',
                  'ply.lex', 'ply.yacc', 'ply.cpp', 'ply.ctokens'],
      )
