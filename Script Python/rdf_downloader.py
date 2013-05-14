#!/usr/bin/python
import urllib
import sys
import os
import glob
import re
import config
import rdf_parser

def remove_files():
    print "Removing files from %s" % config.DOWNLOAD_PATH
    for old_file in glob.glob(config.DOWNLOAD_PATH + "/*.*"):
        os.remove(old_file)

def report_hook(a, b, c):
    print "% 3.1f%% of %d bytes\r" % (min(100, float(a * b) / c * 100), c)
    sys.stdout.flush()

def download(url):
    file = (url[url.rfind('/') + 1:]).rstrip('\n')
    urllib.urlretrieve(url, config.DOWNLOAD_PATH + "/" + file, report_hook)

def extract_rdf(jsp):
    header = '<?xml version="1.0" encoding="ISO-8859-1"?>'
    write = False
    file = open(jsp)
    dest_file = re.sub("\.jsp", ".rdf", jsp)
    dest = open(dest_file, 'wb')
    dest.write(header)
    for line in file:
        if re.match("^<rdf:", line):
            write = True
        elif re.match("^ ?<\/rdf:", line):
            dest.write(line)
            write = False
        if write:
            dest.write(line)
    file.close()
    dest.close()


def main():
    remove_files()
    urls = open(config.URL_FILE)
    for url in urls:
        download(url)
    for jsp in glob.glob(config.DOWNLOAD_PATH + "/*.jsp"):
        extract_rdf(jsp)
    rdf_parser.parse_rdfs()
main()
