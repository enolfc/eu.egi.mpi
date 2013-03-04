#
#
#

DESTDIR=.

PROBESNAME=eu.egi.mpi
PROBESDIR=$(DESTDIR)/usr/libexec/grid-monitoring/probes/$(PROBESNAME)

PROBE=complexjob

all:

install: all
	install -d $(PROBESDIR)/$(PROBE)
	install -m 0644 jdl.template $(PROBESDIR)/$(PROBE)/
	install -d $(PROBESDIR)/$(PROBE)/wnjob/etc/wn.d/$(PROBESNAME)
	install -m 0644 etc/commands.cfg $(PROBESDIR)/$(PROBE)/wnjob/etc/wn.d/$(PROBESNAME)
	install -m 0644 etc/services.cfg $(PROBESDIR)/$(PROBE)/wnjob/etc/wn.d/$(PROBESNAME)
	install -d $(PROBESDIR)/$(PROBE)/wnjob/probes/$(PROBESNAME)
	install -m 0755 probe/MPI $(PROBESDIR)/$(PROBE)/wnjob/probes/$(PROBESNAME)
	install -m 0644 probe/pingtest.c $(PROBESDIR)/$(PROBE)/wnjob/probes/$(PROBESNAME)
	install -m 0644 probe/cpi.c $(PROBESDIR)/$(PROBE)/wnjob/probes/$(PROBESNAME)


