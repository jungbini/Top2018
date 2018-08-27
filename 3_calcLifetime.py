# -*- encoding:utf-8*-
import glob
from pandas import DataFrame
from collections import OrderedDict

DRIVE_PATH      = 'F:/'       
ROOT_PATH       = DRIVE_PATH + 'Tools/revision(TOP)/'

warningList = list()
for line in open(DRIVE_PATH + 'Tools/pmd-5.3.1/PMD_Rules(5.3.0).csv'):
    warningList.append(line.split(',')[1].strip())

def calcLifetime(project):
    
    PROJECT_PATH = ROOT_PATH + project + '/'
    LIFETIME_PATH = PROJECT_PATH + 'STATIC_ANALYSIS/AlertLifeTime/'
    PMDResultPath = LIFETIME_PATH + 'OrderedSummary/'
    AlertLifetimePath = LIFETIME_PATH + 'FinalResult/'
        
    finalLifetimes = OrderedDict()
    for warnIndex in range(0, 248):
        finalLifetimes[warningList[warnIndex]] = 0
        
    for filename in glob.glob(PMDResultPath + '*.csv'):
        
        OUTFILE = open(AlertLifetimePath + filename[filename.rfind('\\')+1:], 'a')
        
        revFileDict = dict()
        for revFile in open(filename):
            revFileDict[revFile.split(',')[0]] = revFile.split(',')[1:-1]
        
        revFileDataFrame = DataFrame(revFileDict)           # Dictionary를 데이터 프레임으로 만들기
        
        warnIndex = 0
        warningLifetimeDict = dict()
        for warnIndex in range(0, len(revFileDataFrame.index)): # 행을 기준으로 반복
            
            existWarning = False
            ellapsedTime = 0.0
            warningLifetimeList = list()
            for colValue in range(0, len(revFileDataFrame.columns)):
                
                # warning이 발견되면, 지워지기까지 걸리는 시간 카운팅
                if int(revFileDataFrame.ix[warnIndex][colValue]) > 0:                       
                    existWarning = True
                    ellapsedTime += float(revFileDataFrame.columns[colValue])
                    continue        
                
                # existWarning이 true이고 warning이 0이면 제거 되었다는 뜻
                if int(revFileDataFrame.ix[warnIndex][colValue]) == 0 and existWarning == True:
                    existWarning = False                    
                    ellapsedTime += float(revFileDataFrame.columns[colValue])
                    warningLifetimeList.append(ellapsedTime)        # 지워지기까지 소요된 시간을 list에 추가
                    ellapsedTime = 0                    
                    continue
            
            # warning은 존재하지만, 제거되지 않았을 경우
            if existWarning and len(warningLifetimeList) == 0:
                average = 365;            
            elif not existWarning and len(warningLifetimeList) != 0:
                average = sum(warningLifetimeList) / len(warningLifetimeList)
            else:
                average = 0
                
            warningLifetimeDict[warningList[warnIndex]] = average                
        
        for key, value in warningLifetimeDict.items():                    
            OUTFILE.write(str(key) + ',' + str(value) + '\n')
            finalLifetimes[key] += value
    
    # 값을 기준으로 정렬하기
    odFinalLifetimes = OrderedDict(sorted(finalLifetimes.items(), key=lambda x: x[1]))
    
    FINAL_OUTPUT = open(LIFETIME_PATH + 'AlertLifetime.csv', 'a')
    FINAL_OUTPUT.write('CategoryName,Weight,Ranking\n')    
    
    rank = 0
    for key, value in odFinalLifetimes.items():
        if value != 0:  rank += 1
        
        FINAL_OUTPUT.write(key + ',' + str(value) + ',' + str(rank) + '\n')
        
        
# 프로젝트 리스트
GIT_PROJECTS = ['bonita']

for project in GIT_PROJECTS:
    calcLifetime(project)    
            