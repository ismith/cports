pkgname = "xz"
version = "5.2.5"
revision = 1
bootstrap = True
build_style = "gnu_configure"
short_desc = "The XZ compression utilities"
maintainer = "Enno Boland <gottox@voidlinux.org>"
license = "Public domain, GPL-2.0-or-later, GPL-3.0-or-later, LGPL-2.1-or-later"
homepage = "https://tukaani.org/xz"
distfiles = [f"https://tukaani.org/xz/xz-{version}.tar.bz2"]
checksum = ["5117f930900b341493827d63aa910ff5e011e0b994197c3b71c08a20228a42df"]

def post_install(self):
    import shutil
    shutil.rmtree(self.destdir / "usr/share/doc")

@subpackage("liblzma")
def _lib(self):
    self.short_desc = "XZ-format compression library"

    def install():
        self.take("usr/lib/*.so.*")

    return install

@subpackage("liblzma-devel")
def _devel(self):
    self.short_desc = "XZ-format compression library - development files"
    self.depends = [f"liblzma>={version}_{revision}"]

    def install():
        self.take("usr/include")
        self.take("usr/lib/*.a")
        self.take("usr/lib/*.so")
        self.take("usr/lib/pkgconfig")

    return install