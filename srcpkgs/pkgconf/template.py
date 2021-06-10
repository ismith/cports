pkgname = "pkgconf"
version = "1.7.3"
revision = 1
bootstrap = True
build_style = "gnu_configure"
configure_args = ["--disable-shared", "--disable-static"]
checkdepends = ["kyua"]
short_desc = "Provides compiler and linker configuration"
maintainer = "Enno Boland <gottox@voidlinux.org>"
license = "MIT"
homepage = "http://pkgconf.org/"
changelog = "https://raw.githubusercontent.com/pkgconf/pkgconf/master/NEWS"
distfiles = [f"https://distfiles.dereferenced.org/pkgconf/pkgconf-{version}.tar.xz"]
checksum = ["b846aea51cf696c3392a0ae58bef93e2e72f8e7073ca6ad1ed8b01c85871f9c0"]

alternatives = [
    ("pkg-config", "pkg-config", "/usr/bin/pkgconf"),
    ("pkg-config", "pkg-config.1", "/usr/share/man/man1/pkgconf.1"),
    ("pkg-config", "pkg.m4", "/usr/share/aclocal/pkg.m4.pkgconf")
]

def post_install(self):
    self.install_license("COPYING")

    import shutil

    shutil.rmtree(self.destdir / "usr/include")
    shutil.move(
        self.destdir / "usr/share/aclocal/pkg.m4",
        self.destdir / "usr/share/aclocal/pkg.m4.pkgconf"
    )