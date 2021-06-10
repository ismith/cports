pkgname = "coreutils"
version = "8.32"
revision = 4
bootstrap = True
makedepends = ["gmp-devel", "acl-devel", "libcap-devel"]
short_desc = "GNU core utilities"
maintainer = "Enno Boland <gottox@voidlinux.org>"
license = "GPL-3.0-or-later"
homepage = "https://www.gnu.org/software/coreutils"
changelog = "https://git.savannah.gnu.org/gitweb/?p=coreutils.git;a=blob_plain;f=NEWS;hb=HEAD"

from cbuild import sites

distfiles = [f"{sites.gnu}/coreutils/coreutils-{version}.tar.xz"]
checksum = ["4458d8de7849df44ccab15e16b1548b285224dbba5f08fac070c1c0e0bcc4cfa"]

replaces = ["chroot-coreutils>=0", "coreutils-doc>=0", "b2sum>=0"]

if not current.bootstrapping:
    hostmakedepends = ["perl"]

alternatives = [
    ("hostname", "hostname", "/usr/bin/hostname-coreutils"),
    ("hostname", "hostname.1", "/usr/share/man/man1/hostname-coreutils.1"),
]

def init_configure(self):
    from cbuild.util import make
    self.make = make.Make(self)

def pre_configure(self):
    from cbuild import cpu

    if not self.cross_build:
        return

    self.do(self.chroot_wrksrc / "configure", [
        "--prefix=" + str(self.chroot_wrksrc / ("coreutils-" + cpu.host())),
        "--enable-install-program=arch,hostname",
        "--enable-no-install-program=kill,uptime"
    ], env = {
        "CC": "cc", "LD": "ld", "AR": "ar", "RANLIB": "ranlib",
        "CFLAGS": "-Os", "CXXFLAGS": "-Os", "LDFLAGS": ""
    })

    hmake = make.Make(self)
    hmake.build()
    hmake.invoke("install")
    hmake.invoke("distclean")

def do_configure(self):
    cargs = [
        "ac_cv_func_sysfs=no",
        "ac_cv_lib_error_at_line=no",
        "ac_cv_header_sys_cdefs_h=no"
    ]

    if self.cross_build:
        cargs += [
            "fu_cv_sys_stat_statfs2_bsize=no",
            "gl_cv_func_working_mkstemp=yes",
            "gl_cv_func_working_acl_get_file=yes",
        ]

    self.do(self.chroot_wrksrc / "configure", [
        "--prefix=/usr", "--disable-rpath",
        "--enable-install-program=arch,hostname",
        "--enable-no-install-program=kill,uptime"
    ] + cargs)

    if self.cross_build:
        import re
        import os
        with open(self.abs_wrksrc / "Makefile") as ifile:
            with open(self.abs_wrksrc / "Makefile.new", "w") as ofile:
                for ln in ifile:
                    ln = re.sub(r"^(cu_install_program =).*", r"\1 install", ln)
                    ofile.write(ln)

        os.rename(
            self.abs_wrksrc / "Makefile.new",
            self.abs_wrksrc / "Makefile"
        )

def do_build(self):
    self.make.build()

def do_install(self):
    self.make.install()

    import os
    import shutil

    os.rename(
        self.destdir / "usr/bin/hostname",
        self.destdir / "usr/bin/hostname-coreutils"
    )
    os.rename(
        self.destdir / "usr/share/man/man1/hostname.1",
        self.destdir / "usr/share/man/man1/hostname-coreutils.1"
    )

    shutil.rmtree(self.destdir / "usr/share/info")