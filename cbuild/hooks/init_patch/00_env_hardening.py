def invoke(pkg):
    pkg.LDFLAGS.insert(0, "-Wl,--as-needed")

    if not pkg.nopie:
        pkg.CFLAGS.insert(0, "-D_FORTIFY_SOURCE=2")
        pkg.CFLAGS.insert(0, "-fstack-clash-protection")

        pkg.CXXFLAGS.insert(0, "-D_FORTIFY_SOURCE=2")
        pkg.CXXFLAGS.insert(0, "-fstack-clash-protection")

        pkg.LDFLAGS.insert(0, "-Wl,-z,now")
        pkg.LDFLAGS.insert(0, "-Wl,-z,relro")
    else:
        pkg.CFLAGS.insert(0, "-fno-PIE")
        pkg.CXXFLAGS.insert(0, "-fno-PIE")
        pkg.LDFLAGS.insert(0, "-no-pie")