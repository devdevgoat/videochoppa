
from os.path import basename, expanduser, isfile, exists, join as joined
import csv

class ClipLog(object):
    def __init__(self, parent, videoName) -> None:
        self.root = parent
        self.log = self.getLog(videoName)
        self.maxId = self.getMaxId()

    def getLog(self, videoName):
        if self.root.rp._isWindows:
            filebase = 'cliplogs\\'
        else:
            filebase = 'cliplogs/'
        self.logFileName = f"{filebase}{videoName.split('.')[0]}.csv"
        #Create the log for this video
        if not exists(self.logFileName):
            logFile = open(self.logFileName,'w')
            logFile.write('id,startMs,endMs,desc,chars\n')
            logFile.close
        logFile = open(self.logFileName,'r')
        log = list(csv.DictReader(logFile))
        logFile.close()
        return log

    def getMaxId(self):
        maxClip = 0
        for i in self.log:
            if int(i['id']) > maxClip:
                maxClip = int(i['id'])
        return maxClip

    def addEntry(self, logLine):
        with open(logLine['logname'],'a') as f:
            out = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            out.writerow([logLine['id'],logLine['startMs'],logLine['endMs'],logLine['desc'],logLine['chars']])
        # jsonOut = {logLine['id']:[logLine['startMs'], logLine['endMs'],f"{logLine['desc']}",logLine['chars']]}
        self.root.clipmanager.addEntry(logLine)
        return logLine