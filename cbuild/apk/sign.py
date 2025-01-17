from cbuild.core import logger, paths

import io
import re
import gzip
import time
import getpass
import pathlib
import tarfile
import subprocess

from . import util

def _get_keypath(keypath):
    keypath = pathlib.Path(keypath)

    if keypath.is_absolute():
        return keypath

    if keypath.parent == pathlib.Path():
        # just a filename
        return paths.distdir() / "etc" / "keys" / keypath
    else:
        # otherwise a path relative to distdir
        return paths.distdir() / keypath

# returns the compressed signature data given
# either an input file path or raw input bytes
def sign(keypath, data, epoch):
    if isinstance(data, bytes):
        inparg = []
        inpval = data
    else:
        inparg = [data]
        inpval = None

    keypath = _get_keypath(keypath)

    if not keypath.is_file():
        logger.get().out_red(f"Non-existent private key '{keypath}'")
        raise Exception()

    keyname = keypath.name + ".pub"
    signame = ".SIGN.RSA." + keyname

    sout = subprocess.run([
        "openssl", "dgst", "-sha1", "-sign", keypath, "-out", "-"
    ] + inparg, input = inpval, capture_output = True)

    if sout.returncode != 0:
        logger.get().out_red("Signing failed!")
        logger.get().out_plain(sout.stderr.strip().decode())
        raise Exception()

    sigio = io.BytesIO()
    rawdata = sout.stdout

    with tarfile.open(None, "w", fileobj = sigio) as sigtar:
        tinfo = tarfile.TarInfo(signame)
        tinfo.size = len(rawdata)
        tinfo.mtime = int(epoch)
        tinfo.uname = "root"
        tinfo.gname = "root"
        tinfo.uid = 0
        tinfo.gid = 0
        with io.BytesIO(rawdata) as sigstream:
            sigtar.addfile(tinfo, sigstream)

    cval = gzip.compress(
        util.strip_tar_endhdr(sigio.getvalue()), mtime = int(epoch)
    )

    sigio.close()
    return cval

def keygen(keypath, size, cfgfile, cfgpath):
    pass

    if not keypath:
        # does not have to succeed, e.g. there may not even be git at all
        eaddr = subprocess.run(
            ["git", "config", "--get", "user.email"], capture_output = True
        )
        if eaddr.returncode == 0:
            eaddr = eaddr.stdout.strip().decode()
            if len(eaddr) == 0:
                eaddr = None
        else:
            eaddr = None
        if not eaddr:
            keyn = getpass.getuser()
        else:
            keyn = eaddr
        keypath = keyn + "-" + hex(int(time.time()))[2:] + ".rsa"
        logger.get().warn(f"No key path provided, using '{keypath}'")

    keypath = _get_keypath(keypath)

    keypath.parent.mkdir(parents = True, exist_ok = True)

    if keypath.is_file():
        logger.get().out_red("Attempt to overwrite an existing key, aborting")
        raise Exception()

    kout = subprocess.run([
        "openssl", "genrsa", "-out", keypath, str(size)
    ], umask = 0o007)

    if not kout.returncode == 0:
        logger.get().out_red("Key generation failed")
        raise Exception()

    pout = subprocess.run([
        "openssl", "rsa", "-in", keypath,
        "-pubout", "-out", str(keypath) + ".pub"
    ])

    if not pout.returncode == 0:
        logger.get().out_red("Public key generation failed")
        raise Exception()

    logger.get().out("Key successfully generated.")

    if "signing" in cfgfile and "key" in cfgfile["signing"]:
        if cfgfile["signing"]["key"] != cfgpath:
            logger.get().out("Signing key set in config, but not the same.")
            logger.get().out("You will probably need to update it.")
        else:
            logger.get().out("The key was already found in the config file.")
        return

    logger.get().out("Updating configuration file...")

    rkpath = keypath
    if rkpath.is_relative_to(paths.distdir() / "etc" / "keys"):
        rkpath = rkpath.relative_to(paths.distdir() / "etc" / "keys")
    elif rkpath.is_relative_to(paths.distdir()):
        rkpath = rkpath.relative_to(paths.distdir())

    if "signing" in cfgfile:
        with open(cfgpath, "r") as cf:
            with open(cfgpath + ".new", "w") as ocf:
                for l in cf:
                    ocf.write(l)
                    if re.match(r"^\[signing\]", l):
                        ocf.write(f"key = {rkpath}\n")

        pathlib.Path(cfgpath + ".new").rename(cfgpath)
    else:
        with open(cfgpath, "a") as cf:
            cf.write("\n[signing]\n")
            cf.write(f"key = {rkpath}\n")

    if not pout.returncode == 0:
        logger.get().out_red("Public key generation failed")
        raise Exception()

    logger.get().out("Configuration file updated.")
