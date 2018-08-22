# -*- encoding:utf-8*-
import re
import datetime

# Commit Log에서 찾아낼 정규식 패턴
DatePattern = re.compile('Date:\s(.*)00\n')
IndexPattern = re.compile('index ([0-9a-fA-F]+)..([0-9a-fA-F]+)\s([0-9]*)')
FilepathPattern = re.compile('diff --git a(.*)java ')

epoch = datetime.datetime.utcfromtimestamp(0)
    
def openProject(projectName):
    
    # 각 프로젝트에서 Commit Log 읽어오기
    CommitLogFile = open('F:/Tools/revision(TOP)/' + projectName + '/COMMIT_LOG/BUGFIX_LOG.txt', 'r')
    
    # 날짜, 파일명 형식으로 기록
    outputFile = open('F:/Tools/revision(TOP)/' + projectName + '/DOWNLOAD/revDateperFile.csv', 'a')
    
    tmpDate = ''
    tmpFileName = ''
    tmpIndex = ''
    for line in CommitLogFile:

        # Revision 시간 찾기
        dp = DatePattern.match(line)
        if dp:
            tmpDate = line[6:line.rfind('+')].strip()
            
            # datetime 형식으로 저장
            tmpDate = convertStr2Datetime(line[6:line.rfind('+')].strip())
            tmpDate = (tmpDate-epoch).total_seconds()      

            continue
        
        # 파일 Path 찾기
        fp = FilepathPattern.match(line)
        if fp:
            tmpPath = line[13:line.rfind(' ')].strip()
            tmpFileName = tmpPath[tmpPath.rfind('/')+1:]
            continue
        
        # 파일 index 찾기
        ip = IndexPattern.match(line)
        if ip:
            if tmpFileName != '':
                tmpIndex = line[6:line.find('..')].strip()
                
                # 파일 쓰기
                outputFile.write(str(tmpDate) + ',' + tmpFileName + '[' + tmpIndex + ']\n')
                
                # 하나의 리비전에 여러 파일이 있기 때문에 하나를 쓰면 비워놔야 함
                tmpFileName = ''
                continue
            
# Commit log에 기록된 날짜를 datetime 형식으로 불러오기
def convertStr2Datetime(strDate):
    # Wed Nov 27 11:25:59 2013 형식
    return datetime.datetime.strptime(strDate, "%a %b %d %H:%M:%S %Y")       
            

# 프로젝트 리스트
GIT_PROJECTS = ['bonita']

for project in GIT_PROJECTS:
    openProject(project)