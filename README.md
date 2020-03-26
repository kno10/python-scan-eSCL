UPDATE 2020: ESCL support was added to SANE Backends 1.0.29 release last month.
With SANE 1.0.29 you should have much easier access to much more functionality than with this prototype!

This prototype project is hence now obsolete.

Scan via WiFi using the eSCL protocol
-------------------------------------

This is a hack, but it works for my Canon PIXMA TS5050 printer (identifies as "TS5000 Series", so I supposed other TS5xxx will work, too), and supposedly works for many other new printers because of the very generic protocol.
Others have reported success with
* [Canon PIXMA TS5055](https://github.com/kno10/python-scan-eSCL/issues/2),
* [Some (unnamed) Kyocera](http://sane-devel.alioth.debian.narkive.com/lQgjGKc3/escl-airprint-support-for-sane)
* [Some (unnamed) HP](http://sane-devel.alioth.debian.narkive.com/lQgjGKc3/escl-airprint-support-for-sane)

This is also known as "Apple AirScan".

I couldn't find any actual documentation for this protocol,
so I mostly used this [blog post by David Poole](http://testcluster.blogspot.de/2014/03/scanning-from-escl-device-using-command.html).

Fortunately, eSCL is a very simple HTTP-based protocol:

1. find the printer by zeroconf/avahi/bonjour

2. query the printer capabilities (an XML file)

3. send XML scan settings by HTTP POST, get a redirect to a new location

4. start the scan by loading the data from the new location.

It's fairly easy to do all this in 100 lines of Python.

Installation and Usage
----------------------
Sorry, I only use Linux. These instructions should work on Debian and Ubuntu.

I used the `zeroconf` and `lxml` python libraries; and Python 2.
```
apt-get install python-zeroconf python-lxml
```

Then scan with
```
python scan.py <file.jpg> <resolution>
```
It will currently default to using the maximum resolution, which may take a while.
Therefore, you may want to use 300 or 600 dpi.

Contributing:
-------------
Of course it would be nice to have a pretty GUI.

This is currently only a tiny prototype, to allow you to test if your scanner works, and make it easy to fiddle with it.

On the long run, it would be best to add an eSCL driver to [SANE](http://www.sane-project.org/)!
