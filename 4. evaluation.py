# -*- encoding:utf-8*-
import os
from collections import OrderedDict, defaultdict
from scipy.stats.stats import pearsonr
from scipy.stats import rankdata
from operator import itemgetter

DRIVE_PATH      = 'F:/'       
ROOT_PATH       = DRIVE_PATH + 'Tools/revision(TOP)/'

def getTOPSummary(project):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'TopicEvaluation/'
    WARNING_RANK_PATH       = PRIORITIZATION_PATH + 'WarningRank/'
    
    OUT_FILE        = open(EVALUATION_PATH + 'TOP_SUMMARY.csv', 'w')
    METRICS_FILE    = open(EVALUATION_PATH + 'TOP_METRICS_RESULT.csv', 'w')
    
    testDict = dict()
    for testLine in open(EVALUATION_PATH + 'TOP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Category 이름 = key, 나머지 fixNum, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = {tokenLine[1]: tokenLine[2:]}
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    categoryCount       = 0
    sumOfWeight         = 0
    sumOfFixnum         = 0
    testRankingList     = list()
    trainRankingList    = list()
    tmpTopicNum         = 0
    
    AOPDict = defaultdict(list)                                             # Average of Precision Metric 저장
    RCDict  = defaultdict(list)                                             # Ranking Correlation Metric 저장
    WDRDict = defaultdict(list)                                             # Warning Detection Rate 을 구하기 위한 토픽별 Fixed Warning 갯수 저장
       
    for trainLine in open(WARNING_RANK_PATH + 'TOP_RANK(5).csv'):
        
        if 'CategoryName' in trainLine:     continue
        
        trainTokenLine      = trainLine.split(',')
        
        if trainTokenLine[0] != tmpTopicNum:                            # Topic이 바뀌면, 다시 모든 변수 초기화
            categoryCount       = 0
            sumOfWeight         = 0
            sumOfFixnum         = 0
            testRankingList     = list()
            trainRankingList    = list()
        
        trainTopicNum       = trainTokenLine[0]
        trainCategoryName   = trainTokenLine[1]
        
        if not trainTopicNum in testDict.keys():                    continue           # test에서 파일의 갯수가 median이 넘는 토픽만 뽑았으므로 test에 없는 토픽이라면 스킵
                
        trainRankingList.append(float(trainTokenLine[3]))               # trainRaking 리스트에 train 랭킹을 순차적으로 쌓기
             
        testInfo = testDict[trainTopicNum][trainCategoryName]           # fixNum, Weight, Ranking 순
        testRankingList.append(float(testInfo[2]))                      # testRanking 리스트에 test 링킹을 순차적으로 쌓기
                
        sumOfWeight += float(testInfo[1])                               # weight 값 누적
        sumOfFixnum += float(testInfo[0])
        categoryCount += 1                                              # category 갯수 누적
        corrRank = pearsonr(trainRankingList, testRankingList)          # Ranking Pearson Correlation 구하기
        
        OUT_FILE.write(','.join(trainTokenLine[:-1]) + ',' + testInfo[1] + ',' + str(sumOfWeight) + ',' + str(sumOfWeight/categoryCount) + ',' + trainTokenLine[3].strip() + ',' + testInfo[2].strip() + ',' + str(corrRank[0]) + ',' + testInfo[0]+ ',' + str(sumOfFixnum) + '\n')
        
        tmpTopicNum         = trainTopicNum
        
        if categoryCount <= 256:                                         # 100개까지만 Average of Precision 기록하기
            AOPDict[trainTopicNum].append(sumOfWeight/categoryCount)
            RCDict[trainTopicNum].append(corrRank[0])
            WDRDict[trainTopicNum].append(sumOfFixnum)
    
    MetricsList = ['AOP', 'RC', 'WDR']
    
    for metric in MetricsList:                                                # Header 출력        
        for i in range(0, len(AOPDict)):        
            METRICS_FILE.write('Topic' + str(i) + ',')                        # Metric이 3개이므로 쉼표도 3개
        METRICS_FILE.write(metric + ',,')
        if metric == 'WDR':
            METRICS_FILE.write('AWDR')
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
            maxTotal = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # 토픽별 AOP 출력
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # 평균을 내기 위해 Precision 축적
                maxTotal += max(tmpMetricDict[str(topicIdx)])                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # 각 Metric의 모든 토픽의 평균값 저장
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic의 갯수로 나누면 평균
            
            maxAvg = maxTotal/(len(tmpMetricDict)-1) 
            if metric == 'WDR':
                METRICS_FILE.write( str( (avgResult/(len(tmpMetricDict)-1)) / maxAvg ) )            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

def getHWPSummary(project):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'TopicEvaluation/'
    WARNING_RANK_PATH       = PRIORITIZATION_PATH + 'WarningRank/'
    
    OUT_FILE = open(EVALUATION_PATH + 'HWP_SUMMARY.csv', 'w')
    METRICS_FILE = open(EVALUATION_PATH + 'HWP_METRIC_RESULT.csv', 'w')
    
    testDict = OrderedDict()
    for testLine in open(EVALUATION_PATH + 'HWP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.strip().split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Category 이름 = key, 나머지 fixNum, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = OrderedDict({tokenLine[1]: tokenLine[2:]})
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    trainInfoDict = OrderedDict()
    for trainLine in open(WARNING_RANK_PATH + 'HWP_RANK.csv'):
        
        if 'CategoryName' in trainLine:     continue
        
        tokenLine = trainLine.strip().split(',')
        
        trainInfoDict[tokenLine[0]] = tokenLine[1:]                     # Category Name을 Key로 하여, Weight, Ranking을 리스트로 저장
    
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
            
            testRankingList.append(float(testInfo[2]))                      # testRanking 리스트에 test 링킹을 순차적으로 쌓기
                    
            sumOfWeight += float(testInfo[1])                               # weight 값 누적
            sumOfFixnum += float(testInfo[0])
            categoryCount += 1                                              # category 갯수 누적
            corrRank = pearsonr(trainRankingList, testRankingList)          # Ranking Pearson Correlation 구하기
            
            OUT_FILE.write(str(topicNum) + ',' + wName + ',' + trainInfoDict[wName][0] + ',' + testInfo[1] + ',' + str(sumOfWeight) + ',' + str(sumOfWeight/categoryCount) + ',' + trainInfoDict[wName][1] + ',' + testInfo[2].strip() + ',' + str(corrRank[0]) + ',' + testInfo[0]+ ',' + str(sumOfFixnum) + '\n')
            
            if categoryCount <= 256:                                         # 100개까지만 Average of Precision 기록하기
                AOPDict[str(topicNum)].append(sumOfWeight/categoryCount)
                RCDict[str(topicNum)].append(corrRank[0])
                WDRDict[str(topicNum)].append(sumOfFixnum)
    
    MetricsList = ['AOP', 'RC', 'WDR']
    
    for metric in MetricsList:                                                # Header 출력        
        for i in range(0, len(AOPDict)):        
            METRICS_FILE.write('Topic' + str(i) + ',')                        # Metric이 3개이므로 쉼표도 3개
        METRICS_FILE.write(metric + ',,')
        if metric == 'WDR':
            METRICS_FILE.write('AWDR')
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
            maxTotal = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # 토픽별 AOP 출력
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # 평균을 내기 위해 Precision 축적
                maxTotal += max(tmpMetricDict[str(topicIdx)])                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # 각 Metric의 모든 토픽의 평균값 저장
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic의 갯수로 나누면 평균
            
            maxAvg = maxTotal/(len(tmpMetricDict)-1) 
            if metric == 'WDR':
                METRICS_FILE.write( str( (avgResult/(len(tmpMetricDict)-1)) / maxAvg ) )            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

def getTOOLSummary(project):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'TopicEvaluation/'
    WARNING_RANK_PATH       = PRIORITIZATION_PATH + 'WarningRank/'
    
    OUT_FILE = open(EVALUATION_PATH + 'TOOL_SUMMARY.csv', 'w')
    METRICS_FILE = open(EVALUATION_PATH + 'TOOL_METRIC_RESULT.csv', 'w')
    
    testDict = OrderedDict()
    for testLine in open(EVALUATION_PATH + 'TOP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.strip().split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Category 이름 = key, 나머지 fixNum, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = OrderedDict({tokenLine[1]: tokenLine[2:]})
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    trainInfoDict = OrderedDict()
    for trainLine in open(WARNING_RANK_PATH + 'TOOL_RANK.csv'):
        
        if 'CategoryName' in trainLine:     continue
        
        tokenLine = trainLine.strip().split(',')
        
        trainInfoDict[tokenLine[0]] = tokenLine[1:]                     # Category Name을 Key로 하여, Weight, Ranking을 리스트로 저장
    
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
            
            testRankingList.append(float(testInfo[2]))                      # testRanking 리스트에 test 링킹을 순차적으로 쌓기
                    
            sumOfWeight += float(testInfo[1])                               # weight 값 누적
            sumOfFixnum += float(testInfo[0])
            categoryCount += 1                                              # category 갯수 누적
            corrRank = pearsonr(trainRankingList, testRankingList)          # Ranking Pearson Correlation 구하기
            
            OUT_FILE.write(str(topicNum) + ',' + wName + ',' + trainInfoDict[wName][0] + ',' + testInfo[1] + ',' + str(sumOfWeight) + ',' + str(sumOfWeight/categoryCount) + ',' + trainInfoDict[wName][1] + ',' + testInfo[2].strip() + ',' + str(corrRank[0]) + ',' + testInfo[0]+ ',' + str(sumOfFixnum) + '\n')
            
            if categoryCount <= 256:                                         # 256개까지만 Average of Precision 기록하기
                AOPDict[str(topicNum)].append(sumOfWeight/categoryCount)
                RCDict[str(topicNum)].append(corrRank[0])
                WDRDict[str(topicNum)].append(sumOfFixnum)
    
    MetricsList = ['AOP', 'RC', 'WDR']
    
    for metric in MetricsList:                                                # Header 출력        
        for i in range(0, len(AOPDict)):        
            METRICS_FILE.write('Topic' + str(i) + ',')                        # Metric이 3개이므로 쉼표도 3개
        METRICS_FILE.write(metric + ',,')
        if metric == 'WDR':
            METRICS_FILE.write('AWDR')
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
            maxTotal = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # 토픽별 AOP 출력
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # 평균을 내기 위해 Precision 축적
                maxTotal += max(tmpMetricDict[str(topicIdx)])                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # 각 Metric의 모든 토픽의 평균값 저장
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic의 갯수로 나누면 평균
            
            maxAvg = maxTotal/(len(tmpMetricDict)-1) 
            if metric == 'WDR':
                METRICS_FILE.write( str( (avgResult/(len(tmpMetricDict)-1)) / maxAvg ) )            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

def getALTRanking(project, isRandom):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'   
    ALTEVALUATION_PATH      = PRIORITIZATION_PATH + 'ALTEvaluation/'
    
    if not isRandom:
        WEIGHT_FILE = ALTEVALUATION_PATH + 'ALT_WEIGHT.csv'
        OUT_FILE = open(ALTEVALUATION_PATH + 'ALT_RANK.csv', 'w')        
    else: 
        WEIGHT_FILE = ALTEVALUATION_PATH + 'ALT_RAND_WEIGHT.csv'
        OUT_FILE = open(ALTEVALUATION_PATH + 'ALT_RAND_RANK.csv', 'w')    
        
    WeightDict = dict()        
    for line in open(WEIGHT_FILE):        
        if 'CategoryName' in line:              continue
        
        tokenLine = line.split(',')
        weightValue = float(tokenLine[1])
        
        if weightValue == 0.0:                  # 0이면 아예 나타나지 않은 warning이므로 최고 값 부여
            weightValue = 999999.9
            
        WeightDict[tokenLine[0]] = weightValue
                
    RankDict = dict()
    sortedDict = dict()    
    reverse = rankdata(WeightDict.values()).astype(float)
#     reverse += 1
      
    idx = 0          
    for wName, wWeight in WeightDict.items():
        RankDict[wName] = reverse[idx]
        idx += 1
        
    sortedDict = OrderedDict(sorted(RankDict.items(), key=itemgetter(1,0)))
    
    OUT_FILE.write('CategoryName,Weight,Ranking\n')
    for wName, wRank in sortedDict.items():            
        OUT_FILE.write(wName + ',' + str(WeightDict[wName]) + ',' + str(wRank) + '\n')

def getALTSummary(project, isRandom):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'TopicEvaluation/'
    ALTEVALUATION_PATH      = PRIORITIZATION_PATH + 'ALTEvaluation/'
    
    # 결과 저장 디렉토리가 없으면 생성
    if not os.path.exists(ALTEVALUATION_PATH):
        os.makedirs(ALTEVALUATION_PATH)
    
    if not isRandom:
        OUT_FILE = open(ALTEVALUATION_PATH + 'ALT_SUMMARY.csv', 'w')
        METRICS_FILE = open(ALTEVALUATION_PATH + 'ALT_METRIC_RESULT.csv', 'w')
    else:
        OUT_FILE = open(ALTEVALUATION_PATH + 'RAND_SUMMARY.csv', 'w')
        METRICS_FILE = open(ALTEVALUATION_PATH + 'RAND_METRIC_RESULT.csv', 'w')
    
    testDict = OrderedDict()
    for testLine in open(EVALUATION_PATH + 'HWP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.strip().split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Topic 번호 = key, Category Name = Sub Key, Occurrence, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = OrderedDict({tokenLine[1]: tokenLine[2:]})
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    if not isRandom:
        RANK_FILE = ALTEVALUATION_PATH + 'ALT_RANK.csv'
    else:
        RANK_FILE = ALTEVALUATION_PATH + 'ALT_RAND_RANK.csv'
    
    trainInfoDict = OrderedDict()
    for trainLine in open(RANK_FILE):
        
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
        if metric == 'WDR':
            METRICS_FILE.write('AWDR')
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
            maxTotal = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # 토픽별 AOP 출력
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # 평균을 내기 위해 Precision 축적
                maxTotal += max(tmpMetricDict[str(topicIdx)])                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # 각 Metric의 모든 토픽의 평균값 저장
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic의 갯수로 나누면 평균
            
            maxAvg = maxTotal/(len(tmpMetricDict)-1) 
            if metric == 'WDR':
                METRICS_FILE.write( str( (avgResult/(len(tmpMetricDict)-1)) / maxAvg ) )            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

def getOptSummary(project):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    
    EVALUATION_PATH         = PRIORITIZATION_PATH + 'TopicEvaluation/'
    ALTEVALUATION_PATH      = PRIORITIZATION_PATH + 'ALTEvaluation/'
    
    # 결과 저장 디렉토리가 없으면 생성
    if not os.path.exists(ALTEVALUATION_PATH):
        os.makedirs(ALTEVALUATION_PATH)
    
    OUT_FILE = open(ALTEVALUATION_PATH + 'OPT_SUMMARY.csv', 'w')
    METRICS_FILE = open(ALTEVALUATION_PATH + 'OPT_METRIC_RESULT.csv', 'w')
    
    testDict = OrderedDict()
    for testLine in open(EVALUATION_PATH + 'HWP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.strip().split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Topic 번호 = key, Category Name = Sub Key, Occurrence, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = OrderedDict({tokenLine[1]: tokenLine[2:]})
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    AOPDict = defaultdict(list)                                         # Average of Precision Metric 저장
    RCDict  = defaultdict(list)                                         # Ranking Correlation Metric 저장
    WDRDict = defaultdict(list)                                         # Warning Detection Rate 을 구하기 위한 토픽별 Fixed Warning 갯수 저장
    
    
    for topicNum in range(0,len(testDict)):
        
        categoryCount       = 0
        sumOfWeight         = 0
        sumOfFixnum         = 0
        testRankingList     = list()
        trainRankingList    = list()
        tmpFixNumList       = list()       
        
        for wName, wInfo in testDict[str(topicNum)].items():           
            
            trainRankingList.append(float(wInfo[2]))                        # trainRaking 리스트에 train 랭킹을 순차적으로 쌓기            
            
            testInfo = testDict[str(topicNum)][wName]                       # 토픽 0부터 시작해서 Test 정보 가져오기                 
            
            testRankingList.append(float(testInfo[2]))                      # testRanking 리스트에 test 랭킹을 순차적으로 쌓기
                    
            sumOfWeight += float(testInfo[1])                               # weight 값 누적
            sumOfFixnum += float(testInfo[0])
            tmpFixNumList.append(int(testInfo[0]))
            
            categoryCount += 1                                              # category 갯수 누적
            corrRank = pearsonr(trainRankingList, testRankingList)          # Ranking Pearson Correlation 구하기
            
            OUT_FILE.write(str(topicNum) + ',' + wName + ',' + testInfo[1] + ',' + testInfo[1] + ',' + str(sumOfWeight) + ',' + str(sumOfWeight/categoryCount) + ',' + testInfo[2].strip() + ',' + testInfo[2].strip() + ',' + str(corrRank[0]) + ',' + testInfo[0]+ ',' + str(sumOfFixnum) + '\n')
            
            if categoryCount <= 256:                                         # n개까지 Average of Precision 기록하기
                AOPDict[str(topicNum)].append(sumOfWeight/categoryCount)
                RCDict[str(topicNum)].append(corrRank[0])
        
        tmpFixNumList.sort(reverse=True)
        
        tmpSumOfFixnum = 0
        for warnFixNum in tmpFixNumList:
            tmpSumOfFixnum += warnFixNum
            WDRDict[str(topicNum)].append(tmpSumOfFixnum)        
    
    MetricsList = ['AOP', 'RC', 'WDR']
    
    for metric in MetricsList:                                                # Header 출력        
        for i in range(0, len(AOPDict)):        
            METRICS_FILE.write('Topic' + str(i) + ',')                        # Metric이 3개이므로 쉼표도 3개
        METRICS_FILE.write(metric + ',,')
        if metric == 'WDR':
            METRICS_FILE.write('AWDR')
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
            maxTotal = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # 토픽별 AOP 출력
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # 평균을 내기 위해 Precision 축적
                maxTotal += max(tmpMetricDict[str(topicIdx)])                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # 각 Metric의 모든 토픽의 평균값 저장
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic의 갯수로 나누면 평균
            
            maxAvg = maxTotal/(len(tmpMetricDict)-1) 
            if metric == 'WDR':
                METRICS_FILE.write( str( (avgResult/(len(tmpMetricDict)-1)) / maxAvg ) )            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

def sumUpResult(project):
    
    PROJECT_PATH            = ROOT_PATH + project + '/'
    PRIORITIZATION_PATH     = PROJECT_PATH + 'PRIORITIZATION/'    

    ALTLineList = [line for line in open(PRIORITIZATION_PATH + 'ALTEvaluation/ALT_METRIC_RESULT.csv')]    
    HWPLineList = [line for line in open(PRIORITIZATION_PATH + 'TopicEvaluation/HWP_METRIC_RESULT.csv')]
    TOPLineList = [line for line in open(PRIORITIZATION_PATH + 'TopicEvaluation/TOP_METRICS_RESULT.csv')]
    TOOLLineList = [line for line in open(PRIORITIZATION_PATH + 'TopicEvaluation/TOOL_METRIC_RESULT.csv')]
    RANDLineList = [line for line in open(PRIORITIZATION_PATH + 'ALTEvaluation/RAND_METRIC_RESULT.csv')]
    OPTLineList = [line for line in open(PRIORITIZATION_PATH + 'ALTEvaluation/OPT_METRIC_RESULT.csv')]
        
    OUT_FILE = open(PRIORITIZATION_PATH + 'Evaluation_Result.csv', 'w')
    OUT_FILE.write('AOP-ALT,AOP-HWP,AOP-TOP,AOP-TOOL,AOP-RAND,AOP-OPT,,WDR-ALT,WDR-HWP,WDR-TOP,WDR-TOOL,WDR-RAND,WDR-OPT,,AWDR-ALT,AWDR-HWP,AWDR-TOP,AWDR-TOOL,AWDR-RAND,AWDR-OPT,,RC-ALT,RC-HWP,RC-TOP,RC-TOOL,RC-RAND,RC-OPT\n')                
    
    for index in range(1, len(ALTLineList)):
        OUT_FILE.write(ALTLineList[index].split(',')[5] + ',')
        OUT_FILE.write(HWPLineList[index].split(',')[5] + ',')
        OUT_FILE.write(TOPLineList[index].split(',')[5] + ',')
        OUT_FILE.write(TOOLLineList[index].split(',')[5] + ',')
        OUT_FILE.write(RANDLineList[index].split(',')[5] + ',')
        OUT_FILE.write(OPTLineList[index].split(',')[5] + ',,')
        
        OUT_FILE.write(ALTLineList[index].split(',')[19] + ',')
        OUT_FILE.write(HWPLineList[index].split(',')[19] + ',')
        OUT_FILE.write(TOPLineList[index].split(',')[19] + ',')
        OUT_FILE.write(TOOLLineList[index].split(',')[19] + ',')
        OUT_FILE.write(RANDLineList[index].split(',')[19] + ',')
        OUT_FILE.write(OPTLineList[index].split(',')[19] + ',,')
        
        OUT_FILE.write(ALTLineList[index].split(',')[21].strip() + ',')
        OUT_FILE.write(HWPLineList[index].split(',')[21].strip() + ',')
        OUT_FILE.write(TOPLineList[index].split(',')[21].strip() + ',')
        OUT_FILE.write(TOOLLineList[index].split(',')[21].strip() + ',')
        OUT_FILE.write(RANDLineList[index].split(',')[21].strip() + ',')
        OUT_FILE.write(OPTLineList[index].split(',')[21].strip() + ',,')
        
        OUT_FILE.write(ALTLineList[index].split(',')[12] + ',')
        OUT_FILE.write(HWPLineList[index].split(',')[12] + ',')
        OUT_FILE.write(TOPLineList[index].split(',')[12] + ',')
        OUT_FILE.write(TOOLLineList[index].split(',')[12] + ',')
        OUT_FILE.write(RANDLineList[index].split(',')[12] + ',')
        OUT_FILE.write(OPTLineList[index].split(',')[12] + '\n')

# 프로젝트 리스트
PROJECTS = ['bonita', 'cassandra', 'checkstyle', 'elasticsearch', 'flink', 'guava', 'guice', 'hadoop_git', 'itext-itextpdf', 'jackrabbit', 'jbpm', 'jclouds', 
            'jenkins', 'libgdx', 'mahout', 'maven_core', 'mylyn', 'neo4j', 'openmap', 'orientdb', 'pivot', 'titan', 'tomcat', 'wildfly', 'ant', 'drools', 'lucene_trunk']

for project in PROJECTS:
    print project + ' Project lifetime 결과 평가 중...'
     
    getTOPSummary(project)
    getHWPSummary(project)
    getTOOLSummary(project)
     
    getALTRanking(project, False)           # ALT weight로 랭킹 계산
    getALTRanking(project, True)            # Random weight로 랭킹 계산
    getALTSummary(project, False)           # ALT Rank로 평가
    getALTSummary(project, True)            # Random Rank로 평가
    getOptSummary(project)

    sumUpResult(project)