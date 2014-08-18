#
# Copyright (c) 2013 Instituto de Física de Cantabria,
#                    CSIC - UC. All rights reserved.
#


%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: A MPI Nagios monitoring probe.
Name: egi-mpi-nagios
Version: 0.0.7
Vendor: EGI 
Release: 1%{?dist}
License: ASL 2.0
Group: System Environment/Daemons 
Source: %{name}.src.tar.gz
URL: https://wiki.egi.eu/wiki/VT_MPI_within_EGI:Nagios
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python-setuptools
Requires: python
Requires: python-ldap
Requires: python-setuptools
Requires: emi-cream-nagios
BuildArch: noarch

%description
This package contains the probes for testing MPI support in the EGI.eu infrastructure.
Full description of probes is available at https://wiki.egi.eu/wiki/VT_MPI_within_EGI:Nagios.

%prep
%setup -q -n %{name}

%build
cd $RPM_BUILD_DIR/%{name}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
cd $RPM_BUILD_DIR/%{name}
%{__make} DESTDIR=$RPM_BUILD_ROOT install

%files
%defattr(-,root,root)
/usr/libexec/grid-monitoring/probes/eu.egi.mpi
# %config %{_sysconfdir}/ncg-metric-config.d/eu.egi.mpi.conf
%{python_sitelib}/mpimetrics*
%doc README

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Aug 18 2014 Enol Fernandez <enolfc _AT_ ifca.unican.es> - 0.0.7-%{release}
- Fix bdii check probe (issue #9)
- Change in the bdii probe structure (as a python package)
* Fri Nov 29 2013 Enol Fernandez <enolfc _AT_ ifca.unican.es> - 0.0.6-%{release}
- Fix complex probe (issue #8).
- Fix bdii check probe.
* Tue Jul 16 2013 Enol Fernandez <enolfc _AT_ ifca.unican.es> - 0.0.5-%{release}
- Removed WholeNode requirement for complex job 
* Wed May 29 2013 Enol Fernandez <enolfc _AT_ ifca.unican.es> - 0.0.4-1%{?dist}
- Fixed minor bdii probe issues
* Thu May 2 2013 Emir Imamagic <eimamagi@srce.hr> - 0.0.3-1%{?dist}
- Removed ncg-metric-config file
* Wed May 1 2013 Emir Imamagic <eimamagi@srce.hr> - 0.0.2-1%{?dist}
- Modified test configuration for EMI CREAM-CE probe
- Added CREAM-CE probe requirement
* Mon Mar 04 2013 <enolfc _AT_ ifca.unican.es> - 0.0.1-1%{?dist}
- Initial packaging of the probes. 
