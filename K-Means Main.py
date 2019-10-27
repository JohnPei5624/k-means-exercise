## Yuanyuan John Pei
## K-Means Clustering Process
## run on python 3.5

import pandas as pd
import numpy as np
import os


fileInputName = 'supermarket_weekly_customer.csv'
fileOutputName = 'supermarket_weekly_customer_temp.csv'

# Calculating Center (average) of Each Group
def group_center(customerFrame):
    groupMean = {}
    for group in range(numberGroups):
        customerFrameTemp = customerFrame[headList[3:]]
        customerFrameTemp = customerFrameTemp[customerFrame.cluster == group+1]
        groupMean[group+1] = customerFrameTemp.mean().tolist()
    return groupMean


# For each record: Distance to the center of every group
# Calculated by squre root of sum of squre: (a^2 + b^2 + c^2 ... n^2)^0.5
def distance_to_centers(customerFrame, groupMean):
    distFrame = pd.DataFrame()
    for group in groupMean:
        meanSeries = pd.DataFrame([groupMean[group]], columns=headList[3:])
        # Cast a list to a row in dataframe: put extra square brackets outside the list
        # https://stackoverflow.com/questions/42202872/how-to-convert-list-to-row-dataframe-with-pandas
        customerFrameTemp = customerFrame[headList[3:]] 
        customerFrameTemp = pd.DataFrame(customerFrameTemp.values - meanSeries.values, columns=customerFrameTemp.columns)
        # Table minus row (for each row)
        # https://stackoverflow.com/questions/22093471/pandas-subtract-dataframe-with-a-row-from-another-dataframe
        for attr in headList[3:]:
            customerFrameTemp[attr] = customerFrameTemp[attr] ** 2
        '''
        print('\n')
        print(group)
        print(customerFrameTemp)
        '''
        distFrame[group] = customerFrameTemp.apply(lambda x: x.sum(), axis=1)
    return distFrame





# User custom input: number of clusters
numberGroups = ''
while numberGroups == '': 
    numberGroups = input('Please enter the number of clusters:\n')
    try:
        numberGroups = int(numberGroups)
        if numberGroups > 10 or numberGroups < 1:
            raise IndexError('The number must be greater than zero and less than ten')
    except:
        numberGroups = ''
        print('Only integer accepted. Min 1, Max 10.')

# User custom input: maximum iteration
maxIter = ''
while maxIter == '':
    maxIter = input('Please set the maximum iteration:\n')
    try:
        maxIter = int(maxIter)
        if maxIter > 100 or maxIter < 5:
            raise IndexError('The number must be greater than five and less than a hundred')
    except:
        maxIter = ''
        print('Only integer accepted. Min 5, Max 100.')

# User custom input: threshold
threshold = ''
while threshold == '':
    threshold = input('Please set the threshold of convergence percentage (50%-99%):\n')
    try:
        threshold = float(threshold)
        if threshold > 99 or threshold < 50:
            raise IndexError('The number must be greater than 50 and less than 99')
    except:
        threshold = ''
        print('Only numbers accepted. Min 50, Max 99.')



        

# Data import
customerFrame = pd.read_csv(fileInputName)
print('\n')
print('Data Summary:')
print(customerFrame.describe())

# Attributes reading
fileInput = open(fileInputName, 'r', encoding = 'utf8')
head = fileInput.readline().replace('\n','')
headList = head.split(',')
inputList = headList
sampleVaule = fileInput.readline().replace('\n','')
sampleVauleList = sampleVaule.split(',')
fileInput.close()
'''
# Which attributes are float? Only float attributes can be made input of clustering algorythm
# Input: 1
# Non-input: 0
typeList = []
for col in range(len(headList)):
    try:
        sampleVauleList[col] = float(sampleVauleList[col])
        if headList[col] == 'id':
            raise TypeError('Non-input for clustering')
    except:
        typeList.append(0)
    else:
        typeList.append(1)

for col in range(len(headList)):
    if typeList[col] == 0:
        inputList.remove(headList[col]) # This line of code kept getting errors and I couldn't figure out why
print(inputList)


customerFrame = customerFrame.set_index(['id'])
'''
print('\n')
print('First 5 rows of sample data:')
print(customerFrame[0:5])

# Add new column: Arbitrary Starting Point, randomly assign clusters
idList = []
for i in range(1000):
    idList.append(i+1)
clusterColumn = pd.DataFrame({'id': idList, 'cluster': np.random.randint(1,numberGroups+1,1000)})
customerFrame = pd.merge(customerFrame, clusterColumn, on='id')

convergePerc = 0
count = 0
while convergePerc < threshold:
    count += 1

    # Calculating Center (average) of Each Group
    groupMean = group_center(customerFrame)

    # For each record: Distance to the center of every group
    # Calculated by squre root of sum of squre: (a^2 + b^2 + c^2 ... n^2)^0.5
    distFrame = distance_to_centers(customerFrame, groupMean)

    # For each record: Which cluster does it belong? Which center is the closest to it?
    # The record should be assigned to this new cluster
    closestGroup = distFrame.idxmax(axis=1, skipna=True).tolist()

    # Assigning each row to a new cluster
    clusterColumnNew = pd.DataFrame({'id': idList, 'new_cluster':closestGroup})
    customerFrame = pd.merge(customerFrame, clusterColumnNew, on='id')

    # For each row: Judge whether the cluster changed
    customerFrame['convergence'] = customerFrame['cluster'] == customerFrame['new_cluster'] # will return True or False

    # Check convergence status: if it meets the threshold
    converge = customerFrame[customerFrame['convergence']==True].count()['id']
    convergePerc = converge / 1000

    # Drop columns out of date
    del customerFrame['cluster']
    del customerFrame['convergence']
    customerFrame = customerFrame.rename(index=str, columns={'new_cluster': 'cluster'})

    # Now the customerFrame is ready for the next iteration!
    print('Iteration',str(count),'is completed.')

    if count >= maxIter:
        break

# Output to file
customerFrame.to_csv(fileOutputName)

os.remove(fileInputName)
os.rename(fileOutputName,fileInputName)

