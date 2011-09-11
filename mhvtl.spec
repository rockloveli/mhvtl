Summary: Virtual tape library. kernel pseudo HBA driver + userspace daemons
Name: mhvtl
Version: 1.0
Release: 1
Source: mhvtl-2011-09-11.tgz
License: GPL
Group: System/Kernel
BuildRoot: /var/tmp/%{name}-buildroot
URL: http://sites.google.com/site/linuxvtl2/
requires: zlib

%description
A Virtual tape library and tape drives:

Used to emulate hardware robot & tape drives:

VTL consists of a pseudo HBA kernel driver and user-space daemons which
function as the SCSI target.

Communication between the kernel module and the daemons is achieved
via /dev/mhvtl? device nodes.

The kernel module is based on the scsi_debug driver.
The SSC/SMC target daemons have been written from scratch.

Note: Currently, the kernel module needs to be built separately. For
      instructions install src.rpm and read the INSTALL file.

%prep
%setup

%build
make RPM_OPT_FLAGS="$RPM_OPT_FLAGS" VERSION=%{version}.%{release} usr
make RPM_OPT_FLAGS="$RPM_OPT_FLAGS" VERSION=%{version}.%{release} etc
make RPM_OPT_FLAGS="$RPM_OPT_FLAGS" VERSION=%{version}.%{release} scripts

%install
[ "%{buildroot}" != "/" ] && rm -rf %[buildroot}

mkdir -p $RPM_BUILD_ROOT/etc/init.d
mkdir -p $RPM_BUILD_ROOT/etc/mhvtl
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/man/man1
mkdir -p $RPM_BUILD_ROOT/usr/share/man/man5

%ifarch x86_64 amd64 ppc64
mkdir -p $RPM_BUILD_ROOT/usr/lib64
%else
mkdir -p $RPM_BUILD_ROOT/usr/lib
%endif

install -m 750 etc/mhvtl $RPM_BUILD_ROOT/etc/init.d/mhvtl
install -m 750 -s usr/vtltape $RPM_BUILD_ROOT/usr/bin/vtltape
install -m 750 -s usr/vtllibrary $RPM_BUILD_ROOT/usr/bin/vtllibrary
install -m 750 usr/vtlcmd $RPM_BUILD_ROOT/usr/bin/vtlcmd
install -m 750 usr/mktape $RPM_BUILD_ROOT/usr/bin/mktape
install -m 750 usr/dump_tape $RPM_BUILD_ROOT/usr/bin/dump_tape
install -m 700 usr/build_library_config $RPM_BUILD_ROOT/usr/bin/build_library_config
install -m 700 usr/make_vtl_media $RPM_BUILD_ROOT/usr/bin/make_vtl_media
install -m 700 usr/tapeexerciser $RPM_BUILD_ROOT/usr/bin/tapeexerciser

%ifarch x86_64 amd64 ppc64
install -m 755 usr/libvtlscsi.so $RPM_BUILD_ROOT/usr/lib64/libvtlscsi.so
%else
install -m 755 usr/libvtlscsi.so $RPM_BUILD_ROOT/usr/lib/libvtlscsi.so
%endif

install -m 644 man/build_library_config.1 $RPM_BUILD_ROOT%{_mandir}/man1/build_library_config.1
install -m 644 man/mktape.1 $RPM_BUILD_ROOT%{_mandir}/man1/mktape.1
install -m 644 man/mhvtl.1 $RPM_BUILD_ROOT%{_mandir}/man1/mhvtl.1
install -m 644 man/vtlcmd.1 $RPM_BUILD_ROOT%{_mandir}/man1/vtlcmd.1
install -m 644 man/vtllibrary.1 $RPM_BUILD_ROOT%{_mandir}/man1/vtllibrary.1
install -m 644 man/vtltape.1 $RPM_BUILD_ROOT%{_mandir}/man1/vtltape.1
install -m 644 man/library_contents.5 $RPM_BUILD_ROOT%{_mandir}/man5/library_contents.5
install -m 644 man/device.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/device.conf.5

%pre
if ! getent group vtl > /dev/null 2>&1; then
 if [ -f /etc/SuSE-release ]; then
   groupadd --system vtl
 elif [ -f /etc/redhat-release ]; then
   groupadd -r vtl
 else
   groupadd vtl
 fi
fi
if ! getent passwd vtl > /dev/null 2>&1; then
 if [ -f /etc/SuSE-release ]; then
   useradd --system -g vtl -c "VTL daemon" -d /opt/mhvtl -m -s /bin/bash vtl
 elif [ -f /etc/redhat-release ]; then
   useradd -r -g vtl -c "VTL daemon" -d /opt/mhvtl -s /bin/bash vtl
 else
   useradd -g vtl -c "VTL daemon" -d /opt/mhvtl -s /bin/bash vtl
 fi
fi
if [ -x /etc/init.d/vtl ]; then
 /etc/init.d/vtl shutdown
fi
if [ -x /etc/init.d/mhvtl ]; then
 /etc/init.d/mhvtl shutdown
fi

%post
/sbin/ldconfig
r=`/sbin/chkconfig --list|grep mhvtl|awk '{print $1}'`
if [ "X"$r == "X" ]; then
	/sbin/chkconfig --add mhvtl
	/sbin/chkconfig mhvtl on
fi
if [ -d /opt/mhvtl ]; then
	chown -R vtl:vtl /opt/mhvtl
fi
# Set the 'GID' bit on the directory so all child files get same group ID
if [ ! -g /opt/mhvtl ]; then
	chmod 2770 /opt/mhvtl
fi

%preun
if [ -x /etc/init.d/mhvtl ]; then
 /etc/init.d/mhvtl shutdown
fi

%postun
/sbin/ldconfig
if getent passwd vtl > /dev/null 2>&1; then
 userdel vtl
fi

if getent group vtl > /dev/null 2>&1; then
 groupdel vtl
fi

%clean
if [ "$RPM_BUILD_ROOT" == "/" ];then
 echo "Attempt to remove / failed! - Fix RPM_BUILD_ROOT macro"
else
 rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,vtl,vtl)
%doc INSTALL README etc/library_contents.sample
/etc/init.d/mhvtl
%{_bindir}/vtlcmd
%attr(4750, root, vtl) %{_bindir}/vtltape
%attr(4750, root, vtl) %{_bindir}/vtllibrary
%{_bindir}/mktape
%{_bindir}/dump_tape
%{_bindir}/tapeexerciser
%{_bindir}/build_library_config
%{_bindir}/make_vtl_media
%ifarch x86_64 amd64 ppc64
%{_prefix}/lib64/libvtlscsi.so
%else
%{_prefix}/lib/libvtlscsi.so
%endif
%doc %{_mandir}/man1/*
%doc %{_mandir}/man5/*

%changelog
* Sun Sep 11 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 1.0.1
- Added mode page 25h (vendor specific) for IBM LTO3/4/5
  This allows the Windows IBM Tape Driver to load correctly (connected via
  iSCSI)
- Attempt to correct file permission/ownership when media is created manually
- A HUP signal to the vtllibrary daemon will cause it to re-read its config
  from the /etc/mhvtl/library_contents.XX file. (So you can change the slot
  config without having to re-start the daemon).

* Sun Sep 04 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 1.00.00
- Re-worked MODE SENSE/SELECT data structures into a linked list.
- Re-worked LOG SENSE/SELECT data structures into a linked list.
- Added support for sub-page MODE information.
- Added STK 9x40 drive emulations.
- Removed dead code from kernel driver.
- Add working REPORT DENSITY support to the SSC.
  This change required the personality modules to define the list of supported
  densities. The media density is defined at 'mktape' time.
  Hence, the optional 'media load' rules in device.conf are now redundent
  and not used.
  BUT: The option to load any media into any drive is also gone.

* Sat Jun 25 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.17
- Improvements
  - Kernel module compile warning since 2.6.33
- Bug fixes
  - Test MAP port open before moving media
  - Fix buffer overflow in vtllibrary (product_id)
  - Return correct sense from space op code

* Sun May 22 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.16
- Improvements
  - Cleaning media behaves more like real (IBM LTO4) drive.
  - Implement OPEN/CLOSE IMPORT/EXPORT element OP code (Thanks Sebastian)
  - Kernel module support for 2.6.39 (Thanks Sebastian)
- Bug fixes
  - SPACE op code - Space to end-of-data fixed (Thanks Sebastian)
    This fixes an issue triggered using Oracle Backup
  - REQUEST SENSE - Return correct data.
  - SPOUT - Return check_condition on some error paths
  - Cleaning Media - Return 'not ready' instead of 'good' when loaded
  - Don't write FILEMARKS to WORM or Cleaning media

* Wed May 04 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.15
- Improvements
  - Implemented 'Personality Module' for each drive type
    (many cleanups due to 'PM' change fallout thanks to Sebastian)
  - Increase max barcode length to 16 chars
- Bug fixes
  - Inquiry no longer incorrectly reports support for TrmIOP and CmdQue
  - Fixed block read/writes corruption if 'multiple blocks' specified
  - Fix Device Capabilities mode page - Don't advertise EXCHANGE MEDIUM support

* Thu Mar 17 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.14
- Bug fixes:
  - kernel module build fixes for Linux kernel 2.6.37 and greater
- Improvements
  - Add STK T10000C media/drive support
  - Always log 'fatal' errors
  - Cleanup to mhvtl.spec
  - Catch signals to prevent daemon terminating early.

* Thu Jan 11 2011 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.13
- Bug fixes:
  - SMC read element status. Return correct length.
  - SMC read element status. Handle request for 'any' slot type.
  - SSC log page. Byte-swap Bytes Read/Written.
  - vtltape: Return ILLEGAL REQUEST for unsupported OP codes.
  - Density code updates.
  - Increased sense buffer from 38 bytes to 96 bytes.

* Wed Nov 17 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.12
- Bug fixes:
  - Silence 'which setuidgid' test
  - Fix compile on 2.6.34 kernel
  - ERASE only from BOT
  - Test SPACE '0' blocks/filemarks before moving
  - Fix REQUEST SENSE returned size
  - Implement SILI bit test
  - Check if ERASE WORM media is allowed
  - Only support SPIN/SPOUT for LTO-4/5, T10K and 3592E05/6 drive types
  - Fix REQUEST SENSE page length. Previously only returning 8 bytes.
- Improvements
  - Re-organised code in vtllibrary to use a big jump table
  - Fix LTO5 media density reporting
  - Match HP ULTRIUM 4-SCSI
  - Ability to create DDS specific media
    (still need to find correct density codes for DDS)

* Thu Sep 23 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.11
- Bug fix: Off-by-one if a re-position & then overwrite a filemark.
  Caused TSM & HP Dataprotector all sorts of problems.
- Export kernel module 'major' number via /sys/bus/pseudo/drivers/mhvtl/major
- Remove external script to create device nodes. Each daemon creates its own
  device node at startup. Uses 'kernel module' major no. sys interface.
- Fix potential NULL pointer usage in REQUEST SENSE
- VPD page 0x83 NAA field fix
- VPD page length fix (only 0x50 bytes in size not 0x52)
- Hopefully removed last reference to /proc
- Use setuidgid if availble instead of 'su $USER -c <vtltape|vtllibrary>'
- Add kernel module RPM spec file for RedHat
- Add Gentoo build

* Wed Sep 01 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.10
- Correct incorrect usage of & vs &&
- Fix TapeAlert.
  Error where the flags were not being set due to an earlier change.
- Add extra verbage around positioning information. Trying to track down
  a problem with HP Dataprotector when it spaces back a block.
- Make tape media & drive type loading logs more readable.
- New utility 'tapeexerciser' which I've been using to track down the
  Dataprotector issue. A simple & basic 'st ioctl()' test utility.
- Fix 'is vtl running' logic in rc script. Was broken if USER == root

* Wed Jul 09 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.9
- Fix WORM media support - Bug report from Albert Pauw
- Complete LTO5 media support

* Wed Jun 23 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.8
- Several Security Protocol IN updates - thanks Albert Pauw
  * Return certificate data
  * Correct length for 'KEY FORMATS'
  * Correct length for SPIN SUPPORTED PAGES
- Fix kernel compile on RedHat AS4
- Media/drive matching now 'dynamic' and defined in device.conf
- Added man page for device.conf
- Fix media corruption when media is 'formatted'
- Add LTO5 & SDLT-S4 drive/media types
- Handle INQUIRY correctly after media change (return SAM_STAT_GOOD)
- Updated rc script so all devices created on Target & LUN. i.e. Don't use
  channel. Some application software has trouble if only the channel is unique.

* Sat May 08 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.7
- Allow media sizes larger than 2G on 32bit platforms
- Implement STK vendor unique op code 'LOAD DISPLAY' -> logs via syslog.
- Fix core dump on invalid data in NAA strings.
- Support VENDOR ID for SMC device with embedded spaces

* Thu May 02 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.6
- Support VENDOR ID with embedded spaces
- Fix 'vtlcmd list map'
- Fix import of media via MAP (off-by-one)
- Return TapeCapacity LOG SENSE in bytes/KB/MB depending on drive type
- Honour MAP status (return error if MAP is open and robot attempts to
  move media in/out of MAP)
- General cleanup of kernel module (thanks to Herbert Stadler)
- Relax dependencies on /proc in faviour of /sys

* Thu Apr 01 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.5
- Silence warning regarding local_irq_save() - Thanks to Norm Lunda
- Re-work param parsing used by vtlcmd - Thanks to Herbert Stadler
- Fix homepage URL

* Fri Mar 05 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.4
- Fix syntax in rc script. Reported by Nabil
  That's what I get for rushing a fix out (ELEMENT STATUS) without testing
  everything..

* Thu Mar 04 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.3
- Test media mounted before REWIND (TSM seems to ignore previous TUR)
- Make creation of media home dir more robust
- Add queue depth callback - Defaults to 32.
- Conversion script of old config files to new format
- Fix problem with size of ELEMENT STATUS DATA length. Thanks to Norm Lunde.

* Thu Jan 28 2010 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.2
- Add support for multiple libraries on single host
- pack MAM struct so it's 1024 bytes on both 32 & 64bit hosts
- Updated URL after google moved it

* Wed Dec 16 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.11
- Add tests for media/drive type. i.e. Only allow LTO media in LTO drives.
- New defination for 'Compression:' in device.conf (Thanks Kevan Rehm)
  ' Compression: factor [1-9] enabled [0|1]'
        Where factor : 1 Fastest compression -> 9 Best compression
             enabled : 0 => Compression disabled, 1 => Compression enabled

* Tue Dec 15 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.1
- Fix data silent data corruption.
- Add tests for media/drive type. i.e. Only allow LTO media in LTO drives.
- Increased max number of LUNs from 7 to 32
- Changed ' Compression: factor X enabled Y' to same as 0.16 branch.
  ' Compression: factor [1-9] enabled [0|1]'
        Where factor : 1 Fastest compression -> 9 Best compression
             enabled : 0 => Compression disabled, 1 => Compression enabled

* Tue Dec 01 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.18.0
- Kevan Rehm reworked media format. The 'old' format suffered from performance
  problems. The larger the defined tape capacity, the longer it took to
  seek/position due to the sequential walk of header structures.

  The new tape format consists of three files.
   .data - Data file.
   .indx - Arrary of one header structure per written tape block or filemark.
   .meta - MAM, followed by meta header structure, followed by variable length
           of filemark block numbers
   Each Physical Cartridge Label (PCL) is located under its own directory
   MHVTL_HOME_PATH/<PCL>/

* Sun Nov 29 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.9
- Check string length in device.conf and abort if too long.
- Compression now working.
  Set up via MODE SELECT op code.
  Set default compression in device.conf 'Compression: X'
   Where 0 is off, 9 is max.
- Defaults with SPECTRA/PYTHON library
- Fix kernel module compile on 2.6.31+ (Ubuntu 9.10)
- Fix kernel silent data corruption
- Set kernel ENABLE_CLUSTERING to enable > 512k blocks on x86_64
- SPIN/SPOUT: Return correct list of supported pages.

* Tue Nov 10 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.8
- Reworked READ ELEMENT STATUS (Thanks to Kevan Rehm)
- Fix EOD header size.
- Makefile rework.
  Honour PREFIX & DESTDIR.
  User/group name defined.
  Home paths for data files & config files defined.
  Add compression support (disabled by default).

* Thu Oct 9 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.7
  Fix REPORT ELMEMENT STATUS for All elements. TSM was core dumping.
  Reported and fixed by Bernardo Clavijo.
  Re-worked Media Access Port.
   Now requires 'vtlcmd library open map' before media can be removed and
   'vtlcmd library close map' for the Medium Transport Element to place
   media into the MAP.

* Thu Oct 1 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.6
  Fixed output of 'dump_tape' utility

* Wed Sep 16 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.5
  Fixed verbosity test in MHVTL_DBG macro (again)

* Tue Sep 15 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.4
  More logging cleanups
  Fixed verbosity test in MHVTL_DBG macro

* Wed Sep 02 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.3
  Reworked logging using a macros MHVTL_DBG.
  Increased max block size to kernel max (from 256k)

* Sat Aug 15 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.2
  Changed/updated load MAP() functionality.
  Previous implementation re-read config file and parsed the MAP slots.
  This is 'interactive' using the vtlcmd command.
   e.g. vtlcmd library load map BARCODE
  Corrected NAA field in VPD page 0x83. This was a hard coded string.
   Now reads entry from /etc/mhvtl/device.conf
	' NAA: 11:22:33:44:ab:cd:ef:03' (8 octet value)
  Remove dependency on sg3_utils

* Wed Aug 05 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.1
  Fixed kernel module oops on lu removal - Many thanks to Jean-Francois
  Added loadMap() to vtllibrary.

* Tue Jul 09 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.16.0
- Moved INQUIRY into userspace.
  Re-jigged all helper scripts.
  Still need to do dynamic config of : vpd pages & mode pages.
- Added pseudo encryption support (SPIN/SPOUT op codes)
- kernel module will oops if unloaded and re-loaded..

* Fri Jan 02 2009 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.10
- Removed kfifo from data path for SCSI OP codes which originate at the target
- Add simple SCSI Persistent Reserve
- Major change to kernel module. Replaced queued_command_arr[] with linked list

* Thu Nov 27 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.9
- Re-fixed WRITE ATTRIBUTE bug forcing a rewind of media.
- Fixed build for PPC64 platform
- Add special reserved barcode 'NOBAR' to indicate a slot is full but
  contains no barcode.

* Fri Nov 21 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.8
- Added initial SECURITY PROTOCOL code

* Tue Nov 19 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.7
- Merge READ ATTRIBUTES fixes from Raymond Gilson

* Sun Nov 16 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.6
- Fixed bug where WRITE ATTRIBUTE was causing media to rewind.
- Increase default buffer size of SMC from 512k to 1024k - Ability to handle
  more (twice the) slots

* Fri Nov 14 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.5
- sg structure changed between 2.6.23 and 2.6.24 causing the kernel module
  to no longer build on latest kernel.

* Fri Apr 04 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.4
- Kernel module change. Default type is SDLT600 instead of IBM TD3 as there is
  confusion on the windows side of things regarding IBM Drivers vs IBM for
  Tivoli vs Symantec Tape Drivers.
  Maybe the QUANTUM SDLT600 will behave better ??
  Only time will tell...

* Fri Mar 28 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.3
- Return 'block descriptor data' on a MODE SENSE 'page 0' instead of an error.

* Mon Mar 10 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.2
  Re-org of the source code.
  - Placed user-space code in directory ./usr
  - Moved kernel drivers from ./kernel-driver/linux-2.6 to ./kernel
  Yet another 'tunable' option. Set the firmware release to "string" by
  # echo "5400" > /sys/bus/pseudo/drivers/vtl/firmware

* Thu Mar 06 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.15.1
  Ability to define default media size in /etc/vtl/vtl.conf

* Wed Mar 05 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Name change as 'vtl' is was deemed too generic.
  Renamed to 'mhvtl' as this is being used by Symantec's Roseville office and
  is as good a name as any.
- With the new name comes a new version 0.15.0

* Tue Feb 19 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.14.1
  Cleaned up compile time warnings on x86_64 platform.
  Added sg_utils and zlib as RPM 'requires' packages.

* Thu Feb 14 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.14.0
- With the ability to define device serial numbers, I thought it was time
  to increase vers from 0.12 to 0.14
- Cleaned up helper scripts.

* Fri Feb 08 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12.37
- Added ability to set serial number via new utility 'vtl_set_sn -q X'
  The serial number is read from /etc/vtl/library_config for each 'Drive X:'
  e.g.
   Drive 2: SN20034
   Drive 3: SN20035
  If there is no serial number defined in library_config file, and the
  serial prefix has been set, then this will be used. Otherwise the old &
  trusted method of calculating based on HBA#, ID# & LUN.

* Wed Feb 06 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12.36
- Added another config file /etc/vtl/vtl.conf
- Added ability to set a serial number prefix for devices.
- Added ability to set the buffer size used by SSC devices.
- Added ability to set/clear logging levels within vtl.conf

* Sat Feb 02 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-35
- Fix post uninstall
  check for group & passwd entries before attempting to run groupdel/userdel

* Sat Jan 08 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-34
  Changes to kernel module & rc scripts.
- Default kernel module load reporting the library only.
- The rc scripts now update the number of required tape devices depending on
  the contents of /etc/vtl/library_contents
- Using the max_luns or num_tgts the library can consist of different drives
  or all the same drive type.
- Deleted x86_64 patch as it is no longer needed.

* Fri Jan 04 2008 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Reserved vers 0.12-33
  A special build with only 5 IBM drives.

* Wed Dec 19 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-32
- Changed user 'vtl' home directory to /opt/vtl
  Otherwise there can be problems starting the vtl s/w if /home is an
  automount and can't mount /home.
- Changed kernel module Makefile
  To compile on Debian or Ubuntu systems "make ubuntu=1"
  To compile on SuSE or RedHat systems "make"

* Tue Oct 16 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-31
- No code changes. As sysdup has crashed and management have decided not to
  replaced the two failed drives in the RAID 5 system, I've changed the
  home of this project to my google homepage.

* Tue Oct 16 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-30
- vtl kernel module: - bumped to 0.12.14 20071015-0
- Another bug fix in the kernel module. This time copying data from user-space
  in an unsafe manner. Last reason for kernel oops ??
- Make library module startup more robust by clearing out message Q at start
  time.
- Set vtl startup to 'on' at package install time.

* Wed Oct 10 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-28
- vtl kernel module: - bumped to 0.12.14 20071010-0
- Many updates to error handling condition.

* Wed Sep 26 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-26
- vtl kernel module: - bumped to 0.12.14 20070926-0
  Moved memory alloc from devInfoReg() to vtl_slave_alloc() - I now don't get
  those horrible "Debug: sleeping function called from invalid context"

* Tue Sep 25 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-25
- Resolved an issue where virtual media was being corrupted when performing
  erase operation.

* Sat Sep 22 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-24
- On corrupt media load, return NOT READY/MEDIUM FORMAT CORRUPT

* Fri Sep 21 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-23
- vtl kernel module bug fix - resolved a race condition with my usage of
  copy_to_user()/copy_from_user() and c_ioctl() routines.
  Thanks to Ray Schafer for finding and being able to reproduce race.

* Fri Aug 24 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-22
- Set correct directory ownership and permissions at post install time
  for /opt/vtl

* Wed Aug 01 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-21
- Corrected warnings identified by sparse

* Sat Apr 07 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-20
- Calls to tune kernel behaviour of out-of-memory always return 'success'.
  Found out the hard way, earlier kernel versions do not support this feature.
- Added check for return status from build_library_config in rc script

* Sat Mar 31 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-19
- Added conditional x86_64/amd64 to vtl.spec so it builds correctly on x86_64
  platforms.

* Wed Mar 28 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-18
- Improved (slightly) checking of MAM header on media open.
  At least made it 32/64 bit friendly.

* Thu Mar 24 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-17
- Added 'Out Of Memory killer tuning to both vtltape and vtllibrary.
- Added 'tags' as a target in Makefile, i.e. 'make tags'
  TAGS will be removed with a 'make distclean'

* Thu Mar 13 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-16
- Added -D_LARGEFILE64 switch to Makefile to allow a more portable way of
  opening files > 2G. There should be no need for the x86_64 patch any more.
  Needs testing.

* Thu Feb 22 2007 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-14
- Added 'ERASE(6)' command as a result of bug report from Laurent Dongradi.
  NetBackup "bplabel -erase -l " command failing.

* Thu Sep 07 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-13
- Just updated some time/date in kernel module. Nothing major.

* Tue Sep 05 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-12
  Shared library (libvxscsi.so) conflict with Symantec VRTSvxvm-common-4.1.20
  so I've renamed mine to libvtlscsi.so
  Should build correctly on an x86_64 RPM system now.

* Thu Aug 31 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-10 (skipped numbering between -5 & -10
  Changed interface between user-space and kernel, hence need kernel module
  version 0.12.10
  The change is to support 'auto sense', where the sense buffer is sent straight
  after the data (if sense data is valid).
  Need to fix: Way of specifying size of sense buffer. Currently defined in
  kernel src (vtl.c) and user-space header vx.h. It would be nice to have this
  defined in one place only.
- Updated rc script to check kernel version before starting user-space daemons.

* Wed Jul 05 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-5
- Updated man pages to reflect name changes from vxtape/vxlibrary to
  vtltape/vtllibrary
- Removed any vxtape/vxlibrary binaries from build process

* Tue Jul 04 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-4
- Fixed (Well tested) kernel makefile compile on SLES 9 and suse 9.3
  i.e. Kernel versions 2.6.5-7.191-smp & 2.6.11.4-21.12-smp
  Hacked scsi.h include file and added #if KERNEL_VERSION conditional compile
  around kfifo.[ch] if below 2.6.10
- Attempt to improve install/startup on RedHat AS4 + SLES9

* Sun Jul 02 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.12-0
- Forked this version from main tree. Main branch is 0.13.x which will continue
  to be work-in-progress for removal of kfifo routines.
- 0.12-x is to be current 'stable' branch.

* Fri May 19 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.10-13
- Added TapeUsage & TapeCapacity log parameters. Even thou I'm specifying these
  pages are not supported, BackupExec still probes for them and barfs on the
  scsi error returned.

* Thu May 18 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.10-12
- Re-worked the READ ELEMENT STATUS command with the idea of adding the extra
  options which appear to be required by BackupExec.

* Wed May 10 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped vers to 0.10-10
- Fixed bug introduced in vtllibrary where I broke the inventory function.

* Tue May 09 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Changed poll of 'getting SCSI command' to use ioctl instead of kfifo.
  Requires kernel module dated > 20060503-0

* Sun Apr 30 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Fixed typo in rc script where trying to set permissions on /dev/vx? instead
  of /dev/vtl?

* Sat Apr 29 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Changed logic on WIRTE-FILEMARK SCSI command. Now only attempts to write
  filemarks if greater the 0 filemarks specified.
- Added check for SuSE-release and use '{user|group}add --system' switch
  otherwise {user|group}add without the --system switch.
- Bumped version to 0.10-6

* Thu Apr 27 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Seek to EndOfData bug where the tape daemon would loop over the last block
  and never return.

* Sat Apr  5 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Changed the kernel module from 'vx_tape' to vtl (no real impact to user space
- daemons) however changing /dev/ entries from /dev/vx? to /dev/vtl due to name
- space clash with VERITAS StorageFoundation (VxVM/VxFS)

* Sat Apr  1 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Bumped version to 0.9 as this has the start of a working Solaris port.

* Thu Mar 24 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Added extra logging for mode_sense command if verbose > 2

* Thu Mar 10 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Start of Solaris kernel port.
- Moved kernel driver into seperate subdir.
- Added some 'ifdef Solaris' to source code.

* Thu Feb 22 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Added check to make sure RPM_BUILD_ROOT is not / when attempting to remove.
- Shutdown daemons before package removal

* Thu Feb 16 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Added ALLOW/DENY MEDIUM REMOVAL SCSI cmd to vxlibrary daemon.
- Added Extend/Retract checking to MOVE MEDIUM SCSI cmds.

* Thu Feb 14 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Made RPM create system account of 'vtl' & group of 'vtl' before install.

* Thu Feb 11 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- bump vers from 0.7 to 0.8
- Rename /opt/vx_media to /opt/vtl
- Rename /etc/vxlibrary to /etc/vtl
- RPM install now creates vtl user & group
- rc script now installs a default library config file in /etc/vtl/

* Thu Feb  2 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Teach me for not testing fully. Resolved bug where no data was written.

* Thu Feb  2 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Improvements to handling of cleaning media.

* Wed Jan  3 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Added a new man page vtl, which aims to document how this package hangs
  together.
- Corrected a couple of hard-coded paths in rc scripts

* Wed Jan  3 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Moved source man pages into separate man directory.
- Updated version of user-mode utilities to that of the kernel module (v0.7)

* Tue Jan  3 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Added man pages.

* Sun Jan  1 2006 Mark Harvey <markh794@gmail.com> <mark_harvey@symantec.com>
- Initial spec file created.
- $Id: vtl.spec,v 1.29.2.7 2006-08-30 06:35:01 markh Exp $
