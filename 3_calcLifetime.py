# -*- encoding:utf-8*-
import glob
from pandas import DataFrame

DRIVE_PATH      = 'D:/'       
ROOT_PATH       = DRIVE_PATH + 'Tools/revision(TOP)/'


def calcLifetime(project):
    
    PROJECT_PATH = ROOT_PATH + project + '/'
    PMDResultPath = PROJECT_PATH + 'STATIC_ANALYSIS/AlertLifeTime/OrderedSummary/'
    AlertLifetimePath = PROJECT_PATH + 'STATIC_ANALYSIS/AlertLifeTime/FinalResult/'
    
    for filename in glob.glob(PMDResultPath + '*.csv'):
        
        OUTFILE = open(AlertLifetimePath + filename[filename.rfind('\\')+1:], 'a')
        
        revFileDict = dict()
        for revFile in open(filename):
            revFileDict[revFile.split(',')[0]] = revFile.split(',')[1:-1]
        
        revFileDataFrame = DataFrame(revFileDict)
        
        warnIndex = 0
        warningLifetimeDict = dict()
        for warnIndex in range(0, len(revFileDataFrame.index)):
            
            existWarning = False
            ellapsedTime = 0.0
            warningLifetimeList = list()
            for colValue in range(0, len(revFileDataFrame.columns)):
                if revFileDataFrame.ix[warnIndex][colValue] > 0:
                    existWarning = True
                    ellapsedTime += float(revFileDataFrame.columns[colValue])
                    continue        
                
                if revFileDataFrame.ix[warnIndex][colValue] == 0 and existWarning == True:
                    existWarning = False                    
                    ellapsedTime += revFileDataFrame.columns[colValue]
                    warningLifetimeList.append(ellapsedTime)
                    ellapsedTime = 0                    
                    continue
            
            if len(warningLifetimeList) != 0:
                average = sum(warningLifetimeList) / len(warningLifetimeList)
            else:
                average = 0
                
            warningLifetimeDict[warnIndex] = average                
        
        for key, value in warningLifetimeDict.items():                    
            OUTFILE.write(str(key) + ',' + str(value) + '\n')
        
# 프로젝트 리스트
GIT_PROJECTS = ['bonita']

for project in GIT_PROJECTS:
    calcLifetime(project)    
            