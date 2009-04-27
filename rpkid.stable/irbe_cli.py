"""
Command line IR back-end control program for rpkid and pubd.

$Id$

Copyright (C) 2007--2008  American Registry for Internet Numbers ("ARIN")

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND ARIN DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS.  IN NO EVENT SHALL ARIN BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

import getopt, sys, textwrap
import rpki.left_right, rpki.https, rpki.x509, rpki.config, rpki.log, rpki.publication

pem_out = None

class UsageWrapper(textwrap.TextWrapper):
  """Call interface around Python textwrap.Textwrapper class."""

  def __call__(self, *args):
    """Format arguments, with TextWrapper indentation."""
    return self.fill(textwrap.dedent(" ".join(args)))

usage_fill = UsageWrapper(subsequent_indent = " " * 4)

class cmd_elt_mixin(object):
  """Protocol mix-in for command line client element PDUs."""

  ## @var excludes
  # XML attributes and elements that should not be allowed as command
  # line arguments.  At the moment the only such is the
  # bsc.pkcs10_request sub-element, but writing this generally is no
  # harder than handling that one special case.
  excludes = ()

  @classmethod
  def usage(cls):
    """Generate usage message for this PDU."""
    args = " ".join("--" + x + "=" for x in cls.attributes + cls.elements if x not in cls.excludes)
    opts = " ".join("--" + x for x in cls.booleans)
    if args and opts:
      return args + " " + opts
    else:
      return args or opts

  def client_getopt(self, argv):
    """Parse options for this class."""
    opts, argv = getopt.getopt(argv, "", [x + "=" for x in self.attributes + self.elements if x not in self.excludes] + list(self.booleans))
    for o, a in opts:
      o = o[2:]
      handler = getattr(self, "client_query_" + o, None)
      if handler is not None:
        handler(a)
      elif o in self.booleans:
        setattr(self, o, True)
      else:
        assert o in self.attributes
        setattr(self, o, a)
    return argv

  def client_query_bpki_cert(self, arg):
    """Special handler for --bpki_cert option."""
    self.bpki_cert = rpki.x509.X509(Auto_file = arg)

  def client_query_glue(self, arg):
    """Special handler for --bpki_glue option."""
    self.bpki_glue = rpki.x509.X509(Auto_file = arg)

  def client_query_bpki_cms_cert(self, arg):
    """Special handler for --bpki_cms_cert option."""
    self.bpki_cms_cert = rpki.x509.X509(Auto_file = arg)

  def client_query_cms_glue(self, arg):
    """Special handler for --bpki_cms_glue option."""
    self.bpki_cms_glue = rpki.x509.X509(Auto_file = arg)

  def client_query_bpki_https_cert(self, arg):
    """Special handler for --bpki_https_cert option."""
    self.bpki_https_cert = rpki.x509.X509(Auto_file = arg)

  def client_query_https_glue(self, arg):
    """Special handler for --bpki_https_glue option."""
    self.bpki_https_glue = rpki.x509.X509(Auto_file = arg)

  def client_reply_decode(self):
    pass

  def client_reply_show(self):
    print self.element_name
    for i in self.attributes + self.elements:
      if getattr(self, i) is not None:
        print "  %s: %s" % (i, getattr(self, i))

class cmd_msg_mixin(object):
  """Protocol mix-in for command line client message PDUs."""

  @classmethod
  def usage(cls):
    """Generate usage message for this PDU."""
    for k,v in cls.pdus.items():
      print usage_fill(k, v.usage())

# left-right protcol

class self_elt(cmd_elt_mixin, rpki.left_right.self_elt):
  pass

class bsc_elt(cmd_elt_mixin, rpki.left_right.bsc_elt):

  excludes = ("pkcs10_request",)

  def client_query_signing_cert(self, arg):
    """--signing_cert option."""
    self.signing_cert = rpki.x509.X509(Auto_file = arg)

  def client_query_signing_cert_crl(self, arg):
    """--signing_cert_crl option."""
    self.signing_cert_crl = rpki.x509.CRL(Auto_file = arg)

  def client_reply_decode(self):
    global pem_out
    if pem_out is not None and self.pkcs10_request is not None:
      if isinstance(pem_out, str):
        pem_out = open(pem_out, "w")
      pem_out.write(self.pkcs10_request.get_PEM())

class parent_elt(cmd_elt_mixin, rpki.left_right.parent_elt):
  pass

class child_elt(cmd_elt_mixin, rpki.left_right.child_elt):
  pass

class repository_elt(cmd_elt_mixin, rpki.left_right.repository_elt):
  pass

class route_origin_elt(cmd_elt_mixin, rpki.left_right.route_origin_elt):

  def client_query_as_number(self, arg):
    """Handle autonomous sequence numbers."""
    self.as_number = long(arg)

  def client_query_ipv4(self, arg):
    """Handle IPv4 addresses."""
    self.ipv4 = resource_set.roa_prefix_set_ipv4(arg)

  def client_query_ipv6(self, arg):
    """Handle IPv6 addresses."""
    self.ipv6 = resource_set.roa_prefix_set_ipv6(arg)

class left_right_msg(cmd_msg_mixin, rpki.left_right.msg):
  pdus = dict((x.element_name, x)
              for x in (self_elt, bsc_elt, parent_elt, child_elt, repository_elt, route_origin_elt))

class left_right_sax_handler(rpki.left_right.sax_handler):
  pdu = left_right_msg

class left_right_cms_msg(rpki.left_right.cms_msg):
  saxify = left_right_sax_handler.saxify

# Publication protocol

class config_elt(cmd_elt_mixin, rpki.publication.config_elt):

  def client_query_bpki_crl(self, arg):
    """Special handler for --bpki_crl option."""
    self.bpki_crl = rpki.x509.CRL(Auto_file = arg)

class client_elt(cmd_elt_mixin, rpki.publication.client_elt):
  pass

class certificate_elt(cmd_elt_mixin, rpki.publication.certificate_elt):
  pass

class crl_elt(cmd_elt_mixin, rpki.publication.crl_elt):
  pass

class manifest_elt(cmd_elt_mixin, rpki.publication.manifest_elt):
  pass

class roa_elt(cmd_elt_mixin, rpki.publication.roa_elt):
  pass

class publication_msg(cmd_msg_mixin, rpki.publication.msg):
  pdus = dict((x.element_name, x)
              for x in (config_elt, client_elt, certificate_elt, crl_elt, manifest_elt, roa_elt))

class publication_sax_handler(rpki.publication.sax_handler):
  pdu = publication_msg

class publication_cms_msg(rpki.publication.cms_msg):
  saxify = publication_sax_handler.saxify

# Usage

top_opts = ["config=", "help", "pem_out=", "verbose"]

def usage(code = 1):
  print __doc__.strip()
  print
  print "Usage:"
  print
  print "# Top-level options:"
  print usage_fill(*["--" + x for x in top_opts])
  print
  print "# left-right protocol:"
  left_right_msg.usage()
  print
  print "# publication protocol:"
  publication_msg.usage()
  sys.exit(code)

# This should probably be a method of an as-yet-unwritten server class

def call_daemon(cms_class, client_key, client_cert, server_ta, url, q_msg):
  q_cms, q_xml = cms_class.wrap(q_msg, client_key, client_cert, pretty_print = True)
  if verbose:
    print q_xml
  der = rpki.https.client(client_key   = client_key,
                          client_cert  = client_cert,
                          server_ta    = server_ta,
                          url          = url,
                          msg          = q_cms)
  r_msg, r_xml = cms_class.unwrap(der, server_ta, pretty_print = True)
  print r_xml
  for r_pdu in r_msg:
    r_pdu.client_reply_decode()

# Main program

rpki.log.init("irbe_cli")

argv = sys.argv[1:]

if not argv:
  usage(0)

cfg_file = "irbe.conf"
verbose = False

opts, argv = getopt.getopt(argv, "c:hpv?", top_opts)
for o, a in opts:
  if o in ("-?", "-h", "--help"):
    usage(0)
  elif o in ("-c", "--config"):
    cfg_file = a
  elif o in ("-p", "--pem_out"):
    pem_out = a
  elif o in ("-v", "--verbose"):
    verbose = True

if not argv:
  usage(1)

cfg = rpki.config.parser(cfg_file, "irbe_cli")

q_msg_left_right = left_right_msg()
q_msg_left_right.type = "query"

q_msg_publication = publication_msg()
q_msg_publication.type = "query"

while argv:
  if argv[0] in left_right_msg.pdus:
    q_pdu = left_right_msg.pdus[argv[0]]()
    q_msg = q_msg_left_right
  elif argv[0] in publication_msg.pdus:
    q_pdu = publication_msg.pdus[argv[0]]()
    q_msg = q_msg_publication
  else:
    usage(1)
  argv = q_pdu.client_getopt(argv[1:])
  q_msg.append(q_pdu)

if q_msg_left_right:
  call_daemon(
    cms_class   = left_right_cms_msg,
    client_key  = rpki.x509.RSA( Auto_file = cfg.get("rpkid-irbe-key")),
    client_cert = rpki.x509.X509(Auto_file = cfg.get("rpkid-irbe-cert")),
    server_ta   = (rpki.x509.X509(Auto_file = cfg.get("rpkid-bpki-ta")),
                   rpki.x509.X509(Auto_file = cfg.get("rpkid-cert"))),
    url         = cfg.get("rpkid-url"),
    q_msg       = q_msg_left_right)

if q_msg_publication:
  call_daemon(
    cms_class   = publication_cms_msg,
    client_key  = rpki.x509.RSA( Auto_file = cfg.get("pubd-irbe-key")),
    client_cert = rpki.x509.X509(Auto_file = cfg.get("pubd-irbe-cert")),
    server_ta   = (rpki.x509.X509(Auto_file = cfg.get("pubd-bpki-ta")),
                   rpki.x509.X509(Auto_file = cfg.get("pubd-cert"))),
    url         = cfg.get("pubd-url"),
    q_msg       = q_msg_publication)