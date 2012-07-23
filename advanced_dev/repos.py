#!/usr/bin/env python

import urllib
import xml.dom.minidom

def readUrl(url):
    contents = ''
    while True:
        line = url.readline()
        contents += line
    return line




class UriHelper:
    def __init__(self):
        self.spring_external = 'http://sigil.codecauldron.org/spring-external.obr'
        self.spring_release = 'http://sigil.codecauldron.org/spring-release.obr'
        
    def parse(self):
        external = urllib.urlopen(self.spring_external)
        #release = urllib.urlopen(self.spring_release)
        
        #external = external.read()
        #print external
        #return
        f = open('./out', 'r')
        external = f.read()
        #print external
        #return
        dom = xml.dom.minidom.parseString(external)
        #print dir(dom), dom.localName, dom.nextSibling.localName, dom.nextSibling.nextSibling.localName
        
        repo = dom.getElementsByTagName('repository')
        bundles = dom.getElementsByTagName('resource')
        for bundle in bundles:
            assert bundle.hasAttribute('symbolicname')
            assert bundle.hasAttribute('uri')
            assert bundle.hasAttribute('version')
            print bundle.getAttribute('symbolicname'), bundle.getAttribute('uri'), bundle.getAttribute('version')
        print 80*'#'
        
if __name__ == '__main__':
    uh = UriHelper()
    uh.parse()