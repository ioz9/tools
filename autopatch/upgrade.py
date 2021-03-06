#!/usr/bin/python
# Filename: upgrade.py

### File Information ###
"""
Upgrade ROM version automatically.
Usage: upgrade.py FROM [TO]
         - FROM: current version (e.g. ROM40)
         - TO: version that upgrade to (e.g. ROM45). Default to be the latest version.
"""

__author__ = 'duanqizhi01@baidu.com (duanqz)'



import os
import sys
import string
from autopatch import AutoPatch
from config import Config
from log import Log


def usage():
    print "\n"
    print " Usage: upgrade.py FROM [TO]                                                                             "
    print "        - FROM: current version (e.g. ROM40)                                                             "
    print "        - TO: version that upgrade to (e.g. ROM45). If not present, will upgrade to the latest available."
    print "\n"


class Upgrade:

    def __init__(self, upgradeFrom, upgradeTo):
        self.run(upgradeFrom, upgradeTo)

    def run(self, oldVersion, newVersion):
        """ Upgrade from old version to new version
        """

        oldVersion = ROMVersion.toDigit(oldVersion)
        newVersion = ROMVersion.toDigit(newVersion)

        curVersion = oldVersion
        for patchName in ROMVersion.mPatches:
            if curVersion >= newVersion:
                break;

            delta = ROMVersion.toDigit(patchName) - curVersion
            if delta > 0:
                self.applyPatch(patchName)
                curVersion += delta

    def applyPatch(self, patchName):
        """ Apply the patch.
        """

        patchXML = os.path.join(Config.UPGRADE_DIR, patchName)
        Config.setPatchXML(patchXML)

        # Append the last BOSP directory to arguments list
        if os.path.exists(Config.UPGRADE_LAST_BAIDU_DIR) and \
           os.path.exists(Config.UPGRADE_BAIDU_DIR) :
            Config.setDiffDir(Config.UPGRADE_LAST_BAIDU_DIR, Config.UPGRADE_BAIDU_DIR)

        Log.i("\n>>> Patching " + patchName + "\t[Diff from " + Config.OLDER_DIR + " to " + Config.NEWER_DIR + " ]")
        AutoPatch()


class ROMVersion:
    """ Model of the ROM versions.
    """

    SPECIAL_VERSIONS = {"V6"       : 47.5,
                        "ROMV6.xml": 47.5,
                        "ROMV7.xml": 0.5,  # To be extended
                        "ROMV8.xml": 0.5   # To be extended
                       }

    mPatches = []

    def __init__(self):
        patches = os.listdir(Config.UPGRADE_DIR)
        for patch in patches:
            if patch.startswith("ROM"):
                ROMVersion.mPatches.append(patch)

        ROMVersion.mPatches.sort(cmp=ROMVersion.comparator);

    def getLatestVersion(self):
        size = len(ROMVersion.mPatches)
        return ROMVersion.mPatches[size-1]

    @staticmethod
    def comparator(patchName1, patchName2):
        """ Comparator to sort the patch name.
            Patch name is like ROM39, ROM40, etc.
        """

        delta = ROMVersion.toDigit(patchName1) - ROMVersion.toDigit(patchName2)
        if delta == 0: return 0
        if delta >  0: return 1
        if delta <  0: return -1

    @staticmethod
    def toDigit(patchName):
        """ Change to version number(integer or special float) from patch name.
        """

        specialVersion = ROMVersion.SPECIAL_VERSIONS.get(patchName)
        if specialVersion != None:
            return specialVersion

        version = filter(str.isdigit, patchName)
        return string.atoi(version)


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc <= 1:
        usage()
        exit(1)

    upgradeTo = ROMVersion().getLatestVersion()
    if argc > 1: upgradeFrom = sys.argv[1]
    if argc > 2: upgradeTo = sys.argv[2]

    Upgrade(upgradeFrom, upgradeTo)
