#
#
#

DESTDIR=.

PROBESNAME=eu.egi.mpi
PROBESDIR=$(DESTDIR)/usr/libexec/grid-monitoring/probes/$(PROBESNAME)

all:


install: all
	install -d $(PROBESDIR)/bdiisanity
	install -m 0755 checkbdii $(PROBESDIR)/bdiisanity/
