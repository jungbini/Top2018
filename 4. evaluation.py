# -*- encoding:utf-8-*-
import os
from collections import OrderedDict, defaultdict
from scipy.stats.stats import pearsonr

DRIVE_PATH      = 'D:/'       
ROOT_PATH       = DRIVE_PATH + 'Tools/revision(TOP)/'

def getALTSummary(project):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'TopicEvaluation/'
    ALTEVALUATION_PATH      = PRIORITIZATION_PATH + 'ALTEvaluation/'
    
    # 결과 저장 디렉토리가 없으면 생성
    if not os.path.exists(ALTEVALUATION_PATH):
        os.makedirs(ALTEVALUATION_PATH)
    
    OUT_FILE = open(ALTEVALUATION_PATH + 'ALT_SUMMARY.csv', 'w')
    METRICS_FILE = open(ALTEVALUATION_PATH + 'ALT_METRIC_RESULT.csv', 'w')
    
    testDict = OrderedDict()
    for testLine in open(EVALUATION_PATH + 'HWP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.strip().split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Topic 번호 = key, Category Name = Sub Key, Occurrence, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = OrderedDict({tokenLine[1]: tokenLine[2:]})
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    trainInfoDict = OrderedDict()
    for trainLine in open(ALTEVALUATION_PATH + 'ALT_RANK.csv'):
        
        if 'CategoryName' in trainLine:     continue
        
        tokenLine = trainLine.strip().split(',')
        
        trainInfoDict[tokenLine[0]] = tokenLine[1:]                     # CategoryName을 Key로 하여, Weight, Ranking을 리스트로 저장
    
    AOPDict = defaultdict(list)                                         # Average of Precision Metric 저장
    RCDict  = defaultdict(list)                                         # Ranking Correlation Metric 저장
    WDRDict = defaultdict(list)                                         # Warning Detection Rate 을 구하기 위한 토픽별 Fixed Warning 갯수 저장
    
    for topicNum in range(0,len(testDict)):
        
        categoryCount       = 0
        sumOfWeight         = 0
        sumOfFixnum         = 0
        testRankingList     = list()
        trainRankingList    = list()       
        
        for wName, wInfo in trainInfoDict.items():           
            
            trainRankingList.append(float(wInfo[1]))                        # trainRaking 리스트에 train 랭킹을 순차적으로 쌓기            
            
            testInfo = testDict[str(topicNum)][wName]                       # 토픽 0부터 시작해서 Test 정보 가져오기                 
            
            testRankingList.append(float(testInfo[2]))                      # testRanking 리스트에 test 랭킹을 순차적으로 쌓기
                    
            sumOfWeight += float(testInfo[1])                               # weight 값 누적
            sumOfFixnum += float(testInfo[0])
            categoryCount += 1                                              # category 갯수 누적
            corrRank = pearsonr(trainRankingList, testRankingList)          # Ranking Pearson Correlation 구하기
            
            OUT_FILE.write(str(topicNum) + ',' + wName + ',' + trainInfoDict[wName][0] + ',' + testInfo[1] + ',' + str(sumOfWeight) + ',' + str(sumOfWeight/categoryCount) + ',' + trainInfoDict[wName][1] + ',' + testInfo[2].strip() + ',' + str(corrRank[0]) + ',' + testInfo[0]+ ',' + str(sumOfFixnum) + '\n')
            
            if categoryCount <= 256:                                         # n개까지 Average of Precision 기록하기
                AOPDict[str(topicNum)].append(sumOfWeight/categoryCount)
                RCDict[str(topicNum)].append(corrRank[0])
                WDRDict[str(topicNum)].append(sumOfFixnum)
    
    MetricsList = ['AOP', 'RC', 'WDR']
    
    for metric in MetricsList:                                                # Header 출력        
        for i in range(0, len(AOPDict)):        
            METRICS_FILE.write('Topic' + str(i) + ',')                        # Metric이 3개이므로 쉼표도 3개
        METRICS_FILE.write(metric + ',,')
    METRICS_FILE.write('\n')
    
    MetricAvgList = defaultdict(list)                                           # 각 Metric의 모든 토픽의 평균값 저장        
    Idx = 0
    while Idx < len(AOPDict['0']): 
        
        for metric in MetricsList:                                                  # 각 Metric 출력
        
            tmpMetricDict = defaultdict(list)       
            if metric == 'AOP':     tmpMetricDict = AOPDict                         # 각 metric 순서에 따라 metric 정보 가져오기                 
            elif metric == 'RC':    tmpMetricDict = RCDict
            else:                   tmpMetricDict = WDRDict

            topicIdx = 0
            avgResult = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # 토픽별 AOP 출력
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # 평균을 내기 위해 Precision 축적                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # 각 Metric의 모든 토픽의 평균값 저장
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic의 갯수로 나누면 평균            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

# 프로젝트 리스트
GIT_PROJECTS = ['bonita']

for project in GIT_PROJECTS:
    getALTSummary(project)