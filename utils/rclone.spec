# Set with_systemd on distros that use it, so we can install the service
# file, otherwise the sysvinit script will be installed
%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1210
%global with_systemd 1
BuildRequires: systemd-units

# Disable some systemd safety features on OSes without a new enough systemd
# (new enough is systemd >= 233)
%if 0%{?fedora} < 26 || 0%{?rhel} > 0
%global safer_systemd 0
%else
%global safer_systemd 1
%endif

%else
%global with_systemd 0
%endif

Name:           rclone
Version:        1.58
Release:        2%{?dist}
Summary:        rclone: Remote FUSE filesystem for cloud storage

Group:          System Environment/Daemons
License:        MIT
URL:            https://rclone.org
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{with_systemd}
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
%endif
Requires:  fuse

%description
"rsync for cloud storage" - Google Drive, S3, Dropbox, Backblaze B2, 
                            One Drive, Swift, Hubic, Wasabi, 
                            Google Cloud Storage, Yandex Files

%prep
%setup -q -n %{name}-%{version}

%build
# skip

%install
mkdir -p %{buildroot}/etc/rclone
mkdir -p %{buildroot}/var/log/rclone
mkdir -p %{buildroot}/mnt/gcs_mount

install -Dp -m0755 bin/rclone %{buildroot}%{_bindir}/rclone
install -Dp -m0755 bin/aesutils %{buildroot}%{_bindir}/aesutils
install -Dp -m0755 bin/uniqsign %{buildroot}%{_bindir}/uniqsign
install -Dp -m0644 etc/rclone.conf %{buildroot}%{_sysconfdir}/rclone/%{name}.conf
install -Dp -m0644 systemd/rclone@.service %{buildroot}%{_unitdir}/%{name}@.service

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%post
if [ $1 -eq 1 ]; then
    # Initial install
%if %{with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    /sbin/chkconfig --add %{name}
%endif
fi

cat <<BANNER
----------------------------------------------------------------------
Thanks for using rclone!

installed in:

  /etc/rclone/rclone.conf            # config option
  /mnt/gcs_mount                     # mount dir for all bucket
  /var/log/rclone/                   # rclone log dir
  systemctl enable rclone@bucketname # enable rclone mount
  systemctl start rclone@bucketname  # start rclone mount

    -- contact administrator to get service_consul_key and bucket name

----------------------------------------------------------------------
BANNER

%postun
%if %{with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

%files
%defattr(-,root,root,-)
%dir %attr(750,root,root) /mnt/gcs_mount
%dir %attr(750,root,root) /var/log/rclone
%dir %attr(750,root,root) /etc/rclone

%{_bindir}/%{name}
%{_bindir}/aesutils
%{_bindir}/uniqsign
%{_sysconfdir}/rclone/%{name}.conf

%if %{with_systemd}
%{_unitdir}/%{name}@.service
%else
%{_initrddir}/%{name}
%endif

%changelog
* Tue Apr 19 2022 arstercz<arstercz@qq.com> - 1.58-2
- Add consul support for gcs
- Add aesutils for encrypt file
