# Installing From Source Code

At present, the entire RPKI tools collection is a single source tree with a
shared autoconf configuration. This may change in the future, but for now,
this means that the build process is essentially the same regardless of which
tools one wants to use. Some of the tools have dependencies on external
packages, although we've tried to keep this to a minimum.

Most of the tools require an [RFC-3779][1]-aware version of the [OpenSSL][2]
libraries. If necessary, the build process will generate its own private copy
of the OpenSSL libraries for this purpose.

Other than OpenSSL, most of the relying party tools are fairly self-contained.
The CA tools have a few additional dependencies, described below.

Note that initial development of this code has been on FreeBSD, so
installation will probably be easiest on FreeBSD. We do, however, test on
other platforms, such as Fedora, Ubuntu, Debian, and MacOSX.

## Downloading the Source Code

The recommended way to obtain the source code is via [subversion][3]. To
download, do:

    
    
    $ svn checkout https://subvert-rpki.hactrn.net/trunk/
    

Code snapshots are also available from <https://download.rpki.net/> as xz-
compressed tarballs.

## Prerequisites

Before attempting to build the tools from source, you will need to install any
missing prerequisites.

Some of the relying party tools and most of the CA tools are written in
Python. Note that the Python code requires Python version 2.6 or 2.7.

On some platforms (particularly MacOSX) the simplest way to install some of
the Python packages may be the "easy_install" or "pip" tools that comes with
Python.

Packages you will need:

  * You will need a C compiler. gcc is fine, others such as Clang should also work. 
  * <http://www.python.org/>, the Python interpreter, libraries, and sources. On some platforms the Python sources (in particular, the header files and libraries needed when building Python extensions) are in a separate "development" package, on other platforms they are all part of a single package. If you get compilation errors trying to build the POW code later in the build process and the error message says something about the file "Python.h" being missing, this is almost certainly your problem. 
    * FreeBSD: 
      * /usr/ports/lang/python27 (python) 
    * Debian &amp; Ubuntu: 
      * python 
      * python-dev 
      * python-setuptools 

  * <http://codespeak.net/lxml/>, a Pythonic interface to the Gnome LibXML2 libraries. lxml in turn requires the LibXML2 C libraries; on some platforms, some of the LibXML2 utilities are packaged separately and may not be pulled in as dependencies. 
    * FreeBSD: /usr/ports/devel/py-lxml (py27-lxml) 
    * Fedora: python-lxml.i386 
    * Debian &amp; Ubuntu: 
      * python-lxml 
      * libxml2-utils 
  * <http://www.mysql.com/>, MySQL client and server. How these are packaged varies by platform, on some platforms the client and server are separate packages, on others they might be a single monolithic package, or installing the server might automatically install the client as a dependency. On MacOSX you might be best off installing a binary package for MySQL. The RPKI CA tools have been tested with MySQL 5.0, 5.1, and 5.5; they will probably work with any other reasonably recent version. 
    * FreeBSD: 
      * /usr/ports/databases/mysql55-server (mysql55-server) 
      * /usr/ports/databases/mysql55-client (mysql55-client) 
    * Debian &amp; Ubuntu: 
      * mysql-client 
      * mysql-server 
  * <http://sourceforge.net/projects/mysql-python/>, the Python "db" interface to MySQL. 
    * FreeBSD: /usr/ports/databases/py-MySQLdb (py27-MySQLdb) 
    * Fedora: MySQL-python.i386 
    * Debian &amp; Ubuntu: python-mysqldb 
  * <http://www.djangoproject.com/>, the Django web user interface toolkit. The GUI interface to the CA tools requires this. Django 1.4 is required. 
    * FreeBSD: /usr/ports/www/py-django (py27-django) 
    * Debian: python-django 
    * Ubuntu: **Do not use the python-django package (Django 1.3.1) in 12.04 LTS, as it is known not to work.**   
Instead, install a recent version using easy_install or pip:

        
                $ sudo pip install django==1.4.5
        

  * <http://vobject.skyhouseconsulting.com/>, a Python library for parsing VCards. The GUI uses this to parse the payload of RPKI Ghostbuster objects. 
    * FreeBSD: /usr/ports/deskutils/py-vobject (py27-vobject) 
    * Debian &amp; Ubuntu: python-vobject 
  * Several programs (more as time goes on) use the Python argparse module. This module is part of the Python standard library as of Python 2.7, but you may need to install it separately if you're stuck with Python 2.6. Don't do this unless you must. In cases where this is necessary, you'll probably need to use pip: 
    
        $ python -c 'import argparse' 2>/dev/null || sudo pip install argparse
    

  * <http://pyyaml.org/>. Several of the test programs use PyYAML to parse a YAML description of a simulated allocation hierarchy to test. 
    * FreeBSD: /usr/ports/devel/py-yaml (py27-yaml) 
    * Debian &amp; Ubuntu: python-yaml 
  * <http://xmlsoft.org/XSLT/>. Some of the test code uses xsltproc, from the Gnome LibXSLT package. 
    * FreeBSD: /usr/ports/textproc/libxslt (libxslt) 
    * Debian &amp; Ubuntu: xsltproc 
  * <http://www.rrdtool.org/>. The relying party tools use this to generate graphics which you may find useful in monitoring the behavior of your validator. The rest of the software will work fine without rrdtool, you just won't be able to generate those graphics. 
    * FreeBSD: /usr/ports/databases/rrdtool (rrdtool) 
    * Debian &amp; Ubuntu: rrdtool 
  * <http://www.freshports.org/www/mod_wsgi3/> If you intend to run the GUI with wsgi, its default configuration, you will need to install mod_wsgi v3 
    * FreeBSD: /usr/ports/www/mod_wsgi3 (app22-mod_wsgi) 
    * Debian &amp; Ubuntu: libapache2-mod-wsgi 
  * <http://south.aeracode.org/> Django South 0.7.6 or later. This tool is used to ease the pain of changes to the web portal database schema. 
    * FreeBSD: /usr/ports/databases/py-south (py27-south) 
    * Debian: python-django-south 
    * Ubuntu: **Do not use the python-django-south 0.7.3 package in 12.04 LTS, as it is known not to work.**   
Instead, install a recent version using easy_install or pip:

        
                pip install South>=0.7.6
        

## Configure and build

Once you have the prerequesite packages installed, you should be able to build
the toolkit. cd to the top-level directory in the distribution, run the
configure script, then run "make":

    
    
    $ cd $top
    $ ./configure
    $ make
    

This should automatically build everything, in the right order, including
building a private copy of the OpenSSL libraries with the right options if
necessary and linking the POW module against either the system OpenSSL
libraries or the private OpenSSL libraries, as appopriate.

In theory, `./configure` will complain about any required packages which might
be missing.

If you don't intend to run any of the CA tools, you can simplify the build and
installation process by telling `./configure` that you only want to build the
relying party tools:

    
    
    $ cd $top
    $ ./configure --disable-ca-tools
    $ make
    

## Testing the build

Assuming the build stage completed without obvious errors, the next step is to
run some basic regression tests.

Some of the tests for the CA tools require MySQL databases to store their
data. To set up all the databases that the tests will need, run the SQL
commands in `ca/tests/smoketest.setup.sql`. The MySQL command line client is
usually the easiest way to do this, eg:

    
    
    $ cd $top/ca
    $ mysql -u root -p <tests/smoketest.setup.sql
    

To run the tests, run "make test":

    
    
    $ cd $top
    $ make test
    

To run a more extensive set of tests on the CA tool, run "make all-tests" in
the `ca/` directory:

    
    
    $ cd $top/ca
    $ make all-tests
    

If nothing explodes, your installation is probably ok. Any Python backtraces
in the output indicate a problem.

## Installing

Assuming the build and test phases went well, you should be ready to install
the code. The `./configure` script attempts to figure out the "obvious" places
to install the various programs for your platform: binaries will be installed
in `/usr/local/bin` or `/usr/local/sbin`, Python modules will be installed
using the standard Python distutils and should end up wherever your system
puts locally-installed Python libraries, and so forth.

The RPKI validator, rcynic, is a special case, because the install scripts may
attempt to build a chroot jail and install rcynic in that environment. This is
straightforward in FreeBSD, somewhat more complicated on other systems,
primarily due to hidden dependencies on dynamic libraries.

To install the code, become root (su, sudo, whatever), then run "make
install":

    
    
    $ cd $top
    $ sudo make install
    

## Tools you should not need to install

There's a last set of tools that only developers should need, as they're only
used when modifying schemas or regenerating the documentation. These tools are
listed here for completeness.

  * <http://www.doxygen.org/>. Doxygen in turn pulls in several other tools, notably Graphviz, pdfLaTeX, and Ghostscript. 
    * FreeBSD: /usr/ports/devel/doxygen 
    * Debian &amp; Ubuntu: doxygen 
  * <http://www.mbayer.de/html2text/>. The documentation build process uses xsltproc and html2text to dump flat text versions of a few critical documentation pages. 
    * FreeBSD: /usr/ports/textproc/html2text 
  * <http://www.thaiopensource.com/relaxng/trang.html>. Trang is used to convert RelaxNG schemas from the human-readable "compact" form to the XML form that LibXML2 understands. Trang in turn requires Java. 
    * FreeBSD: /usr/ports/textproc/trang 
  * <http://search.cpan.org/dist/SQL-Translator/>. SQL-Translator, also known as "SQL Fairy", includes code to parse an SQL schema and dump a description of it as Graphviz input. SQL Fairy in turn requires Perl. 
    * FreeBSD: /usr/ports/databases/p5-SQL-Translator 
  * <http://www.easysw.com/htmldoc/>. The documentation build process uses htmldoc to generate PDF from the project's Trac wiki. 
    * FreeBSD: /usr/ports/textproc/htmldoc 

## Next steps

Once you've finished installing the code, you will need to configure it. Since
CAs are generally also relying parties (if only so that they can check the
results of their own actions), you will generally want to start by configuring
the [relying party tools][4], then configure the [CA tools][5] if you're
planning to use them.

   [1]: http://www.rfc-editor.org/rfc/rfc3779.txt

   [2]: http://www.openssl.org/

   [3]: https://subversion.apache.org/

   [4]: #_.wiki.doc.RPKI.RP

   [5]: #_.wiki.doc.RPKI.CA

