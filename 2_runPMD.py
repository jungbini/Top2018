# -*- encoding:utf-8*-
import os, re, glob, shutil
from collections import OrderedDict

DRIVE_PATH      = 'F:/'       
ROOT_PATH       = DRIVE_PATH + 'Tools/revision(TOP)/'
TOOL_PATH       = DRIVE_PATH + 'Tools/pmd-5.3.1/bin/'

warnDict = OrderedDict()
for line in open(DRIVE_PATH + 'Tools/pmd-5.3.1/PMD_Rules(5.3.0).csv'):
    warnDict[line.split(',')[1].strip()] =  0

def runPMD(projectName):
    
    SubjectPath = ROOT_PATH + projectName
    TrainsetPath = SubjectPath + '/DOWNLOAD/BUGGY/'
    ResultPath = SubjectPath + '/STATIC_ANALYSIS/AlertLifeTime/'
    
    if os.path.exists(ResultPath):         # 결과 저장 디렉토리가 있으면 기존 파일들 모두 지우기
        shutil.rmtree(ResultPath)
    
    if not os.path.exists(ResultPath):      # 결과 저장 디렉토리가 없으면 생성
        os.makedirs(ResultPath)
    
    print TrainsetPath
  
    curDir = os.getcwd()
    os.chdir(TOOL_PATH)    
    cmd_result = os.system('pmd -d '+ TrainsetPath + ' -f csv -R rulesets/java/basic.xml,rulesets/java/braces.xml,rulesets/java/clone.xml,'+
                               'rulesets/java/codesize.xml,rulesets/java/comments.xml,rulesets/java/controversial.xml,rulesets/java/coupling.xml,rulesets/java/design.xml,'+
                               'rulesets/java/empty.xml,rulesets/java/finalizers.xml,rulesets/java/imports.xml,rulesets/java/j2ee.xml,rulesets/java/javabeans.xml,'+
                               'rulesets/java/junit.xml,rulesets/java/logging-jakarta-commons.xml,rulesets/java/logging-java.xml,rulesets/java/migrating.xml,'+
                               'rulesets/java/naming.xml,rulesets/java/optimizations.xml,rulesets/java/strictexception.xml,rulesets/java/strings.xml,rulesets/java/sunsecure.xml,'+
                               'rulesets/java/typeresolution.xml,rulesets/java/unnecessary.xml,rulesets/java/unusedcode.xml > ' + ResultPath + 'PMD_RESULT1.txt')
           
    if not cmd_result == 0:
        print '에러 발생\n'        

    RESULT_FILE = open(ResultPath + 'PMD_RESULT1.txt', 'r')
    OUT_FILE = open(ResultPath + 'PMD_RESULT2.txt', 'w')
          
    for line in RESULT_FILE:
         
        if (not line.startswith('Removed') and not line.startswith('\"Problem') and line.startswith('\"')):
             
            alertToken = re.match('"(\d+)","(.*)","(.*)","(\d+)","(\d+)","(.*)","(.*)","(.*)"', line)   # 정규식으로 뽑아오기
         
            # 파일 이름, Alert 이름, 위반 라인 추출
            if alertToken:
                filename = alertToken.group(3).replace('\\', '/')                         # 파일 이름, Alert 이름, 위반 라인 추출
                filename = filename[filename.rfind('/')+1:]
                alertline = alertToken.group(5)
                alertname = alertToken.group(8)
                
                revNum = filename[:filename.rfind(']')+1]
                tmpFilename = filename[filename.find(']')+1:]
                finalFileName = tmpFilename + revNum                                                             
                 
                OUT_FILE.write(finalFileName + ',' + alertline + ',' + alertname + '\n')
                
    os.chdir(curDir) 

# PMD 파일에서 Warning 위반 갯수 정보 가져오는 함수
def getWarningInfo(projectName):
    
    SubjectPath = DRIVE_PATH + 'Tools/revision(TOP)/' + projectName
    ResultPath = SubjectPath + '/STATIC_ANALYSIS/AlertLifeTime/'
    
    filePath = ResultPath + 'PMD_RESULT2.txt'
    
    if os.path.exists(ResultPath + 'PMD_RESULT3.txt'):
        os.remove(ResultPath + 'PMD_RESULT3.txt')
    
    OUTPUT_FILE = open(ResultPath + 'PMD_RESULT3.txt', 'a')
    
    WarnInfoDict = dict()                                                       # 파일별로 warning category에 위반된 갯수 저장
    for line in open(filePath):
        tokenLine = line.strip().split(',')        
        
        if tokenLine[2] in warnDict.keys():                                     # 해당 warning이 PMD warning list에 있다면,
        
            if not WarnInfoDict.has_key(tokenLine[0]):                          # 파일명 자체를 key로 가지고 있지 않으면,    
                WarnInfoDict[tokenLine[0]] = warnDict.copy()                    # 모든 warning category key, value(0)를 복사                
                WarnInfoDict[tokenLine[0]][tokenLine[2]] = 1                    # 해당 warning도 새로 나온 것이므로, 해당 warning 0부터 시작
            else:                                                               # 파일명을 key로 가지고 있다면,            
                WarnInfoDict[tokenLine[0]][tokenLine[2]] += 1                    
        
    for k1, sub_dic in sorted(WarnInfoDict.items()):        
        for k2, v in sub_dic.items():
            OUTPUT_FILE.write(k1 + ',' + k2 + ',' + str(v) + '\n')
            
    return WarnInfoDict

def summarizeFixedWarning(projectName, warnInfoDict):
    
    SubjectPath = DRIVE_PATH + 'Tools/revision(TOP)/' + projectName
    ResultPath = SubjectPath + '/STATIC_ANALYSIS/AlertLifeTime/Summary/'
    
    if os.path.exists(ResultPath):         # 결과 저장 디렉토리가 있으면 기존 파일들 모두 지우기
        shutil.rmtree(ResultPath)
    
    if not os.path.exists(ResultPath):      # 결과 저장 디렉토리가 없으면 생성
        os.makedirs(ResultPath)
               
    for k1, sub_dic in sorted(warnInfoDict.items()):
        
        fileName    = k1[:k1.find('.')]
        revNum      = k1[k1.find('['):]     
        
        # revision이 하나밖에 없는 파일은 변화를 관찰할 수 없으므로 생략
        fileList = [files for files in warnInfoDict.keys() if fileName in files]        
        if len(fileList) <= 1:  continue 
        
        OUTFILE = open(ResultPath + fileName + '.csv', 'a')            
        OUTFILE.write(revNum + ',')                               # 파일 리비전 넘버 기록
        
        for k2, v in sub_dic.items():
            OUTFILE.write(str(v) + ',')
        OUTFILE.write('\n')
        
    OUTFILE.close()
    
def orderFilesbyRevDate(projectName):
    
    SubjectPath = DRIVE_PATH + 'Tools/revision(TOP)/' + projectName
    RevInfoPath = SubjectPath + '/DOWNLOAD/'
    STATIC_ANALYSIS_PATH = SubjectPath + '/STATIC_ANALYSIS/AlertLifeTime/'
    PMDResultPath = STATIC_ANALYSIS_PATH + 'Summary/'
    OrderedResultPath = STATIC_ANALYSIS_PATH + 'OrderedSummary/'
    
    if os.path.exists(OrderedResultPath):         # 결과 저장 디렉토리가 있으면 기존 파일들 모두 지우기
        shutil.rmtree(OrderedResultPath)
    
    # 결과 저장 디렉토리가 없으면 생성
    if not os.path.exists(OrderedResultPath):
        os.makedirs(OrderedResultPath)
        
    RevDateDict = dict()
    for line in open(RevInfoPath + 'revDateperFile.csv'):
        
        fileName = line.split(',')[1].strip()
        timeStamp = line.split(',')[0]
        
        RevDateDict[fileName] = timeStamp
    
    for filename in glob.glob(PMDResultPath + '*.csv'):    
                
        RevFiles = dict()
        for revFile in open(filename):
            revNum = revFile.split(',')[0]             # 파일의 Revision Number            

            try:
                timestamp = [value for key, value in RevDateDict.items() if revNum in key][0]       # 해당 revision number를 포함하는 키를 찾아 timestamp를 저장
            except IndexError:
                print filename + '이 리스트에 없습니다.'
                continue
                  
            RevFiles[timestamp] = revFile
        
        OUTPUT_FILE = open(SubjectPath + '/STATIC_ANALYSIS/AlertlifeTime/OrderedSummary/' + filename[filename.rfind('\\'):], 'a')        
        OrderedRevFiles = OrderedDict(sorted(RevFiles.items(), reverse=False))
        for key, value in OrderedRevFiles.items():
            if OrderedRevFiles.keys().index(key) == 0:                
                OUTPUT_FILE.write('0,' + value[value.find(',')+1:])
            else:
                prevTimestamp = OrderedRevFiles.keys()[OrderedRevFiles.keys().index(key)-1]
                deltaTimestamp = round(float(key)) - round(float(prevTimestamp))
                deltaDays = deltaTimestamp / 60 / 60 / 24
                OUTPUT_FILE.write(str(deltaDays) + ',' + value[value.find(',')+1:])
       
# 프로젝트 리스트
PROJECTS = ['bonita', 'cassandra', 'checkstyle', 'elasticsearch', 'flink', 'guava', 'guice', 'hadoop_git', 'itext-itextpdf', 'jackrabbit', 'jbpm', 'jclouds', 
            'jenkins', 'libgdx', 'mahout', 'maven_core', 'mylyn', 'neo4j', 'openmap', 'orientdb', 'pivot', 'titan', 'tomcat', 'wildfly', 'ant', 'drools', 'lucene_trunk']

for project in PROJECTS:
    print project + ' Project Static analysis 수행 중...'
    
#     runPMD(project)                                     # 1. PMD 실행
    warnInfoDict = getWarningInfo(project)              # 2. 파일별 위반 warning 건수로 파싱
    summarizeFixedWarning(project, warnInfoDict)        # 3. 파일별로 수정된 warning 건수 요약
    orderFilesbyRevDate(project)