#
# Makefile for eu.egi.mpi probes
#
# Copyright (c) 2013 Instituto de Física de Cantabria,
#                    CSIC - UC. All rights reserved.
#
#

DESTDIR=.

PROBESNAME=eu.egi.mpi
PROBESDIR=$(DESTDIR)/usr/libexec/grid-monitoring/probes/$(PROBESNAME)

all:


install: all
	install -d $(PROBESDIR)
	$(MAKE) -C etc install
	$(MAKE) -C bdiisanity install
	$(MAKE) -C simplejob install
	$(MAKE) -C complexjob install

dist:
	mkdir -p build
	rm -rf build/$(PROBESNAME).src.tar.gz
	git archive --prefix $(PROBESNAME)/ master | gzip > build/$(PROBESNAME).src.tar.gz

rpm: dist
	mkdir -p build/SOURCES build/SRPMS build/SPECS build/BUILD build/RPMS
	cp build/$(PROBESNAME).src.tar.gz build/SOURCES
	cp $(PROBESNAME).spec build/SPECS
	rpmbuild --define "_topdir `pwd`/build" -bs build/SPECS/$(PROBESNAME).spec
	rpmbuild $(PACKAGER) --define "_topdir `pwd`/build" -bb build/SPECS/$(PROBESNAME).spec

clean:
	rm -rf build

export DESTDIR
export PROBESDIR
