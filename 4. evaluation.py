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
    
    # ��� ���� ���丮�� ������ ����
    if not os.path.exists(ALTEVALUATION_PATH):
        os.makedirs(ALTEVALUATION_PATH)
    
    OUT_FILE = open(ALTEVALUATION_PATH + 'ALT_SUMMARY.csv', 'w')
    METRICS_FILE = open(ALTEVALUATION_PATH + 'ALT_METRIC_RESULT.csv', 'w')
    
    testDict = OrderedDict()
    for testLine in open(EVALUATION_PATH + 'HWP_RANK(5).csv'):
        
        if 'CategoryName' in testLine:     continue
        
        tokenLine = testLine.strip().split(',')        
        
        if testDict.has_key(tokenLine[0]):
            testDict[tokenLine[0]][tokenLine[1]] = tokenLine[2:]          # Topic ��ȣ = key, Category Name = Sub Key, Occurrence, Weight, Ranking = Value
        else:
            testDict[tokenLine[0]] = OrderedDict({tokenLine[1]: tokenLine[2:]})
    
    OUT_FILE.write('Topic,CategoryName,Train_Weight,Test_Weight,Sum_Precision,Avg_Precision,Train_Rank,Test_Rank,Rank_Corr,Occurrences,Sum_Occur\n')
    
    trainInfoDict = OrderedDict()
    for trainLine in open(ALTEVALUATION_PATH + 'ALT_RANK.csv'):
        
        if 'CategoryName' in trainLine:     continue
        
        tokenLine = trainLine.strip().split(',')
        
        trainInfoDict[tokenLine[0]] = tokenLine[1:]                     # CategoryName�� Key�� �Ͽ�, Weight, Ranking�� ����Ʈ�� ����
    
    AOPDict = defaultdict(list)                                         # Average of Precision Metric ����
    RCDict  = defaultdict(list)                                         # Ranking Correlation Metric ����
    WDRDict = defaultdict(list)                                         # Warning Detection Rate �� ���ϱ� ���� ���Ⱥ� Fixed Warning ���� ����
    
    for topicNum in range(0,len(testDict)):
        
        categoryCount       = 0
        sumOfWeight         = 0
        sumOfFixnum         = 0
        testRankingList     = list()
        trainRankingList    = list()       
        
        for wName, wInfo in trainInfoDict.items():           
            
            trainRankingList.append(float(wInfo[1]))                        # trainRaking ����Ʈ�� train ��ŷ�� ���������� �ױ�            
            
            testInfo = testDict[str(topicNum)][wName]                       # ���� 0���� �����ؼ� Test ���� ��������                 
            
            testRankingList.append(float(testInfo[2]))                      # testRanking ����Ʈ�� test ��ŷ�� ���������� �ױ�
                    
            sumOfWeight += float(testInfo[1])                               # weight �� ����
            sumOfFixnum += float(testInfo[0])
            categoryCount += 1                                              # category ���� ����
            corrRank = pearsonr(trainRankingList, testRankingList)          # Ranking Pearson Correlation ���ϱ�
            
            OUT_FILE.write(str(topicNum) + ',' + wName + ',' + trainInfoDict[wName][0] + ',' + testInfo[1] + ',' + str(sumOfWeight) + ',' + str(sumOfWeight/categoryCount) + ',' + trainInfoDict[wName][1] + ',' + testInfo[2].strip() + ',' + str(corrRank[0]) + ',' + testInfo[0]+ ',' + str(sumOfFixnum) + '\n')
            
            if categoryCount <= 256:                                         # n������ Average of Precision ����ϱ�
                AOPDict[str(topicNum)].append(sumOfWeight/categoryCount)
                RCDict[str(topicNum)].append(corrRank[0])
                WDRDict[str(topicNum)].append(sumOfFixnum)
    
    MetricsList = ['AOP', 'RC', 'WDR']
    
    for metric in MetricsList:                                                # Header ���        
        for i in range(0, len(AOPDict)):        
            METRICS_FILE.write('Topic' + str(i) + ',')                        # Metric�� 3���̹Ƿ� ��ǥ�� 3��
        METRICS_FILE.write(metric + ',,')
    METRICS_FILE.write('\n')
    
    MetricAvgList = defaultdict(list)                                           # �� Metric�� ��� ������ ��հ� ����        
    Idx = 0
    while Idx < len(AOPDict['0']): 
        
        for metric in MetricsList:                                                  # �� Metric ���
        
            tmpMetricDict = defaultdict(list)       
            if metric == 'AOP':     tmpMetricDict = AOPDict                         # �� metric ������ ���� metric ���� ��������                 
            elif metric == 'RC':    tmpMetricDict = RCDict
            else:                   tmpMetricDict = WDRDict

            topicIdx = 0
            avgResult = 0.0            
            while topicIdx < len(tmpMetricDict[str(topicIdx)]):
                METRICS_FILE.write(str(tmpMetricDict[str(topicIdx)][Idx]) + ',')       # ���Ⱥ� AOP ���
                avgResult += tmpMetricDict[str(topicIdx)][Idx]                         # ����� ���� ���� Precision ����                
                topicIdx += 1
            
            MetricAvgList[metric].append(avgResult/(len(tmpMetricDict)-1))             # �� Metric�� ��� ������ ��հ� ����
            METRICS_FILE.write(str(avgResult/(len(tmpMetricDict)-1)) + ',,')           # Topic�� ������ ������ ���            
            
        Idx += 1
    
        METRICS_FILE.write('\n')
    
    return MetricAvgList

# ������Ʈ ����Ʈ
GIT_PROJECTS = ['bonita']

for project in GIT_PROJECTS:
    getALTSummary(project)