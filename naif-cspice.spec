Name:              naif-cspice
Version:           1.67
Release:           1%{?dist}
Summary:           The NAIF CSPICE Toolkit by NASA JPL
License:           Apache-2.0
URL:               https://naif.jpl.nasa.gov/naif/toolkit.html
Source0:           https://naif.jpl.nasa.gov/pub/naif/misc/toolkit_N0067/C/PC_Linux_GCC_64bit/packages/cspice.tar.Z
BuildRequires:     tcsh
BuildRequires:     gcc
BuildRequires:     sed
Requires:          %{name}-libs{_isa} = %{version}-%{release}

%description

The NAIF CSPICE Toolkit, together with data obtained from the JPL Horizons 
system, is commonly used for obtaining precise orbital data for planets, 
moons, asteroids, comets, and spacecraft. It can provide precise positions, 
velocities, orientation, and in some cases shape information on the above 
mentions orbiting bodies.

The Navigation and Ancillary Information Facility (NAIF), acting under the 
directions of NASA's Planetary Science Division, has built an information 
system named "SPICE" (Spacecraft, Planet, Instrument, C-matrix, Events) to 
assist NASA scientists in planning and interpreting scientific observations 
from space-borne instruments, and to assist NASA engineers involved in 
modeling, planning and executing activities needed to conduct planetary 
exploration missions.

This package is redistributed with the explicit permission by NAIF, and in 
accordance with the upstream licensing terms.

%package libs
Summary:		Shared libraries for the NAIF CSPICE Toolkit

%description libs
The shared libraries that provide the functionality for the NAIF CSPICE
Toolkit.

%package devel
Summary:		Development files for the NAIF CSPICE Toolkit
Requires:		%{name}-libs{_isa} = %{version}-%{release}

%description devel
C headers and non-versioned shared libraries for building applications
against the NAIF CSPICE Toolkit.

%package doc
Summary:		Documentation for the the NAIF CSPICE Toolkit
BuildArch:		noarch

%description doc
HTML documentation for the JPL CSPICE Toolkit.	



%prep
%setup -q -n cspice

# The upstream tarball comes with prebuilt executables, does not contain a 
# license file, and uses static libraries in the build. Thus we need to 
# modify the upstream heavily to make it suitable for packaging for Fedora.
cd %{_builddir}/cspice

# ----------------------------------------------------------------------------
# Clean out the pre-built binaries that shipped with upstream archive
rm -rf lib/* exe/*

# ----------------------------------------------------------------------------
# Create a LICENSE file...
echo "Copyright 1982 National Aeronautics and Space Administration (NASA)" > LICENSE
echo "" >> LICENSE
echo "Licensed under the Apache License, Version 2.0 (the "License");" >> LICENSE
echo "you may not use this file except in compliance with the License." >> LICENSE
echo "You may obtain a copy of the License at" >> LICENSE
echo "" >> LICENSE
echo "    http://www.apache.org/licenses/LICENSE-2.0" >> LICENSE
echo "" >> LICENSE
echo "Unless required by applicable law or agreed to in writing, software" >> LICENSE
echo "distributed under the License is distributed on an "AS IS" BASIS," >> LICENSE
echo "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied." >> LICENSE
echo "See the License for the specific language governing permissions and" >> LICENSE
echo "limitations under the License." >> LICENSE
echo "" >> LICENSE
echo "Exceptions to the above licensing terms:" >> LICENSE
echo "" >> LICENSE
echo "Redistribution of the unmodified SPICE Toolkit, such as from a mirror site, is" >> LICENSE 
echo "prohibited without prior, written clearance from the NAIF manager. However," >> LICENSE 
echo "including the SPICE Toolkit modules (source and object code), documentation," >> LICENSE 
echo "and relevant SPICE Toolkit programs and allied User Guides as part of a" >> LICENSE 
echo "package supporting a customer-built SPICE-based tool is entirely appropriate." >> LICENSE
echo "This includes providing a new 3rd party interface to the SPICE Toolkit," >> LICENSE 
echo "subject to the relevant rules listed elsewhere on the webpage:" >> LICENSE
echo "" >> LICENSE
echo "    https://naif.jpl.nasa.gov/naif/rules.html" >> LICENSE
echo "" >> LICENSE

# ----------------------------------------------------------------------------
# Modify the build scripts for shared libs, and for packaging.
cd src

for component in * ; do
  if [ -d $component ] ; then
    if [ "$component" == "cspice" -o "$component" == "csupport" -o "$component" == "cook_c" ] ; then
      # Don't used default build for static libs or cookbook examples. 
      # We don't package these...
      rm -f $component/*.pgm
      echo "" > $component/mkprodct.csh
    else 
      # Don't link executables against static libs
      sed -i "s:../../lib/cspice.a::g" $component/mkprodct.csh
      sed -i "s:../../lib/csupport.a::g" $component/mkprodct.csh
    fi
  fi
done


%build

# ----------------------------------------------------------------------------
# Additional compiler flags we need.
# It's an old library, with parts converted from FORTRAN. 
# Some functions do not declare a return value, so we must allow implitic-int
# and also other compat flags since we do not control the source code.
CFLAGS="$CFLAGS -ansi -DNON_UNIX_STDIO -Wno-implicit-int -fno-strict-aliasing"

# Flags for linking shared libraries
SO_LINK="-shared -fPIC -Wl,-soname,libcspice.so.1 $LDFLAGS -lm"

# ----------------------------------------------------------------------------
# Build shared lib first (our way)
gcc -o lib/libcspice.so src/cspice/*.c src/csupport/*.c $CFLAGS $SO_LINK

# ----------------------------------------------------------------------------
# Now we can run the modified build scripts...

# Set up variables for build scripts
export TKCOMPILER=gcc
export TKCOMPILEOPTIONS="-c $CFLAGS"
export TKLINKOPTIONS="$LDFLAGS -L$(pwd)/lib -lcspice -lm"

# Locating the shared libraries for local builds
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$(pwd)/lib"

# Now build the executables
csh makeall.csh



%install

# ----------------------------------------------------------------------------
# Shared libs
mkdir -p %{buildroot}/%{_libdir}

# libcspice.so...
install -m 755 lib/libcspice.so %{buildroot}/%{_libdir}/libcspice.so.%{version}

# Link libcspice.so.1.XX -> libcspice.so.1
( cd %{buildroot}/%{_libdir} ; ln -sf libcspice.so.%{version} libcspice.so.1 )

# Link libcspice.so.1 -> libcspice.so
( cd %{buildroot}/%{_libdir} ; ln -sf libcspice.so.1 libcspice.so )


# ----------------------------------------------------------------------------
# Executables
mkdir -p %{buildroot}/%{_bindir}
install -m 755 -D exe/* %{buildroot}/%{_bindir}


# ----------------------------------------------------------------------------
# C header files
# They are many, so we'll put them into a cspice sub-directory...
mkdir -p %{buildroot}/%{_prefix}/include/%{name}
install -m 644 -D include/* %{buildroot}/%{_prefix}/include/%{name}


# ----------------------------------------------------------------------------
# HTML docs
mkdir -p %{buildroot}/%{_docdir}/%{name}/html/
install -m 644 -D doc/html/*.html %{buildroot}/%{_docdir}/%{name}/html

mkdir -p %{buildroot}/%{_docdir}/%{name}/html/cspice
install -m 644 -D doc/html/cspice/* %{buildroot}/%{_docdir}/%{name}/html/cspice

mkdir -p %{buildroot}/%{_docdir}/%{name}/html/info
install -m 644 -D doc/html/info/* %{buildroot}/%{_docdir}/%{name}/html/info

mkdir -p %{buildroot}/%{_docdir}/%{name}/html/req
install -m 644 -D doc/html/req/* %{buildroot}/%{_docdir}/%{name}/html/req

mkdir -p %{buildroot}/%{_docdir}/%{name}/html/ug
install -m 644 -D doc/html/ug/* %{buildroot}/%{_docdir}/%{name}/html/ug


%files
%{_bindir}/*
%license LICENSE
%doc doc/version.txt
%doc doc/whats.new

%files libs
%{_libdir}/libcspice.so.1{,.*}
%license LICENSE
%doc doc/version.txt
%doc doc/whats.new

%files devel
%{_prefix}/include/*
%{_libdir}/libcspice.so
%license LICENSE
%doc doc/version.txt
%doc doc/whats.new

%files doc
%dir %{_docdir}/%{name}/html
%doc %{_docdir}/%{name}/html/*


%changelog
%autochangelog

