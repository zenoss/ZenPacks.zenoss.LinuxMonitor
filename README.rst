
Linux Monitor Zenpack
=====================

This ZenPack monitors the Linux Operating System.

Releases
--------

.. _Version-2.1.1: http://wiki.zenoss.org/download/zenpacks/ZenPacks.zenoss.LinuxMonitor/2.1.1/ZenPacks.zenoss.LinuxMonitor-2.1.1.egg

Version-2.1.1_ : Released on 2016/12/21

   Compatible with Zenoss Core 4.2.x, Zenoss Core 5.0.x, Zenoss Core 5.1.x,
   Zenoss Resource Manager 4.2.x, Zenoss Resource Manager 5.0.x, Zenoss
   Resource Manager 5.1.x, Zenoss Resource Manager 5.x.x

.. _Version-2.0.6: http://wiki.zenoss.org/download/zenpacks/ZenPacks.zenoss.LinuxMonitor/2.0.6/ZenPacks.zenoss.LinuxMonitor-2.0.6.egg

Version-2.0.6_ : Released on 2016/11/01

   Compatible with Zenoss Core 4.2.x, Zenoss Core 5.0.x, Zenoss Core 5.1.x,
   Zenoss Resource Manager 4.2.x, Zenoss Resource Manager 5.0.x, Zenoss
   Resource Manager 5.1.x

.. contents::
   :depth: 2

Background
----------

This ZenPack provided monitoring support for Linux, leveraging OpenSSH
for data access. In addition to system health, disks, LVM, services, and
processes are monitored.

Features
--------

-  Monitors multiple Linux flavors and versions
-  OpenStack LVM volume integration
-  Monitors LVM Physical Volumes, Volume Groups, and Logical Volumes
-  Block Device monitoring
-  Service Monitoring via Sysvinit, Systemd, Upstart
-  Root Cause Analysis with Impact Support
-  Dynamic View support

.. Note::
   This version of LinuxMonitor fully replaces EnterpriseLinux. To avoid
   related errors in zenhub logs, EnterpriseLinux ZP should be removed.

Discovery
~~~~~~~~~

The following entities will be automatically discovered. The attributes
and collections will be updated on Zenoss normal remodeling interval
which defaults to every 12 hours.

Hard Disks
    Attributes: Name, Size, LVM PV

.. Note::
   * On CentOS5, RHEL5 (and possibly others), the **lsblk** command is not
     available, in which case this component will be missing.

   * To ignore unmounted drives, set the *zIgnoreUnmounted* configuration
     property to True.

Processors
    Attributes: Socket, Manufacturer, Model, Speed, Ext Speed, L1, L2,
    Voltage

IP Services
    Attributes: Name, Protocol, Port, IPs, Description

File Systems
    Attributes: Mount Point, Storage Device, Total Bytes, Used Bytes,
    Free Bytes, % Util

Interfaces
    Attributes: IP Interface, IP Addresses, Description, MAC Address,
    Operational Status, Admin Status

Network Routes
    Attributes: Destination, Next Hop, Interface, Protocol, Type

Snapshot Volumes
    Attributes: Name, Volume Group, Logical Volume, Size, Block Device,
    File System, Active
    Relations: Logical Volumes

Physical Volumes
    Attributes: Name, Format, Size, Free, % Util, Block Device, Volume
    Group
    Relations: Volume Groups

Volume Groups
    Attributes: Name, Size, Free, % Util, Snapshot Volumes, Logical
    Volumes, Physical Volumes

Logical Volumes
    Attributes: Name, Volume Group, Size, Block Device, File System,
    Active, Snapshot Volumes
    Relations: Volume Groups

OS Processes
    Attributes: Process Class, Process Set, Restart Alert?, Fail
    Severity

OS Services
    Attributes: Name, Loaded Status, Active Status, Main PID, Processes,
    Description

.. Note::
   On some Linux flavors some fields (Loaded Status, Processes,
   Description) could be empty.

Set Linux Server Monitoring Credentials
---------------------------------------

All Linux servers must have a device entry in an organizer below the
``/Devices/Server/SSH/Linux`` device class.

.. Tip::
   The SSH monitoring feature will attempt to use key-based authentication
   before using a configuration properties password value.

#. Select Infrastructure from the navigation bar.
#. Click the device name in the device list.
   The device overview page appears.

#. Select Configuration Properties from the left panel.
#. Verify the credentials for the service account.
   The zCommandUsername property must be set. To use public key
   authentication you must verify that the public portion of the key
   referenced in zKeyPath is installed in the
   ``~/.ssh/authorized\_keys`` file for the appropriate user on the
   linux server. If this key has a passphrase you should set it in the
   zCommandPassword property. If you'd rather use password
   authentication than setup keys, simply put the user's password in the
   zCommandPassword property.

Using a Root User
~~~~~~~~~~~~~~~~~

This ZenPack requires the ability to run the *pvs*, *vgs*, *lvs*,
*systemctl*, *initctl* and *service* commands, remotely on your linux
server(s) using SSH. By default, these commands are only allowed to
be run locally. To remotely run these commands, the root user must
not be required to use TTY.

#. Install the **sudo** package on your server.
#. Allow root user to execute commands via ssh without a TTY.

   #. Edit the /etc/sudoers file.
   #. Find the line containing *root ALL=(ALL) ALL*.
   #. Add this line underneath it:

          Defaults:root !requiretty

   #. Save the changes and exit.

Using a Non-Root User
~~~~~~~~~~~~~~~~~~~~~

This ZenPack requires the ability to run the *pvs*, *vgs*, *lvs*,
*systemctl*, *initctl* and *service* commands, remotely on your linux
server(s) using SSH. By default, most of these commands are only
allowed to be run by the **root** user. The output of *systemctl*,
*initctl* and *service* commands depends on whether they are executed
via **sudo**. Furthermore, this ZenPack expects these commands be in
the user's path. Normally this is only true for the root user.

Assuming that you've created a user named **zenmonitor** on your
linux servers for monitoring purposes, you can follow these steps to
allow the **zenmonitor** user to run the commands.

#. Install the **sudo** package on your server
#. Allow the **zenmonitor** user to run the commands via ssh without a TTY

   - Edit /etc/sudoers.d/zenoss (Or /etc/sudoers if sudoers.d not
      supported) and add the following lines to the bottom of the file::

         Defaults:zenmonitor !requiretty
         Cmnd_Alias ZENOSS_LVM_CMDS = /sbin/pvs, /sbin/vgs, /sbin/lvs, \
             /usr/sbin/pvs, /usr/sbin/vgs, /usr/sbin/lvs
         Cmnd_Alias ZENOSS_SVC_CMDS = /bin/systemctl list-units *, \
             /bin/systemctl status *, /sbin/initctl list, /sbin/service --status-all, \
             /usr/sbin/dmidecode
         zenmonitor ALL=(ALL) NOPASSWD: ZENOSS_LVM_CMDS, ZENOSS_SVC_CMDS

   - Save, ensuring all paths for these commands are correct

.. Note::
   In order for Ssh operation works correctly, ensure OpenSSH is updated
   to your distro's current version. This is especially true for older
   versions of RHEL, CentOS, Ubuntu, and Suse Linux.


.. Note::
   For Suse Linux the paths for (**pvs, vgs, lvs**) are located at
   **/sbin/pvs**, **/sbin/vgs**, and **/sbin/lvs** respectively. Please
   ensure that each command can be manually executed remotely.

+--------------------------------------+--------------------------------------+
| Name                                 | Description                          |
+======================================+======================================+
| zCommandUsername                     | Linux user with privileges to gather |
|                                      | performance information.             |
+--------------------------------------+--------------------------------------+
| zCommandPassword                     | Password for the Linux user.         |
+--------------------------------------+--------------------------------------+

Table: Linux Configuration Properties

.. Note::
   zSshConcurrentSessions property by default equals to 5. In case of
   increasing this value user has change sshd daemon configuration on
   target device by increasing allowed session number and restart sshd
   daemon.

Add a Linux Server
------------------

The following procedure assumes that credentials have been set.

#. Select Infrastructure from the navigation bar.
#. Select Add a Single Device from the Add Device list of options.
   The Add a Single Device dialog appears.

#. Enter the following information in the dialog:

   +-----------------------------------+--------------------------------------+
   | Name                              | Description                          |
   +===================================+======================================+
   | Name or IP                        | Linux host to model.                 |
   +-----------------------------------+--------------------------------------+
   | Device Class                      | /Server/SSH/Linux                    |
   +-----------------------------------+--------------------------------------+
   | Model Device                      | Select this option unless adding a   |
   |                                   | device with a user name and password |
   |                                   | different than found in the device   |
   |                                   | class. If you do not select this     |
   |                                   | option, then you must add the        |
   |                                   | credentials (see) and then manually  |
   |                                   | model the device.                    |
   +-----------------------------------+--------------------------------------+

   Table: Adding Linux Device Details

#. Click **Add**.

Alternatively you can use zenbatchload to add Linux servers from the
command line. To do this, you must create a text file with hostname,
username and password of all the servers you want to add. Multiple
endpoints can be added under the same /Devices/Server/Linux section.
Here is an example...

.. code:: text

    /Devices/Server/Linux
    LinuxDevice zCommandUsername="user", zCommandPassword="password"

You can then load the Linux servers into Zenoss Core or Resource Manager
as devices with the following command.

.. code:: bash

    zenbatchload <filename>

Installed Items
---------------

Installing this ZenPack will add the following items to your Zenoss
system.

Device Classes

-  /Server/SSH/Linux

Modeler Plugins

-  zenoss.cmd.uname
-  zenoss.cmd.linux.df
-  zenoss.cmd.linux.alt\_kernel\_name
-  zenoss.cmd.linux.cpuinfo
-  zenoss.cmd.linux.interfaces
-  zenoss.cmd.linux.lvm
-  zenoss.cmd.linux.memory
-  zenoss.cmd.linux.netstat\_an
-  zenoss.cmd.linux.netstat\_rn
-  zenoss.cmd.linux.process
-  zenoss.cmd.linux.rpm
-  zenoss.cmd.linux.sudo\_dmidecode
-  zenoss.cmd.linux.os\_release
-  zenoss.cmd.linux.os\_service

Monitoring Templates

-  Device (in /Devices/Server/SSH/Linux)
-  HardDisk (in /Devices/Server/SSH/Linux)
-  IpService (in /Devices)
-  FileSystem (in /Devices/Server/SSH/Linux)
-  ethernetCsmacd (in /Devices/Server/SSH/Linux)
-  SnapshotVolume (in /Devices/Server/SSH/Linux)
-  PhysicalVolume (in /Devices/Server/SSH/Linux)
-  VolumeGroup (in /Devices/Server/SSH/Linux)
-  LogicalVolume (in /Devices/Server/SSH/Linux)
-  OSProcess (in /Devices/Server/SSH/Linux)

Monitoring Templates
--------------------

Device (in /Devices/Server/SSH/Linux)

-  Data Points

   -  ssCpuIdlePerCpu
   -  ssCpuUserPerCpu
   -  ssCpuSystemPerCpu
   -  ssCpuWaitPerCpu
   -  sysUpTime
   -  laLoadInt15
   -  laLoadInt5
   -  laLoadInt1
   -  Buffers
   -  Cached
   -  MemFree
   -  MemTotal
   -  SwapFree
   -  SwapTotal
   -  ssIORawReceived
   -  ssIORawSent

-  Thresholds

   -  *None*

-  Graphs

   -  CPU Utilization
   -  Load Average
   -  Memory Utilization
   -  Memory Usage
   -  IO Throughput

HardDisk (in /Devices/Server/SSH/Linux)

-  Data Points

   -  readsCompleted
   -  readsMerged
   -  sectorsRead
   -  msReading
   -  writesCompleted
   -  writesMerged
   -  sectorsWritten
   -  msWriting
   -  ioInProgress
   -  msDoingIO
   -  msDoingIOWeighted

-  Thresholds

   -  *None*

-  Graphs

   -  Operation Throughtput
   -  Merge Rate
   -  Sector Throughtput
   -  IO Operation in Progress
   -  IO Utilization
   -  Weighted IO Utilization

.. Note::
   There were significant changes between 2.4 and 2.6 in the I/O subsystem. As
   a result, some statistic information disappeared. The translation from a
   disk address relative to a partition to the disk address relative to the
   host disk happens much earlier. All merges and timings now happen at the
   disk level rather than at both the disk and partition level as in 2.4. There
   are only \*four\* fields available for partitions on 2.6 machines and in
   this case few datapoints will be missed.

IpService (in /Devices)

-  Data Points

   -  *None*

-  Thresholds

   -  *None*

-  Graphs

   -  *None*

FileSystem (in /Devices/Server/SSH/Linux)

-  Data Points

   -  usedBlocks
   -  percentInodesUsed
   -  totalInodes
   -  usedInodes
   -  availableInodes

-  Thresholds

   -  90 percent used

-  Graphs

   -  Utilization
   -  Usage
   -  Inode Utilization
   -  Inode Usage

ethernetCsmacd (in /Devices/Server/SSH/Linux)

-  Data Points

   -  ifInOctets
   -  ifOutOctets
   -  ifInPackets
   -  ifOutPackets
   -  ifInErrors
   -  ifInDropped
   -  ifInOverruns
   -  ifOutErrors
   -  ifOutCarrier
   -  ifOutCollisions
   -  ifOutDropped

-  Thresholds

   -  75 percent utilization

-  Graphs

   -  Data Throughput
   -  Packet Throughput
   -  Error Rate

SnaphotVolume (in /Devices/Server/SSH/Linux)

-  Data Points

   -  state
   -  health

-  Thresholds

   -  *None*

-  Graphs

   -  *None*

PhysicalVolume (in /Devices/Server/SSH/Linux)

-  Data Points

   -  size
   -  free
   -  allocatable
   -  exported
   -  missing

-  Thresholds

   -  unallocatable
   -  exported
   -  missing

-  Graphs

   -  Utilization

VolumeGroup (in /Devices/Server/SSH/Linux)

-  Data Points

   -  size
   -  free
   -  partial

-  Thresholds

   -  partial

-  Graphs

   -  Utilization

LogicalVolume (in /Devices/Server/SSH/Linux)

-  Data Points

   -  state
   -  health

-  Thresholds

   -  *None*

-  Graphs

   -  *None*

OSProcess (in /Devices/Server/SSH/Linux)

-  Data Points

   -  count
   -  cpu
   -  mem

-  Thresholds

   -  count

-  Graphs

   -  Process Count
   -  CPU Utilization
   -  Memory Usage

Service Impact
--------------

When combined with the Zenoss Service Dynamics product, this ZenPack
adds built-in service impact capability for services running on Linux.
The following service impact relationships are automatically added.
These will be included in any services that contain one or more of the
explicitly mentioned entities.

Service Impact Relationships

-  HardDisk, IpInterface, IpService, OSProcess, CPU, OSService are
   impacted by LinuxDevice;
-  PhysicalVolume is impacted by HardDisk;
-  VolumeGroup is impacted by PhysicalVolume;
-  LogicalVolume is impacted by VolumeGroup or HardDisk;
-  SnapshotVolume is impacted by LogicalVolume or HardDisk;
-  FileSystem is impacted by SnapshotVolume or LogicalVolume or HardDisk
   or LinuxDevice

Daemons
-------

+--------------------------------------+--------------------------------------+
| Type                                 | Name                                 |
+======================================+======================================+
| Modeler                              | zenmodeler                           |
+--------------------------------------+--------------------------------------+
| Performance Collector                | zencommand                           |
+--------------------------------------+--------------------------------------+

Supported flavors
-----------------

The following flavors of Linux are supported

+--------------------+--------------------+--------------------+--------------------+
| Linux Flavor       | Version            | Released           | EOS                |
+====================+====================+====================+====================+
| Ubuntu             | 12.04 LTS          | April 2012         | April 2017         |
+--------------------+--------------------+--------------------+--------------------+
|                    | 14.04 LTS          | April 2014         | April 2019         |
+--------------------+--------------------+--------------------+--------------------+
|                    | 15.04              | April 2015         | Feb 2016           |
+--------------------+--------------------+--------------------+--------------------+
|                    | 15.10              | Oct 2015           | July 2016          |
+--------------------+--------------------+--------------------+--------------------+
| RedHat EL          | RHEL 5             | March 2007         | March 2017         |
+--------------------+--------------------+--------------------+--------------------+
|                    | RHEL 6             | Nov 2010           | Nov 2020           |
+--------------------+--------------------+--------------------+--------------------+
| CentOS             | 5                  |                    | March 2017         |
+--------------------+--------------------+--------------------+--------------------+
|                    | 6                  |                    | Nov 2020           |
+--------------------+--------------------+--------------------+--------------------+
|                    | 7                  |                    | June 2024          |
+--------------------+--------------------+--------------------+--------------------+
| SuSE LES           | SLES 11            |                    | March 2022         |
+--------------------+--------------------+--------------------+--------------------+
|                    | SLES 12            |                    | Oct 2027           |
+--------------------+--------------------+--------------------+--------------------+

Changes
-------

2.1.2

- Improve OS process detection. (ZPS-659)
- Quiet modeler error messages for missing services. (ZPS-644)

2.1.1

-  Fix "ifconfig" is checked before "ip" Linux Monitor (ZEN-25425)

2.1.0

-  Add cpu\_ssCpuUsedPerCpu and mem\_MemUsedPercent datapoints. (ZEN-22978)
-  Add common datapoint aliases. (ZEN-24619)
-  Improve ability to model network interface speeds.
-  Improve support for NFS filesystem impact. (ZEN-24478)
-  Improve NFS filesystem linking to NFS server. (ZEN-24478)
-  Disable monitor of NFS mounted filesystems by default. (ZEN-24650)
-  Prevent threshold violations on interfaces with unknown speed.
-  Fix IndexError when modeling older LVM versions. (ZEN-25792)
-  Fix setIdForRelationship error when modeling some LVM versions. (ZEN-22409)

2.0.6

-  Fix "string index out of range" error when modeling older LVM versions (ZEN-25792)

2.0.4

-  Fix "unimplemented" SSH error on 4.2.5 SP709. (ZEN-23392)

2.0.3

-  Fix migration of Linux devices to new type. (ZEN-24293)

2.0.2

-  Added property to ignore unmounted hard disks
-  Improve 1.x to 2.x migration time. (ZEN-24024)

2.0.1

-  Fix invalid event class in filesystem threshold

2.0.0

-  Added support for LVM Physical Volumes, Volume Groups, and Logical Volumes
-  Added support for OpenStack-LVM Integration
-  Added disk (block device) monitoring.
-  Added service monitoring (sysvinit, systemd, upstart).
-  Combined EnterpriseLinux and LinuxMonitor capabilities.
-  Enhanced Impact Support
-  Added Dynamic View Support
-  Completely replaces EnterpriseLinux ZenPack
-  Many other smaller improvements.

