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

export DESTDIR
export PROBESDIR
