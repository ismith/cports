from cbuild.core import template

import os

def invoke(pkg):
    crossb = pkg.cross_build if pkg.cross_build else ""
    patch_done = pkg.statedir / f"{pkg.pkgname}_{crossb}_patch_done"

    template.call_pkg_hooks(pkg, "init_patch")
    template.run_pkg_func(pkg, "init_patch")

    if patch_done.is_file():
        return

    pkg.run_step("patch", optional = True)

    patch_done.touch()
