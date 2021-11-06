Summary: A GNU implementation of Scheme for application extensibility
Name: guile
%define mver 3.0
Version: 3.0.7
Release: 1
Source: ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.xz
URL: http://www.gnu.org/software/guile/
License: LGPLv3+
BuildRequires: gcc
BuildRequires: libtool
BuildRequires: libtool-ltdl-devel
BuildRequires: gmp-devel
BuildRequires: readline-devel
BuildRequires: gettext-devel
BuildRequires: libunistring-devel
BuildRequires: libffi-devel
BuildRequires: pkgconfig(bdw-gc)
BuildRequires: make
BuildRequires: flex
Requires: coreutils

%description
GUILE (GNU's Ubiquitous Intelligent Language for Extension) is a library
implementation of the Scheme programming language, written in C.  GUILE
provides a machine-independent execution platform that can be linked in
as a library during the building of extensible programs.

Install the guile package if you'd like to add extensibility to programs
that you are developing.

%package devel
Summary: Libraries and header files for the GUILE extensibility library
Requires: guile%{?_isa} = %{version}-%{release} gmp-devel pkgconfig(bdw-gc)
Requires: pkgconfig

%description devel
The guile-devel package includes the libraries, header files, etc.,
that you'll need to develop applications that are linked with the
GUILE extensibility library.

You need to install the guile-devel package if you want to develop
applications that will be linked to GUILE.  You'll also need to
install the guile package.

%prep
%setup -q -n %name-%version/upstream

%build
autoreconf -fiv

%configure --disable-static --disable-error-on-warning

# Remove RPATH
sed -i 's|" $sys_lib_dlsearch_path "|" $sys_lib_dlsearch_path %{_libdir} "|' \
    libtool

%{make_build}

%install
%{make_install}

mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/guile/site/%{mver}

rm -f ${RPM_BUILD_ROOT}%{_libdir}/libguile*.la
rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir

# Our gdb doesn't support guile yet
rm -f ${RPM_BUILD_ROOT}%{_libdir}/libguile*gdb.scm

# Compress large documentation
bzip2 NEWS

for i in $RPM_BUILD_ROOT%{_infodir}/goops.info; do
    iconv -f iso8859-1 -t utf-8 < $i > $i.utf8 && mv -f ${i}{.utf8,}
done

touch $RPM_BUILD_ROOT%{_datadir}/guile/site/%{mver}/slibcat

# Create symlinks for compatibility
ln -s guile $RPM_BUILD_ROOT%{_bindir}/guile2
ln -s %{_mandir}/man1/guile.1.gz $RPM_BUILD_ROOT%{_mandir}/man1/guile2.1.gz
ln -s guile-tools $RPM_BUILD_ROOT%{_bindir}/guile2-tools

# Adjust mtimes so they are all identical on all architectures.
# When guile.x86_64 and guile.i686 are installed at the same time on an x86_64 system,
# the *.scm files' timestamps change, as they normally reside in /usr/share/guile/.
# Their corresponding compiled *.go file go to /usr/lib64/, or /usr/lib/, depending on the arch.
# The mismatch in timestamps between *.scm and *.go files makes guile to compile itself
# everytime it's run. The following code adjusts the files so that their timestamps are the same
# for every file, but unique between builds.
# See https://bugzilla.redhat.com/show_bug.cgi?id=1208760.
find $RPM_BUILD_ROOT%{_datadir} -name '*.scm' -exec touch -r "%{_specdir}/guile.spec" '{}' \;
find $RPM_BUILD_ROOT%{_libdir} -name '*.go' -exec touch -r "%{_specdir}/guile.spec" '{}' \;

%ldconfig_scriptlets

%triggerin -- slib >= 3b4-1
rm -f %{_datadir}/guile/site/%{mver}/slibcat
export SCHEME_LIBRARY_PATH=%{_datadir}/slib/

# Build SLIB catalog
%{_bindir}/guile --fresh-auto-compile --no-auto-compile -c \
    "(use-modules (ice-9 slib)) (require 'new-catalog)" &> /dev/null || \
    rm -f %{_datadir}/guile/site/%{mver}/slibcat
:

%triggerun -- slib >= 3b4-1
if [ "$2" = 0 ]; then
    rm -f %{_datadir}/guile/site/%{mver}/slibcat
fi

%files
%license COPYING COPYING.LESSER LICENSE
%doc AUTHORS HACKING NEWS.bz2 README THANKS
%{_bindir}/guile2
%{_bindir}/guile2-tools
%{_bindir}/guild
%{_bindir}/guile
%{_bindir}/guile-tools
%{_libdir}/libguile*.so.*
%{_libdir}/libguilereadline-*.so
%{_libdir}/guile
%dir %{_datadir}/guile
%dir %{_datadir}/guile/%{mver}
%{_datadir}/guile/%{mver}/ice-9
%{_datadir}/guile/%{mver}/language
%{_datadir}/guile/%{mver}/oop
%{_datadir}/guile/%{mver}/rnrs
%{_datadir}/guile/%{mver}/scripts
%{_datadir}/guile/%{mver}/srfi
%{_datadir}/guile/%{mver}/sxml
%{_datadir}/guile/%{mver}/system
%{_datadir}/guile/%{mver}/texinfo
%{_datadir}/guile/%{mver}/web
%{_datadir}/guile/%{mver}/guile-procedures.txt
%{_datadir}/guile/%{mver}/*.scm
%dir %{_datadir}/guile/site
%dir %{_datadir}/guile/site/%{mver}
%ghost %{_datadir}/guile/site/%{mver}/slibcat
%{_infodir}/*
%{_mandir}/man1/guile.1*
%{_mandir}/man1/guile2.1*

%files devel
%{_bindir}/guile-config
%{_bindir}/guile-snarf
%{_datadir}/aclocal/*
%{_libdir}/libguile-%{mver}.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/guile
