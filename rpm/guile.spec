#
# spec file for package guile
#
# Copyright (c) 2021 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

%bcond_without doc
# FIXME: is needed during build guile-procedures.texi but is generated during doc


%global subdirs                     \\\
	lib					            \\\
	meta					        \\\
	libguile				        \\\
	bootstrap				        \\\
	module					        \\\
	guile-readline				    \\\
	examples				        \\\
	emacs					        \\\
	test-suite				        \\\
	benchmark-suite				    \\\
	gc-benchmarks				    \\\
	am %{?with_doc: doc}


# define the name used for versioning libs and directories.
%define guilemaj    3
%define guilemin    0
%define guilevers   %{guilemaj}.%{guilemin}
%define libgver     1
%define gsuff       %{guilemaj}_%{guilemin}-%{libgver}
Name:           guile
Version:        %{guilevers}.8
Release:        0
Summary:        GNU's Ubiquitous Intelligent Language for Extension
License:        GFDL-1.3-only AND GPL-3.0-or-later AND LGPL-3.0-or-later
URL:            https://www.gnu.org/software/guile/
Source0:        %{name}-%{version}.tar.xz
Source3:        guile-rpmlintrc
# Fix the resulting /usr/lib64/pkgconfig/guile-3.0.pc
Patch0:         guile-3.0-gc_pkgconfig_private.patch
# The out-of-memory test is flaky, so disable it
Patch1:         disable-test-out-of-memory.patch
Patch2:         gcc10-x86-disable-one-test.patch
Patch3:         adjust-32bit-big-endian-build-flags.patch
# do sequential build for reproducible .go files = https://issues.guix.gnu.org/issue/20272 - boo#1102408
Patch4:         stage2-serialize.patch
Patch5:         0001-Don-t-enable-tests-that-require-a-network-connection.patch
BuildRequires:  gmp-devel
BuildRequires:  libffi-devel
BuildRequires:  libtool
BuildRequires:  libunistring-devel
BuildRequires:  pkgconfig
BuildRequires:  readline-devel
BuildRequires:  pkgconfig(bdw-gc)
BuildRequires:  gperf
BuildRequires:  flex
# /usr/share/autoconf/Autom4te/FileUtils.pm: autopoint
BuildRequires:  gettext-devel
# dependencies that are present on openSUSE but are not pulled in for Sailfish OS
BuildRequires: pkgconfig(libcrypt)

%{?with_doc:BuildRequires: texinfo}
Requires(pre):  fileutils
Requires(pre):  sh-utils

%description
This is Guile, a portable, embeddable Scheme implementation written in
C. Guile provides a machine independent execution platform that can be
linked in as a library when building extensible programs.

%package -n libguile-%{gsuff}
Summary:        GNU's Ubiquitous Intelligent Language for Extension
License:        GFDL-1.3-only AND GPL-3.0-or-later AND LGPL-3.0-or-later
Requires:       %{name}-modules-%{guilemaj}_%{guilemin} >= %{version}

%description -n libguile-%{gsuff}
This is Guile, a portable, embeddable Scheme implementation written in
C. Guile provides a machine independent execution platform that can be
linked in as a library when building extensible programs. This package
contains the shared libraries.

%package modules-%{guilemaj}_%{guilemin}
Summary:        GNU's Ubiquitous Intelligent Language for Extension
License:        GFDL-1.3-only AND GPL-3.0-or-later AND LGPL-3.0-or-later

%description modules-%{guilemaj}_%{guilemin}
This is Guile, a portable, embeddable Scheme implementation written in
C. Guile provides a machine independent execution platform that can be
linked in as a library when building extensible programs. This package
contains guile modules.

%package devel
Summary:        GNU's Ubiquitous Intelligent Language for Extension
License:        LGPL-2.1-or-later
Requires:       gmp-devel
# following Requires needed because /usr/bin/guile-config needs /usr/bin/guile
Requires:       guile = %{version}
Requires:       libffi-devel
Requires:       libguile-%{gsuff} = %{version}
Requires:       libunistring-devel
Requires:       ncurses-devel
Requires:       readline-devel
Requires:       pkgconfig(bdw-gc)

%description devel
This is Guile, a portable, embeddable Scheme implementation written in
C. Guile provides a machine independent execution platform that can be
linked in as a library when building extensible programs.

%prep
%autosetup -p 1 -n %name-%version/upstream 

# remove broken prebuilt objects
rm -r prebuilt/32-bit-big-endian

%if 0%{?qemu_user_space_build}
# QEMU ignores rlimit requests for setting RLIMIT_AS
echo exit 77 > test-suite/standalone/test-stack-overflow
%endif

%build

# Set tarball version for ./build-aux/git-version-gen
echo %{version}|sed 's/\+.*//' > .tarball-version

autoreconf -fi
# FIXME: lto doesn't work right now
%configure \
  --disable-static \
  --with-pic \
  --enable-lto=no \
  --with-threads \
  --disable-silent-rules
%make_build

%check
LD_LIBRARY_PATH="." \
%make_build check

%install
# Workarund broken make_install argument that doesn't accept arguments :/
# %%{make_install} SUBDIRS:=%%{subdirs}
%{__make} install DESTDIR=%{?buildroot} INSTALL="%{__install} -p"

mkdir -p %{buildroot}%{_datadir}/guile/site
find %{buildroot} -type f -name "*.la" -delete -print
# bug #874028
mkdir -p %{buildroot}%{_datadir}/gdb/auto-load%{_libdir}
mv %{buildroot}%{_libdir}/libguile*-gdb.scm %{buildroot}%{_datadir}/gdb/auto-load%{_libdir}/

%pre
# Remove obsolete files (< SuSE Linux 10.2)
rm -f var/adm/SuSEconfig/md5%{_datadir}/guile/*/slibcat
rm -f usr/share/guile/site/slibcat.SuSEconfig

%post -n libguile-%{gsuff} -p /sbin/ldconfig
%postun -n libguile-%{gsuff} -p /sbin/ldconfig

%files
%doc ABOUT-NLS AUTHORS ChangeLog GUILE-VERSION HACKING
%doc NEWS README THANKS
%{_bindir}/guile-tools
%{_bindir}/guild
%{_bindir}/guile
%if %{with doc}
%{_mandir}/man1/guile.1%{?ext_man}
%endif

%files -n libguile-%{gsuff}
%license LICENSE COPYING*
%{_libdir}/libguile-%{guilevers}.so.%{libgver}*

%files modules-%{guilemaj}_%{guilemin}
%{_libdir}/%{name}
# Own usr/share/guile/site; side effect of not doing so is slib failing to install correctly.
%{_datadir}/%{name}

%files devel
%{_bindir}/guile-snarf
%{_bindir}/guile-config
%dir %{_includedir}/%{name}
%dir %{_includedir}/%{name}/%{guilevers}
%{_includedir}/%{name}/%{guilevers}/*
%{_datadir}/aclocal/guile.m4
%if %{with doc}
%{_infodir}/%{name}.info%{?ext_info}
%{_infodir}/%{name}.info-[0-9]%{ext_info}
%{_infodir}/%{name}.info-1[0-9]%{ext_info}
%{_infodir}/r5rs.info%{?ext_info}
%endif
%{_libdir}/libguile-%{guilevers}.so
%{_libdir}/pkgconfig/guile-%{guilevers}.pc
# bug #874028
%dir %{_datadir}/gdb
%dir %{_datadir}/gdb/auto-load
%dir %{_datadir}/gdb/auto-load%{_prefix}
%dir %{_datadir}/gdb/auto-load/%{_libdir}
%{_datadir}/gdb/auto-load/%{_libdir}/libguile*-gdb.scm
