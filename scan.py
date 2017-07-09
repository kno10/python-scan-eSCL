#!/usr/bin/python
import urllib, urllib2, sys, tempfile
from lxml import etree

# Usage: python scan.py "filename.jpg" "600"
onam = sys.argv[1] if len(sys.argv) > 1
resolution = sys.argv[2] if len(sys.argv) > 2
scanner = None

##### Scanner discovery via zeroconf:
import zeroconf, time
timeout = 30
sb = None

class ZCListener:
    def remove_service(self, zeroconf, type, name):
        pass
    def add_service(self, zeroconf, type, name):
        global scanner, sb
        info = zeroconf.get_service_info(type, name)
        # TODO: verify that info.rs = "eSCL"?
        # TODO: verify that info.is = "platen"?
        scanner = "http://%s:%d/eSCL/" % (info.server, info.port)
        print("Found scanner '%s' at '%s'" % (info.name, info.server))

zc = zeroconf.Zeroconf()
sb = zeroconf.ServiceBrowser(zc, "_uscan._tcp.local.", listener=ZCListener())

try:
    for i in range(0, timeout * 10):
        if scanner: break
        time.sleep(.1)
except: pass
sb.cancel()

if not scanner:
    sys.stderr.write("No scanner found within %f seconds.\n" % timeout)
    sys.exit(1)

######### Get scanner configuration:

scanns = "http://schemas.hp.com/imaging/escl/2011/05/03"
pwgns = "http://www.pwg.org/schemas/2010/12/sm"

etree.register_namespace('scan', scanns)
etree.register_namespace('pwg', pwgns)

req = urllib2.Request(url = scanner+'ScannerCapabilities')
tree = etree.parse(urllib2.urlopen(req))
print("Scanner information:")
print etree.tostring(tree, pretty_print=True)

maxwid = etree.ETXPath("//{%s}MaxWidth" % scanns)(tree)[0].text
maxhei = etree.ETXPath("//{%s}MaxHeight" % scanns)(tree)[0].text

if not resolution:
    maxxr = etree.ETXPath("//{%s}MaxOpticalXResolution" % scanns)(tree)[0].text
    maxyr = etree.ETXPath("//{%s}MaxOpticalYResolution" % scanns)(tree)[0].text
    resolution = min(int(maxxr), int(maxyr))

req = etree.Element("{%s}ScanSettings" % scanns, nsmap={"pwg":pwgns})
etree.SubElement(req, "{%s}Version" % pwgns).text = "2.6"
srs = etree.SubElement(req, "{%s}ScanRegions" % pwgns)
sr = etree.SubElement(srs, "{%s}ScanRegion" % pwgns)
etree.SubElement(sr, "{%s}XOffset" % pwgns).text = "0"
etree.SubElement(sr, "{%s}YOffset" % pwgns).text = "0"
etree.SubElement(sr, "{%s}Width" % pwgns).text = maxwid
etree.SubElement(sr, "{%s}Height" % pwgns).text = maxhei
etree.SubElement(sr, "{%s}ContentRegionUnits" % pwgns).text = "escl:ThreeHundredthsOfInches"
etree.SubElement(req, "{%s}InputSource" % scanns).text = "Platen"
# Default is usually RGB24 anyway
etree.SubElement(req, "{%s}ColorMode" % scanns).text = "RGB24"
etree.SubElement(req, "{%s}XResolution" % scanns).text = str(resolution)
etree.SubElement(req, "{%s}YResolution" % scanns).text = str(resolution)

print("Our scan request:")
print(etree.tostring(req, pretty_print=True, xml_declaration=True, encoding="UTF-8"))

# Post the request:
xml = etree.tostring(req, xml_declaration=True, encoding="UTF-8")
req = urllib2.Request(url = scanner+'ScanJobs', data=xml,
        headers={'Content-Type': 'text/xml'})
location = None
try:
    import logging, urllib2, sys

    hh = urllib2.HTTPHandler()
    hsh = urllib2.HTTPSHandler()
    hh.set_http_debuglevel(1)
    hsh.set_http_debuglevel(1)
    opener = urllib2.build_opener(hh, hsh)
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.NOTSET)
    # opener.open(req)
    response = urllib2.urlopen(req)
    print (response.info())
    location = response.info().getheader("Location")
except urllib2.HTTPError as e:
    if e.code != 201:
        print(e.code)
        print(e.read())
        print(e.headers)
        print(e.msg)
        sys.exit(1)
    print(e.headers)
    location = e.headers.get("Location")

if not location:
    sys.stderr.write("No location received.\n")
    sys.exit(1)

if onam:
    of = open(onam, "w")
else:
    of = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    onam = of.name
print("Scanning to: %s" % onam)
req = urllib2.Request(url = location + "/NextDocument")
data = urllib2.urlopen(req)
of.write(data.read())
of.close()
print("Scan saved to: %s" % of.name)
