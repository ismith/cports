pkgname = "libcap"
version = "2.49"
revision = 0
build_style = "gnu_makefile"
hostmakedepends = ["gmake", "perl"]
make_cmd = "gmake"
make_build_args = ["GOLANG=no"]
make_install_args = [
    "PKGCONFIGDIR=/usr/lib/pkgconfig",
    "SBINDIR=/usr/bin",
    "LIBDIR=/usr/lib",
    "exec_prefix=/usr",
    "RAISE_SETFCAP=no",
]
make_use_env = True
makedepends = ["attr-devel"]
short_desc = "POSIX.1e capabilities suite"
maintainer = "q66 <q66@chimera-linux.org>"
license = "GPL-2.0-only"
homepage = "http://sites.google.com/site/fullycapable/"
distfiles = [f"$(KERNEL_SITE)/libs/security/linux-privs/libcap2/{pkgname}-{version}.tar.xz"]
checksum = ["e98bc4d93645082ec787730b0fd1a712b38882465c505777de17c338831ee181"]

def init_configure(self):
    self.make_build_args += [
        "CC=" + self.get_tool("CC"),
        "BUILD_CC=" + self.get_tool("CC", target = "host"),
    ]

@subpackage("libcap-devel")
def _devel(self):
    self.depends = [f"{pkgname}={version}-r{revision}"]
    self.short_desc = short_desc + " - development files"

    return [
        "usr/include",
        "usr/lib/libcap.a",
        "usr/lib/libpsx.a",
        "usr/lib/libcap.so",
        "usr/lib/libpsx.so",
        "usr/lib/pkgconfig",
        "usr/share/man/man3",
    ]

@subpackage("libcap-progs")
def _progs(self):
    self.short_desc = short_desc + " - utilities"

    return ["usr/bin", "usr/share"]
