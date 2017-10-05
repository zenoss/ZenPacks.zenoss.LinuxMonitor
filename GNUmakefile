###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011-2017, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
default: pass

PYTHON=python
SRC_DIR=$(PWD)/src
ZP_NAME=LinuxMonitor
ZP_DIR=$(PWD)/ZenPacks/zenoss/$(ZP_NAME)

pass:
	@echo "pass: do nothing"

egg:
	python setup.py bdist_egg

clean:
	rm -rf build dist *.egg-info
	find . -name '*.pyc' -exec rm {} \;

test:
	runtests -v ZenPacks.zenoss.LinuxMonitor

# Make README.html
docs:
	python docs.py
