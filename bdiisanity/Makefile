#
#
#

DESTDIR=.

PROBESNAME=eu.egi.mpi
PROBEDIR=usr/libexec/grid-monitoring/probes/$(PROBESNAME)/bdiisanity

all:


install: all
	install -d $(DESTDIR)/$(PROBEDIR)
	python setup.py install --root $(DESTDIR) \
		--install-scripts $(PROBEDIR)
