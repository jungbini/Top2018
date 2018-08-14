# -*- encoding:utf-8*-
import os, re
from collections import defaultdict, Counter

def runPMD(projectName):
    
    SubjectPath = 'D:/Tools/revision(TOP)/' + projectName
    TrainsetPath = SubjectPath + '/DOWNLOAD/BUGGY/'
    ResultPath = SubjectPath + '/STATIC_ANALYSIS/AlertLifeTime/'
    
    print TrainsetPath
  
    cmd_result = os.system('pmd -d '+ TrainsetPath + ' -f csv -R java-basic,java-braces,java-clone,java-codesize,java-comments,java-controversial,java-coupling,java-design,java-typeresolution,java-empty,java-finalizers,java-imports,java-j2ee,java-javabeans,java-junit,java-logging-jakarta-commons,java-logging-java,java-migrating,java-naming,java-optimizations,java-strictexception,java-strings,java-sunsecure,java-unnecessary,java-unusedcode > ' + ResultPath + 'PMD_RESULT1.txt')
        
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
                 
                OUT_FILE.write(filename + ',' + alertline + ',' + alertname + '\n')

# PMD 파일에서 Warning 위반 갯수 정보 가져오는 함수
def getWarningInfo(projectName):
    
    SubjectPath = 'D:/Tools/revision(TOP)/' + projectName
    TrainsetPath = SubjectPath + '/DOWNLOAD/BUGGY/'
    ResultPath = SubjectPath + '/STATIC_ANALYSIS/AlertLifeTime/'
    
    filePath = ResultPath + 'PMD_RESULT2.txt'
    
    FileInfoDict = dict()
    for line in open(filePath):
        tokenLine = line.strip().split(',')        
        
        if not FileInfoDict.has_key(tokenLine[0]):                      # 파일명 자체를 key로 가지고 있지 않으면,    
            # 해당 warning도 새로 나온 것이므로, 해당 warning 0부터 시작
            FileInfoDict[tokenLine[0]] = {tokenLine[2]: 0}
        else:                                                            # 파일명을 key로 가지고 있다면,
            # warning을 key로 다시 가지고 있는지 검사
            if not FileInfoDict[tokenLine[0]].has_key(tokenLine[2]):
                # key로 가지고 있지 않다면, 해당 warning은 0부터 시작
                FileInfoDict[tokenLine[0]] = {tokenLine[2]: 0}
            else:
                FileInfoDict[tokenLine[0]][tokenLine[2]] += 1
    
    return FileInfoDict
       
# 프로젝트 리스트
GIT_PROJECTS = ['bonita']

# for project in GIT_PROJECTS:
#     runPMD(project)
    
fileInfoDict = getWarningInfo('bonita')
for k, d in fileInfoDict.items():
   for sub_k, v in d.items():
       print k + ':' + sub_k + '=' + str(d[sub_k])