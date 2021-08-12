from cbuild.core import logger, paths, version

from . import sign

import os
import pathlib
import subprocess

def _collect_repos(intree):
    from cbuild.core import chroot

    ret = []
    for r in chroot.get_confrepos():
        ret.append("--repository")
        if intree:
            ret.append("/binpkgs/main/" + r)
        else:
            ret.append(str(paths.repository()) + "/main/" + r)
    return ret

def call(
    subcmd, args, cwd = None, env = None, capture_output = False, root = None
):
    return subprocess.run(
        [
            "apk", subcmd, "--root", root if root else paths.masterdir(),
            "--repositories-file", "/dev/null",
        ] + _collect_repos(False) + args,
        cwd = cwd, env = env, capture_output = capture_output
    )

def call_chroot(
    subcmd, args, capture_out = False, check = False
):
    from cbuild.core import chroot

    return chroot.enter(
        "apk",
        [
            subcmd, "--repositories-file", "/dev/null"
        ] + _collect_repos(True) + args,
        capture_out = capture_out, check = check,
        pretend_uid = 0, pretend_gid = 0, mount_binpkgs = True
    )

def summarize_repo(repopath, olist, quiet = False):
    rtimes = {}
    obsolete = []

    for f in repopath.glob("*.apk"):
        fn = f.name
        pf = fn[:-4]
        rd = pf.rfind("-")
        if rd > 0:
            rd = pf.rfind("-", 0, rd)
        if rd < 0:
            if not quiet:
                logger.get().warn(f"Malformed file name found, skipping: {fn}")
            continue
        pn = pf[0:rd]
        mt = f.stat().st_mtime
        if not pn in rtimes:
            rtimes[pn] = (mt, f.name)
        else:
            omt, ofn = rtimes[pn]
            # this package is newer, so prefer it
            if mt > omt:
                fromf = ofn
                fromv = ofn[rd + 1:-4]
                tof = f.name
                tov = pf[rd + 1:]
                rtimes[pn] = (mt, f.name)
                obsolete.append(ofn)
            elif mt < omt:
                fromf = f.name
                fromv = pf[rd + 1:]
                tof = ofn
                tov = ofn[rd + 1:-4]
                obsolete.append(f.name)
            else:
                # same timestamp? should pretty much never happen
                # take the newer version anyway
                if version.compare(pf[rd + 1:], ofn[rd + 1:-4]) > 0:
                    rtimes[pn] = (mt, f.name)
                    obsolete.append(ofn)
                else:
                    obsolete.append(f.name)

            if version.compare(tov, fromv) < 0 and not quiet:
                logger.get().warn(f"Using lower version ({fromf} => {tof}): newer timestamp...")

    for k, v in rtimes.items():
        olist.append(v[1])

    return obsolete

def prune(repopath):
    from cbuild.core import chroot

    repopath = repopath / chroot.target_cpu()

    if not repopath.is_dir():
        return

    logger.get().out(f"pruning old packages: {repopath}")

    nlist = []
    olist = summarize_repo(repopath, nlist, True)

    for pkg in olist:
        print(f"pruning: {pkg}")
        (repopath / pkg).unlink()

    logger.get().out("repo cleanup complete")

def build_index(repopath, epoch, keypath):
    repopath = pathlib.Path(repopath)

    aargs = ["--quiet"]

    if (repopath / "APKINDEX.tar.gz").is_file():
        aargs += ["--index", "APKINDEX.tar.gz"]

    # if no key is given, just use the final index name
    if not keypath:
        aargs += ["--allow-untrusted", "--output", "APKINDEX.tar.gz"]
    else:
        aargs += ["--output", "APKINDEX.unsigned.tar.gz"]

    summarize_repo(repopath, aargs)

    # create unsigned index
    signr = call("index", aargs, cwd = repopath, env = {
        "PATH": os.environ["PATH"],
        "SOURCE_DATE_EPOCH": str(epoch)
    })
    if signr.returncode != 0:
        logger.get().out_red("Indexing failed!")
        return False

    # we're done if no key is given
    if not keypath:
        return True

    try:
        signhdr = sign.sign(
            keypath, repopath / "APKINDEX.unsigned.tar.gz", epoch
        )
    except:
        return False

    # write signed index
    with open(repopath / "APKINDEX.tar.gz", "wb") as outf:
        outf.write(signhdr)
        with open(repopath / "APKINDEX.unsigned.tar.gz", "rb") as inf:
            while True:
                buf = inf.read(16 * 1024)
                if not buf:
                    break
                outf.write(buf)
        (repopath / "APKINDEX.unsigned.tar.gz").unlink()

    return True
