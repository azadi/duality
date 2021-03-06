Duality 
=======

The Social BitTorrent Client

Introduction
------------

Duality is a new approach to downloading files over the BitTorrent protocol.

If you are interested, we have a nice [introduction](http://www.duality.sukhbir.in/idea.html) to get you started.

Requirements
------------

1. Python 2.6+ (2.7 is not supported)
2. [libtorrent](http://www.rasterbar.com/products/libtorrent/) and the Python bindings

Installation
------------

[Detailed instructions](http://www.duality.sukhbir.in/installation.html) are available on author's website.

Basic Usage
-----------

The [manual](http://www.duality.sukhbir.in/manual.html) should cover everything you need to know.

Download stops at 99.99%
------------------------

If your download stops at 99.99%, this might be due a to a bug in `libtorrent`. The `RC_0_15` branch from the [SVN repository](http://libtorrent.svn.sourceforge.net/viewvc/libtorrent/) fixes this bug. Install that and this issue should be resolved.

Authors
-------

Written by Sukhbir Singh.
Uses the `libtorrent` library, written by Arvid Norberg.
