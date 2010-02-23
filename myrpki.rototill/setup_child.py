"""
Step 2: User sends me.xml to parent, who saves it in a file
        children/foo.xml (where foo is the parent's name for this
        child).  Parent also feeds this file and and parent's own
        me.xml into another new script (call it"setup_child" for now,
        since the parent uses it to set up its child).  This script
        writes out a customized parent record (another XML blob)
        tailored to this particular child (service url including
        parent's and child's names, parent's rpkid server bpki cert,
        etc -- most of the data that goes into a line in parents.csv
        now).  This XML blob can (and usually does) also include
        either an offer of publication service (if the parent runs
        pubd and is willing to act as repository for this child) or a
        hint pointing to some other repository (probably the one the
        parent itself uses).  The distinction between offer and hint
        here is that the parent can only offer a pubd server it runs;
        for anything else it can only hint.  Parent sends this xml
        result blob back to child, who stores at in a parents/
        directory with a name corresponding to the current
        parent_handle (ie, the filename is the child's name for the
        parent, eg, arin.xml).

$Id$

Copyright (C) 2010  Internet Systems Consortium ("ISC")

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS.  IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

import subprocess, csv, re, os, getopt, sys, base64, time, myrpki, rpki.config

from xml.etree.ElementTree import Element, SubElement, ElementTree

os.environ["TZ"] = "UTC"
time.tzset()

cfg_file = "myrpki.conf"

child_handle = None

opts, argv = getopt.getopt(sys.argv[1:], "c:h?", ["config=", "help", "--child_handle="])
for o, a in opts:
  if o == "--child_handle":
    child_handle = a
  elif o in ("-c", "--config"):
    cfg_file = a
  elif o in ("-h", "--help", "-?"):
    print __doc__
    sys.exit(0)

if len(argv) != 1 or not os.path.exists(argv[0]):
  raise RuntimeError, "Need to specify filename for child.xml on command line"

cfg = rpki.config.parser(cfg_file, "myrpki")

if not cfg.getboolean("run_rpkid"):
  raise RuntimeError, "Don't (yet) know how to set up child unless we run rpkid"

my_handle = cfg.get("handle")
run_pubd  = cfg.getboolean("run_pubd")

myrpki.openssl = cfg.get("openssl", "openssl")

bpki_myrpki = myrpki.CA(cfg_file, cfg.get("myrpki_bpki_directory"))
bpki_myirbe = myrpki.CA(cfg_file, cfg.get("myirbe_bpki_directory"))

e = ElementTree(file = argv[0]).getroot()

if child_handle is None:
  child_handle = e["handle"]

print "Child calls itself %r, we call it %r" % (e["handle"], child_handle)

# Cross certify child's cert

myrpki.fxcert(pem = e.findtext(myrpki.tag("bpki_ca_certificate")), path_restriction = 1)

# Build result

e = Element("parent", xmlns = myrpki.namespace, version = "1",
            parent_handle = handle, child_handle = child_handle,
            service_url = "https://%s:%s/up-down/%s/%s" % (cfg.get("rpkid_server_host"),
                                                           cfg.get("rpkid_server_port"),
                                                           handle, child_handle))

myrpki.PEMElement(e, "bpki_resource_ca", bpki_myrpki.cer)
myrpki.PEMElement(e, "bpki_server_ca",   bpki_myirbe.cer)

if run_pubd:
  SubElement(e, "repository", type = "offer",
             service_url = "https://%s:%d/" % (cfg.get("pubd_server_host"),
                                               cfg.get("pubd_server_port")))
else:
  print "Warning: I don't yet know how to do publication hints, only offers"

child_filename = "children/%s.xml" % child_handle
print "Writing", child_filename
myrpki.etree_write(e, child_filename)
