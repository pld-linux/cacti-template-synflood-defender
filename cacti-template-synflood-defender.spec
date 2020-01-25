%define		template synflood-defender
Summary:	Template for Cacti - Synflood-Defender
Name:		cacti-template-%{template}
Version:	0.1.0
Release:	1
License:	GPL v2
Group:		Applications/WWW
Source0:	http://synflood-defender.net/_media/download/synflooddefender-%{version}-linux.tar.gz
# Source0-md5:	d744ae65a69edbf893c86e36498be85a
Source1:	http://synflood-defender.net/_media/download/synflooddefender_cacti_tpls.tar.gz
# Source1-md5:	f0002aa57955008dc5e51b11c1c3cdc6
Patch0:		iproute.patch
URL:		http://synflood-defender.net/
BuildRequires:	rpm-php-pearprov >= 4.4.2-11
BuildRequires:	rpmbuild(macros) >= 1.554
Requires:	cacti >= 0.8.7e-8
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		cactidir		/usr/share/cacti
%define		resourcedir		%{cactidir}/resource
%define		scriptsdir		%{cactidir}/scripts
%define		_libdir			%{_prefix}/lib
%define		snmpdconfdir	/etc/snmp
%define		snmpdextend		synflooddefender

%description
Synflood-Defender is an extension for SNMP protocol, which is used for
monitoring SYN-queue and protection the host if SYN-flood attack
happens.

Features:
- monitoring SYN-queue
- changing TCP kernel parameters "on-the-fly" when threshold is
  reached
- 2 protection modes: dynamic and force
- the ability to specify kernel parameters you want to change
- templates for Cacti are available for download
- the ability to integrate with any monitoring system which supports
  SNMP

%package -n net-snmp-agent-synflood-defender
Summary:	SNMPd agent to for Synflood Defender
Group:		Networking/Daemons
Requires:	net-snmp
# for ss
Requires:	iproute2

%description -n net-snmp-agent-synflood-defender
SNMPd agent to for Synflood Defender.

%prep
%setup -qn synflooddefender-%{version}-linux -a1
mv synflooddefender_cacti_tpls/*.xml .
%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{resourcedir},%{scriptsdir},%{_sysconfdir}/%{template},%{_libdir}}
cp -p *.xml $RPM_BUILD_ROOT%{resourcedir}

cp -p %{template}.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{template}
cp -p state $RPM_BUILD_ROOT%{_sysconfdir}/%{template}
cp -p %{template}.sh $RPM_BUILD_ROOT%{_libdir}/%{template}

%post
%cacti_import_template %{resourcedir}/cacti_data_template_%{template}.xml
%cacti_import_template %{resourcedir}/cacti_graph_template_%{template}.xml

%clean
rm -rf $RPM_BUILD_ROOT

%post -n net-snmp-agent-%{template}
if ! grep -qF %{snmpdextend} %{snmpdconfdir}/snmpd.local.conf; then
	echo "extend %{snmpdextend} %{_libdir}/%{template}" >> %{snmpdconfdir}/snmpd.local.conf

	%service -q snmpd reload
fi

%preun -n net-snmp-agent-%{template}
if [ "$1" = 0 ]; then
	if [ -f %{snmpdconfdir}/snmpd.local.conf ]; then
		%{__sed} -i -e "/extend %{snmpdextend}/d" %{snmpdconfdir}/snmpd.local.conf
		%service -q snmpd reload
	fi
fi

%files
%defattr(644,root,root,755)
%{resourcedir}/cacti_data_template_%{template}.xml
%{resourcedir}/cacti_graph_template_%{template}.xml

%files -n net-snmp-agent-%{template}
%defattr(644,root,root,755)
%dir %{_sysconfdir}/%{template}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{template}/%{template}.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{template}/state
%attr(755,root,root) %{_libdir}/%{template}
