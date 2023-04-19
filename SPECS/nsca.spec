%define nsusr nagios
%define nsgrp rgm
%define nsport 5667
# %define nsport 8086

# Reserve option to override port setting with:
# rpm -ba|--rebuild --define 'nsport 5666'
%{?port:%define nsport %{port}}

# Macro that print mesages to syslog at package (un)install time
%define nnmmsg logger -t %{name}/rpm

Summary: Host/service/network monitoring agent for Nagios
URL: http://www.nagios.org
Name: nsca
Version: 2.9.1
Release: 0.rgm
License: GPL
Group: Applications/System
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildRequires: libmcrypt-devel
Requires: bash, nagios, libmcrypt, xinetd
Patch0: nsca-2.9.1-fix-open.patch

# uncomment this for RedHat Enterprise Linux 3:
#PreReq: util-linux, sh-utils, shadow-utils, sed, fileutils, mktemp
# SuSE Linux Enterprise Server 8:
PreReq: util-linux, sh-utils, shadow-utils, sed, fileutils, mktemp 


%description
This program is designed to accept passive service check results from 
clients that use the send_nsca utility and pass them along to the 
Nagios process by using the external command 
interface. The program can either be run as a standalone daemon or as 
a service under inetd. If you have libmcrypt installed on your systems, 
you can choose from multiple crypto algorithms (DES, 3DES, CAST, xTEA, 
Twofish, LOKI97, RJINDAEL, SERPENT, GOST, SAFER/SAFER+, etc.) for 
encrypting the traffic between the client and the server. 
Encryption is important in this addon, as it prevents unauthorized users 
from sending bogus check results to Nagios. Read the included SECURITY 
document for more information. 

This package provides the core agent running on the Nagios server

%package send
Requires: libmcrypt, nagios
Group: Applications/System
Summary: Provides the send_nsca utility running on the Nagios-Client

%description send
This program is designed to accept passive service check results from 
clients that use the send_nsca utility (which is included in this package) 
and pass them along to the Nagios process by using the external command 
interface. The program can either be run as a standalone daemon or as 
a service under inetd. If you have libmcrypt installed on your systems, 
you can choose from multiple crypto algorithms (DES, 3DES, CAST, xTEA, 
Twofish, LOKI97, RJINDAEL, SERPENT, GOST, SAFER/SAFER+, etc.) for 
encrypting the traffic between the client and the server. 
Encryption is important in this addon, as it prevents unauthorized users 
from sending bogus check results to Nagios. Read the included SECURITY 
document for more information. 

This package provides the send_nsca utility running on the client.

%prep
%setup -q
%patch0 -p0

%pre
# Create `nagios' user on the system if necessary
if id %{nsusr} 
then
	: # user already exists
else
        grep nagios /etc/group &>/dev/null || /usr/sbin/groupadd -r nagios 

	/usr/sbin/useradd -r -d /var/log/nagios -s /bin/sh -c "%{nsusr}" -g %{nsgrp} %{nsusr} || \
		%nnmmsg Unexpected error adding user "%{nsusr}". Aborting install process.
fi

# if LSB standard /etc/init.d does not exist,
# create it as a symlink to the first match we find
if [ -d /etc/init.d -o -L /etc/init.d ]; then
  : # we're done
elif [ -d /etc/rc.d/init.d ]; then
  ln -s /etc/rc.d/init.d /etc/init.d
elif [ -d /usr/local/etc/rc.d ]; then
  ln -s  /usr/local/etc/rc.d /etc/init.d
elif [ -d /sbin/init.d ]; then
  ln -s /sbin/init.d /etc/init.d
fi

%postun
/etc/init.d/xinetd restart 

%post
/etc/init.d/xinetd restart 


%build
export PATH=$PATH:/usr/sbin
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" \
./configure \
	--with-nsca-port=%{nsport} \
	--with-nsca-user=%{nsusr} \
	--with-nsca-grp=%{nsgrp} \
	--prefix=""        \
	--bindir=/srv/rgm/nagios/bin \
 	--sysconfdir=/srv/rgm/nagios/etc \
	--localstatedir=/srv/rgm/nagios/var/log \

make all

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
install -b -D -m 0644 sample-config/nsca.cfg ${RPM_BUILD_ROOT}/srv/rgm/nagios/etc/nsca.cfg
install -b -D -m 0644 sample-config/send_nsca.cfg ${RPM_BUILD_ROOT}/srv/rgm/nagios/etc/send_nsca.cfg
install -b -D -m 0644 sample-config/nsca.xinetd ${RPM_BUILD_ROOT}/etc/xinetd.d/nsca
install -b -D -m 0755 src/nsca ${RPM_BUILD_ROOT}/srv/rgm/nagios/bin/nsca
install -b -D -m 0755 src/send_nsca ${RPM_BUILD_ROOT}/srv/rgm/nagios/bin/send_nsca

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(755,root,root)
/etc/xinetd.d/nsca
/srv/rgm/nagios/bin/nsca
%dir /srv/rgm/nagios/etc/
%defattr(644,root,root)
%config(noreplace) /srv/rgm/nagios/etc/*.cfg
%defattr(755,%{nsusr},%{nsgrp})
%doc Changelog LEGAL README SECURITY

%files send
%defattr(755,root,root)
/srv/rgm/nagios/bin/send_nsca
%defattr(644,root,root)
%config(noreplace) /srv/rgm/nagios/etc/send_nsca.cfg
%defattr(755,%{nsusr},%{nsgrp})
%doc Changelog LEGAL README SECURITY

%changelog
* Mon Mar 04 2019 Michael Aubertin <maubertin@fr.scc.com> - 2.9.1-0.rgm
- Initial fork 

* Tue Jan 13 2015 Jean-Philippe Levy <jeanphilippe.levy@gmail.com> - 2.9.1-0.eon
- Upgrade to version 2.9.1

* Tue Aug 27 2013 Jean-Philippe Levy <jeanphilippe.levy@gmail.com> - 2.7.2-2.eon
- Compilation with libmcrypt x86_64

* Wed Feb 02 2011 Jean-Philippe Levy <jeanphilippe.levy@gmail.com> - 2.7.2-1.eon
- Compilation with libmcrypt

* Mon Nov 23 2009 Jean-Philippe Levy <jeanphilippe.levy@gmail.com> - 2.7.2-0.eon 
- First build for EyesOfNetwork 

* Wed Jan 28 2004 Falk H�ppner <fh at honix de>
- Create SPEC from nrpe.spec  
- Tested on ia32/ia64 with SLES8/RHEL3

