#!/usr/local/bin/python
import os
import argparse
import sys
import configparser
import pprint
import subprocess
import xml.etree.ElementTree as ET
import itertools
import pygit2
from pathlib import Path
from datetime import date

parser = argparse.ArgumentParser()
parser.add_argument("path", default=os.getcwd(), help='path to tests/auto', nargs="?")
parser.add_argument("platform", default="", help='platform (prefix)', nargs="?")
parser.add_argument("--blame", dest='blame', action='store_true', default=False, help='Run git blame on the BLACKLISTs')
parser.add_argument("--runtests", dest='testrun', action='store_true', default=False, help='Run the tests')
args = parser.parse_args()

testsPath = os.path.abspath(args.path)
print("Looking at tests in {0}".format(testsPath));

repositoryPath = pygit2.discover_repository(testsPath)
repo = None
try:
    repo = pygit2.Repository(repositoryPath)
    print ("Git repo path: {0}".format(repositoryPath))
except:
    print ("Git repo not found: blame disabled")

print("Platform: {0}".format(args.platform))


def blacklistDirs(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file == "BLACKLIST" and not "selftests/blacklisted" in root:
                yield root

def blacklistedTestFunctions(blacklistDir, platformPrefix):
    blacklistFile = os.path.join(blacklistDir, "BLACKLIST")
    with open(blacklistFile, "r") as ins:
        currentFunction = ""
        lineNumber = -1
        for line in ins:
            lineNumber += 1

            # look for [foo] lines to find test function names
            begin = line.find("[")
            end = line.find("]")
            if begin != -1 and end != -1:
                currentFunction = line[ begin + 1 : end ]
                continue
                    
            # yield any current function of the platform prefix matches:
            if len(currentFunction) > 0 and line.startswith(platformPrefix) and not line.startswith("#") :
                yield (currentFunction, line.strip(), lineNumber)

def parseTestXmlForPassFail(xml, testFunction):
    try:
        tree = ET.parse(xml)
        root = tree.getroot()
        for child in root:
            # testFunction includes the data tag ("test_plist:LSUIElement-as-garbage"),
            # while the name attribute has the function name only.
            nameOnly = testFunction.split(":")[0]
            if child.tag == "TestFunction" and child.attrib["name"] == nameOnly:
                for cchild in child:
                    if cchild.tag == "Incident":
                        yield cchild.attrib["type"].upper()
    except:
        yield "XML PARSE ERROR"

def runTest(testDir, testFunction):
    head, tail = os.path.split(blacklistDir)
    testBinary = "tst_" + tail
    if not os.path.exists(os.path.join(testDir, testBinary)):
        return ["NO TEST BINARY"]

    command = "./" + testBinary  + " " + testFunction + " -xml"
    p = subprocess.Popen(command, cwd = testDir, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

    if "Unknown test function" in p.stderr:
        return ["UNKNOWN TEST FUNCTION"]
    
    return list(parseTestXmlForPassFail(p.stdout, testFunction))

def blacklistBlame(repo, blacklistDir):
    if repo is None:
        return None

    blacklistAbs = Path(os.path.join(blacklistDir, "BLACKLIST"))
    repoPath = Path(repo.path[:-5]) # repo path wihout trailing ".git"
    blacklistRel = blacklistAbs.relative_to(repoPath)
    
    return repo.blame(str(blacklistRel))

def formatBlacklistBlame(repo, blame, lineNumber):
    if repo is None or blame is None:
        return ""

    hunk = blame.for_line(lineNumber)
    shortSha1 = (str(hunk.final_commit_id))[0:8]

    commit = repo.get(hunk.final_commit_id)
    year = str(date.fromtimestamp(commit.commit_time).year)
    description = commit.message.splitlines()[0]
    return shortSha1 + " " + year + " " + description

# statistics
passCount = 0;
failCount = 0;
naCount = 0;
def interpretStatus(statuses):
    global passCount, failCount, naCount
    seenPass = False
    seenFail = False
    
    # if the test function has data there might be multiple statues.
    # we want to count this as a single pass/fail
    for status in statuses:
        if "PASS" in status or "BPASS" in status:
            seenPass = True
        if "FAIL" in status or "BFAIL" in status:
            seenFail = True

    # count any sub-failure as a full failure
    if seenFail:
      failCount += 1
      return
    if seenPass:
      passCount += 1
      return
       
    naCount += 1

def printStats():
    global passCount, failCount, naCount
    total = passCount + failCount + naCount;
    print("Totals: Pass {0:4} Fail {1:4} Unknown {2:4}".format(passCount, failCount, naCount))
    print("Rate  : Pass {0:3.0f}% Fail {1:3.0f}% Unknown {2:3.0f}%".format(100 * passCount/total, 100 * failCount/total, 100 * naCount/total))

format = "{0:30.29}{1:55.54}{2:30.29}{3:15.14}{4:10}"
print(format.format("TEST", "FUNCTION", "STATUS", "BLACKLIST", "BLAME"))

for blacklistDir in blacklistDirs(testsPath):
    head, tail = os.path.split(blacklistDir)
    
    # git blame
    if args.blame:
        blame = blacklistBlame(repo, blacklistDir)
    else:
        blame = None

    for function, platformSpec, lineNumber in blacklistedTestFunctions(blacklistDir, args.platform):
        
        # run test
        if args.testrun:
            status = runTest(blacklistDir, function)
        else:
            status = ""

        interpretStatus(status)
        functionBlame = formatBlacklistBlame(repo, blame, lineNumber)
        print(format.format(tail, function, str(status)[0:30 - 1], platformSpec, functionBlame[0:60]))

print("")
printStats()