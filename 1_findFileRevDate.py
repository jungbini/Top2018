# -*- encoding:utf-8*-
import re
import datetime

# Git Commit Log에서 찾아낼 정규식 패턴
GitDatePattern = re.compile('Date:\s(.*)00\n')
GitIndexPattern = re.compile('index ([0-9a-fA-F]+)..([0-9a-fA-F]+)\s([0-9]*)')
GitFilepathPattern = re.compile('diff --git a(.*)java ')

# SVN Commit Log에서 찾아낼 정규식 패턴
SvnDatePattern = re.compile('r([0-9]+)\s|(.*)행\n')
SvnIndexPattern = re.compile('---\s(.*)\r\n')
SvnFilepathPattern = re.compile('Index:\s(.*)java\r\n')

epoch = datetime.datetime.utcfromtimestamp(0)
    
ROOT_DRIVE = 'F:/'
ROOT_PATH = ROOT_DRIVE + '/Tools/revision(TOP)/'
    
def openGitProject(projectName):
    
    # 각 프로젝트에서 Commit Log 읽어오기
    CommitLogFile = open(ROOT_PATH + projectName + '/COMMIT_LOG/BUGFIX_LOG.txt', 'r')
    
    # 날짜, 파일명 형식으로 기록
    outputFile = open(ROOT_PATH + projectName + '/DOWNLOAD/revDateperFile.csv', 'a')
    
    tmpDate = ''
    tmpFileName = ''
    tmpIndex = ''
    for line in CommitLogFile:

        # Revision 시간 찾기
        dp = GitDatePattern.match(line)
        if dp:            
            tmpDate = line[6:line.rfind(' ')].strip()
                        
            # datetime 형식으로 저장
            tmpDate = convertStr2GitDatetime(tmpDate)
            tmpDate = (tmpDate-epoch).total_seconds()      

            continue
        
        # 파일 Path 찾기
        fp = GitFilepathPattern.match(line)
        if fp:
            tmpPath = line[13:line.rfind(' ')].strip()
            tmpFileName = tmpPath[tmpPath.rfind('/')+1:]
            continue
        
        # 파일 index 찾기
        ip = GitIndexPattern.match(line)
        if ip:
            if tmpFileName != '':
                tmpIndex = line[6:line.find('..')].strip()
                
                # 파일 쓰기
                outputFile.write(str(tmpDate) + ',' + tmpFileName + '[' + tmpIndex + ']\n')
                
                # 하나의 리비전에 여러 파일이 있기 때문에 하나를 쓰면 비워놔야 함
                tmpFileName = ''
                continue
            
def openSVNProject(projectName):
    
    # 각 프로젝트에서 Commit Log 읽어오기
    CommitLogFile = open(ROOT_PATH + projectName + '/COMMIT_LOG/BUGFIX_LOG.txt', 'r')
    
    # 날짜, 파일명 형식으로 기록
    outputFile = open(ROOT_PATH + projectName + '/DOWNLOAD/revDateperFile.csv', 'a')
    
    tmpDate = ''
    tmpFileName = ''
    tmpIndex = ''
    for line in CommitLogFile:

        # Revision 시간 찾기
        dp = SvnDatePattern.match(line)
        if dp:            
            tmpDate = line.split(' | ')[2]
            tmpDate = tmpDate[:tmpDate.rfind('+')-1]
                        
            # datetime 형식으로 저장
            tmpDate = convertStr2SvnDatetime(tmpDate)
            tmpDate = (tmpDate-epoch).total_seconds()      

            continue
        
        # 파일 Path 찾기
        fp = SvnFilepathPattern.match(line)
        if fp:
            tmpPath = line[line.find(':')+1:].strip()
            tmpFileName = tmpPath[tmpPath.rfind('/')+1:]
            continue
        
        # 파일 index 찾기
        ip = SvnIndexPattern.match(line)
        if ip:
            if tmpFileName != '':
                tmpIndex = line[line.rfind(' ')+1:line.find(')')]
                
                # 파일 쓰기
                outputFile.write(str(tmpDate) + ',' + tmpFileName + '[' + tmpIndex + ']\n')
                
                # 하나의 리비전에 여러 파일이 있기 때문에 하나를 쓰면 비워놔야 함
                tmpFileName = ''
                continue
            
# Commit log에 기록된 날짜를 datetime 형식으로 불러오기
def convertStr2GitDatetime(strDate):
    # Wed Nov 27 11:25:59 2013 형식    
    return datetime.datetime.strptime(strDate, "%a %b %d %H:%M:%S %Y")

def convertStr2SvnDatetime(strDate):       
    # 2014-05-04 17:25:22 형식
    return datetime.datetime.strptime(strDate, "%Y-%m-%d %H:%M:%S")

# 프로젝트 리스트
PROJECTS = ['bonita', 'cassandra', 'checkstyle', 'elasticsearch', 'flink', 'guava', 'guice', 'hadoop_git', 'itext-itextpdf', 'jackrabbit', 'jbpm', 'jclouds', 
                       'jenkins', 'libgdx', 'mahout', 'maven_core', 'mylyn', 'neo4j', 'openmap', 'orientdb', 'pivot', 'titan', 'tomcat', 'wildfly']
SVN_PROJECTS = ['ant', 'drools', 'lucene_trunk'] 

# for project in PROJECTS:
#     print project + ' Project Revision Date 찾는 중...'
#     openGitProject(project)

for project in SVN_PROJECTS:
    print project + ' Project Revision Date 찾는 중...'
    openSVNProject(project)