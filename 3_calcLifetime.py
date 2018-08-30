# -*- encoding:utf-8*-
import glob, os, random, shutil
from pandas import DataFrame
from collections import OrderedDict, defaultdict

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
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'ALTEvaluation/'
                
    if os.path.exists(AlertLifetimePath):         # 결과 저장 디렉토리가 있으면 기존 파일들 모두 지우기
        shutil.rmtree(AlertLifetimePath)    
    if not os.path.exists(AlertLifetimePath):     # 결과 저장 디렉토리가 없으면 생성
        os.makedirs(AlertLifetimePath)
    
    if os.path.exists(EVALUATION_PATH):         # 결과 저장 디렉토리가 있으면 기존 파일들 모두 지우기
        shutil.rmtree(EVALUATION_PATH)    
    if not os.path.exists(EVALUATION_PATH):     # 결과 저장 디렉토리가 없으면 생성
        os.makedirs(EVALUATION_PATH)               
        
    finalLifetimes = OrderedDict()
    for warnIndex in range(0, 256):
        finalLifetimes[warningList[warnIndex]] = 0

    warningFileNum = defaultdict(int)
    for filePath in glob.glob(PMDResultPath + '*.csv'):
        
        OUTFILE = open(AlertLifetimePath + filePath[filePath.rfind('\\')+1:], 'a')                     
        
        revFileDict = dict()
        for revFile in open(filePath):
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
                totalDays = 365;   
                warningFileNum[warningList[warnIndex]] += 1         
            elif not existWarning and len(warningLifetimeList) != 0:
                totalDays = sum(warningLifetimeList)
                warningFileNum[warningList[warnIndex]] += 1
            else:
                totalDays = 0
                
            warningLifetimeDict[warningList[warnIndex]] = totalDays                
        
        for key, value in warningLifetimeDict.items():                    
            OUTFILE.write(str(key) + ',' + str(value) + '\n')
            finalLifetimes[key] += value
    
#     # 값을 기준으로 정렬하기
#     odFinalLifetimes = OrderedDict(sorted(finalLifetimes.items(), key=lambda x: x[1]))
    
    FINAL_OUTPUT = open(EVALUATION_PATH + 'ALT_WEIGHT.csv', 'w')
    RAND_OUTPUT = open(EVALUATION_PATH + 'ALT_RAND_WEIGHT.csv', 'w')
    FINAL_OUTPUT.write('CategoryName,Weight\n')
    
    for key, value in sorted(finalLifetimes.items(), key=lambda (k, v): (v, k)):
        if warningFileNum[key] != 0:
            averageDays = float(value / warningFileNum[key])
        else:
            averageDays = 0.0
        FINAL_OUTPUT.write(key + ',' + str(averageDays) + '\n')
        RAND_OUTPUT.write(key + ',' + str(random.random()) + '\n')
        
# 프로젝트 리스트
# PROJECTS = ['bonita', 'cassandra', 'checkstyle', 'elasticsearch', 'flink', 'guava', 'guice', 'hadoop_git', 'itext-itextpdf', 'jackrabbit', 'jbpm', 'jclouds', 
#             'jenkins', 'libgdx', 'mahout', 'maven_core', 'mylyn', 'neo4j', 'openmap', 'orientdb', 'pivot', 'titan', 'tomcat', 'wildfly', 'ant', 'drools', 'lucene_trunk']
PROJECTS = ['neo4j', 'openmap', 'orientdb', 'pivot', 'titan', 'tomcat', 'wildfly', 'ant', 'drools', 'lucene_trunk']


for project in PROJECTS:
    print project + ' Project lifetime 우선순위화 수행  중...'
    
    calcLifetime(project)    
            