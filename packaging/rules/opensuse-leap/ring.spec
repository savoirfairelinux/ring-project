%define name        ring
%define version     RELEASE_VERSION
%define release     0

Name:          %{name}
Version:       %{version}
Release:       %{release}%{?dist}
Summary:       Free software for distributed and secured communication.
Group:         Applications/Internet
License:       GPLv3+
URL:           https://jami.net/
Source:        ring_%{version}.tar.gz
Requires:      ring-daemon = %{version}
Obsoletes:     ring-gnome

BuildRequires: make
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: cmake
BuildRequires: libcanberra-devel
BuildRequires: libtool
BuildRequires: pcre-devel
BuildRequires: yaml-cpp-devel
BuildRequires: boost-devel
BuildRequires: libXext-devel
BuildRequires: yasm
BuildRequires: speex-devel
BuildRequires: chrpath
BuildRequires: check
BuildRequires: astyle
BuildRequires: gettext-devel
BuildRequires: gcc-c++
BuildRequires: which
BuildRequires: alsa-lib-devel
BuildRequires: systemd-devel
BuildRequires: libuuid-devel
BuildRequires: libXfixes-devel
BuildRequires: uuid-devel
BuildRequires: gnutls-devel
BuildRequires: jsoncpp-devel
BuildRequires: gcc-c++
BuildRequires: gnome-icon-theme-symbolic
BuildRequires: clutter-gtk-devel
BuildRequires: clutter-devel
BuildRequires: glib2-devel
BuildRequires: gtk3-devel
BuildRequires: libnma-devel
BuildRequires: libva-devel
BuildRequires: libvdpau-devel

%description
Ring is free software for universal communication which respects freedoms
and privacy of its users.
.
This package contains the desktop client: jami-gnome.

%package daemon
Summary: Free software for distributed and secured communication - daemon

%description daemon
Ring is free software for universal communication which respects freedoms
and privacy of its users.
.
This package contains the Ring daemon: dring.

%prep
%setup -n ring-project

%build
###########################
## Ring Daemon configure ##
###########################
mkdir -p daemon/contrib/native
cd %{_builddir}/ring-project/daemon/contrib/native && \
    ../bootstrap \
        --no-checksums \
        --disable-ogg \
        --disable-flac \
        --disable-vorbis \
        --disable-vorbisenc \
        --disable-speex \
        --disable-sndfile \
        --disable-gsm \
        --disable-speexdsp \
        --disable-natpmp && \
    make list && \
    make fetch && \
    make -j4 V=1

cd %{_builddir}/ring-project/daemon && \
    ./autogen.sh && \
    ./configure \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --disable-shared

#############################
## libringclient configure ##
#############################
cd %{_builddir}/ring-project/lrc && \
    mkdir build && \
    cd build && \
    cmake \
        -DRING_BUILD_DIR=%{_builddir}/ring-project/daemon/src \
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
        -DCMAKE_BUILD_TYPE=Debug \
        ..

############################
## gnome client configure ##
############################
cd %{_builddir}/ring-project/client-gnome && \
    mkdir build && \
    cd build && \
    cmake \
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
        -DLibRingClient_PROJECT_DIR=%{_builddir}/ring-project/lrc \
        -DGSETTINGS_LOCALCOMPILE=OFF \
        ..

#######################
## Ring Daemon build ##
#######################
make -C %{_builddir}/ring-project/daemon -j4 V=1
pod2man %{_builddir}/ring-project/daemon/man/dring.pod > %{_builddir}/ring-project/daemon/dring.1

#########################
## libringclient build ##
#########################
make -C %{_builddir}/ring-project/lrc/build -j4 V=1

########################
## gnome client build ##
########################
make -C %{_builddir}/ring-project/client-gnome/build LDFLAGS="-lpthread" -j4 V=1


%install
#########################
## Ring Daemon install ##
#########################
DESTDIR=%{buildroot} make -C daemon install
cp %{_builddir}/ring-project/daemon/dring.1 %{buildroot}/%{_mandir}/man1/dring.1
rm -rfv %{buildroot}/%{_prefix}/include
rm -rfv %{buildroot}/%{_libdir}/*.a
rm -rfv %{buildroot}/%{_libdir}/*.la

###########################
## libringclient install ##
###########################
DESTDIR=%{buildroot} make -C lrc/build install
rm -rfv %{buildroot}/%{_prefix}/include

# This is a symlink, should be in -dev package
rm -v %{buildroot}/%{_libdir}/libringclient.so

# cmake files
rm -rfv %{buildroot}/%{_libdir}/cmake

##########################
## gnome client install ##
##########################
DESTDIR=%{buildroot} make -C client-gnome/build install
ln -sf %{_bindir}/jami %{buildroot}/%{_bindir}/ring.cx

%files
%defattr(-,root,root,-)
%{_bindir}/jami
%{_bindir}/ring.cx
%{_bindir}/jami-gnome
%{_libdir}/libringclient*.so*
%{_datadir}/glib-2.0/schemas/net.jami.Jami.gschema.xml
%{_datadir}/applications/jami-gnome.desktop
%{_datadir}/jami-gnome/jami-gnome.desktop
%{_datadir}/icons/hicolor/scalable/apps/jami.svg
%{_datadir}/metainfo/jami-gnome.appdata.xml
%{_datadir}/libringclient/*
%{_datadir}/locale/*
%{_datadir}/sounds/jami-gnome/*
%doc %{_mandir}/man1/dring*

%files daemon
%defattr(-,root,root,-)
%{_libdir}/ring/dring
%{_datadir}/ring/ringtones
%{_datadir}/dbus-1/services/*
%{_datadir}/dbus-1/interfaces/*

%post
/sbin/ldconfig
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/sbin/ldconfig

#for < f24 we have to update the schema explicitly
%if 0%{?fedora} < 24
    if [ $1 -eq 0 ] ; then
        /usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
    fi
%endif

if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
#for < f24 we have to update the schema explicitly
%if 0%{?fedora} < 24
    /usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
%endif

/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
