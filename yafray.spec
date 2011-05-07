Name:		yafray
Version:	0.0.9
Release:	%mkrel 8
Summary:	Raytracing tool 
License:	LGPLv2+
Group: 		Graphics
Source0:	http://www.yafray.org/sec/2/downloads/yafray-%{version}.tar.bz2
# From Debian: fixes build with GCC 4.3 - AdamW 2008/07
Patch0:		yafray-0.0.9-gcc43.patch
Patch1:         yafray-0.0.9-gcc44.patch
URL: 		http://www.yafray.org
Buildroot:	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	libjpeg-devel
BuildRequires:	libz-devel
BuildRequires:	OpenEXR-devel
BuildRequires:	scons

%description
YafRay is a graphic raytracer to render 3D models.

%prep
%setup -q -n %{name}
%patch0 -p1 -b .gcc43
%patch1 -p1 -b .gcc44
perl -pi -e 's@/lib@/%{_lib}@g' linux-settings.py
%build

%ifarch %{ix86}
cp -p linux-settings.py linux-settings.ix86
mkdir build-sse2
perl -pi -e \
	's/-O3 -ffast-math -fomit-frame-pointer/%{optflags} -O3 -ffast-math -msse2 -mfpmath=sse/g' linux-settings.py
scons prefix=%{_prefix}
# TODO: also the plugins .so files should be under ./build-sse2, but we need
# to modify the yafray library code so that they will be searched into
# /usr/lib/yafray/sse2/ too, before /usr/lib/yafray/.
# AdamW 2008/07 - libyafrayplugin and libyafraycore are really plugins,
# not shared libraries, and should go to /usr/lib/yafray and /usr/lib/
# yafray/sse2 as well. Debian does this.
cp -p ./src/interface/libyafrayplugin.so \
	./src/yafraycore/libyafraycore.so ./build-sse2
scons -c 
cp -p linux-settings.ix86 linux-settings.py
%endif
perl -pi -e \
	's/-O3 -ffast-math -fomit-frame-pointer/%{optflags} -O3 -ffast-math/g' linux-settings.py
scons prefix=%{_prefix}

%install
rm -rf %{buildroot}
scons install prefix=%{buildroot}%{_prefix}
%ifarch %{ix86}
mkdir -p %{buildroot}%{_prefix}/%{_lib}/sse2
install -m 755 ./build-sse2/libyafrayplugin.so %{buildroot}%{_prefix}/%{_lib}/sse2/
install -m 755 ./build-sse2/libyafraycore.so %{buildroot}%{_prefix}/%{_lib}/sse2/
%endif

# our sysconf dir is /etc not /usr/etc
mv %{buildroot}%{_prefix}/etc %{buildroot}/etc

# remove .sconsign files
find %{buildroot} -name .sconsign -exec rm -f {} \;

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%doc README doc/doc.html
%attr(0755,root,root) %{_bindir}/yafray
%{_sysconfdir}/gram.yafray
# Warning: Module, not development library
%{_libdir}/libyafray*
# Plugins
%{_libdir}/yafray
%ifarch %{ix86}
%{_libdir}/sse2
%endif


