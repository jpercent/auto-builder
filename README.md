Auto Builder: A Tool for Automating PDE-based OSGi Builds
==========================================================

Prelude
--------

During the summer of 2010 I was helping out with the Rifidi project.  As part of that, I recommended getting a continuous integration (CI) system in place.

Surprisingly, because of the infrastructure that the Rifidi platform is based on, this was not as straight forward as I thought it would be.  The platform is based on OSGi technology – a dynamic module and service registry specification for Java-based applications.  In particular, it’s based on Eclipse’s Plugin Development Environment (PDE).

While PDE provides a fairly sophisticated and mature set of tools for OSGi-based development, when it comes to automation and continuous integration, the PDE build tooling is abstruse and the maven-based tools I played with, when integrated with PDE, didn’t “just work.”

We wanted to do all of our coding in PDE and have a Hudson-based CI without any fuss in between.  So I rolled my own tool, called auto builder, that automatically generates Ant-based build artifacts.  It’s completely declarative and supports transitive closure over dependencies.

The rest of this post documents how to install and use the auto builder.

Overview
---------

The auto builder is a Python program that will introspect a PDE project and generate Ant-based build artifacts.  The build artifacts include targets for compiling, testing and packaging the source bundles of the project.

The auto builder consists of an OSGi Manifest parser, which is implemented with the PLY (Python Lex-Yacc) parse generator, a dependency resolver and a build script generator.  It is designed to be very hands off – it only needs to know the path(s) to the target platform bundles and the path(s) to the source bundles.  It is as simple as that.

Installation
-------------

To install the auto builder, Python 2.x needs to be installed and working on your system.  I have packaged a zip version here, which should play nicely with Windows, and a tar.gz version here.  The sources are on Google code and can also be downloaded from there via subversion.

A treasure trove of Python package installation documentation is here.  Just the same, I will cover how to install for UNIX variants; note, the following installation instructions will also work for Windows users that have Cygwin installed.

First download the tar.gz version linked above and run the following script from the command-line:

<pre>
   $ tar xzvf auto-builder-1.0.tar.gz \
     && pushd auto-builder-1.0 \
     && sudo python setup.py install \
     && popd
</pre>

That’s it!  The installation can be validated with 2 commands.  First, run the following command: which auto-build.   If the installation failed, then the which command will complain that it can not find auto-build.

Next, fire-up the Python interpreter and run: import auto_builder.  If the installation failed, then doing so will result in an ImportError exception.  Here’s what a successful validation looks like:

<pre>
   $ python
   >>> import auto_builder
   >>>
   $ which auto-build
   /usr/local/bin/auto-build
</pre>


Usage
------

The auto builder only needs to know the path to the libraries that comprise the target platform of the project (binary bundles — a.k.a. the jar files) and the paths to the source bundles of the project.

The easiest way to feed this information into the auto builder is to define a file called conf.py; it must be defined the directory from which the auto builder is executed (more on execution in a second).  Here’s an conf.py example:

<pre>
   # Author: James Percent (james@empty-set.net)
   # Copyright 2010, 2011 James Percent

   project_name = 'Minerva'

   library_path = [
      '../Minerva-SDK/lib/'
   ]

   source_path = [
    '../org.syndeticlogic.minerva',
    '../org.syndeticlogic.minerva.adapters',
    '../org.syndeticlogic.minerva.init',
    '../org.syndeticlogic.minerva.tools'
   ]
</pre>

The example configuration file defines the following parameters:

    library_path – a Python list of string variables that is path(s) to the bundle libraries that comprise the target platform;
    source_path – a Python list of string variables that correspond to the source bundles of the project;
    project_name – a Python string that represents the name of the project.

The project_name is completely optional.  The library_path and source_path are required.  However, they can also be defined via the command-line if that is preferable.

The user interface to the auto builder is the auto-build script.  Here’s the output from running the help:
<pre>
$ auto-build --help
Usage: auto-build [options]
Options:
 --version            show program's version number and exit
 -h, --help           show this help message and exit
 -j, --display-jars   display binary bundles found on the
                      library_path
 -d, --display-src    display source bundles found on the
                      source_path
 -c, --check-dep      validate dependencies without generating build
                      artifacts
 -b, --build-gen      validate dependencies and generate build
                      artifacts; set by default if no other options
                      are set
-p PATH, --lib-path=PATH
                      colon separated list of valid root directories
                      to search for binary bundles (search path for
                      the target platform); overrides the
                      library_path defined in conf.py
 -s PATH, --source-path=PATH
                      colon separated list of valid root directories
                      to search for source bundles; overrides the
                      source_path defined in conf.py
 -n NAME, --project-name=NAME
                      specifies the name to use in the generated
                      content; overrides the project_name defined in
                      conf.py
-l LEVEL, --logging-level=LEVEL
                      set the logging level; valid values are debug,
                      info, warn, error and critical
</pre>

The option of interest here is –build-gen.  As advertised it’s the default option.  All you have to do is set up the conf.py and run auto-build and it will generate build scripts for your project.  An example build script, generated by auto builder, for the Minerva project is here.

The other options are really straight forward.  If you’re not sure what they do, just run them and you’ll see…

Conclusion
-----------

The auto builder is a tool that discovers the structure of a PDE-based project and automatically generates standard, Ant-based build artifacts.  It’s declarative, performs transitive closure over dependencies, and does not define its own, new vocabulary.  It just plain works.

My opinion is that systems themselves define their assembly; therefore the assemply process should be completely automated.  And generating Ant files is an interesting strategy because it gives you all the benefits of a declarative build tool, but it leaves you with a procedural description of what it is doing.

The next steps are to find more projects to test on, and to add support for automatic dependency download.  I already have code for automatically downloading dependencies from RFC-0112 bundle repositories.  If I could garner interest, then I could easily integrate it.

Copyright (C) James Percent 2012