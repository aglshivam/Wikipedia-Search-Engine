import glob
from heapq import heappush,heappop

'''
posting structure 
term:docId#tagVal+tagVal|docId#tagVal
'''

globalDict = dict(list())
fileNames = glob.glob("/media/shivam/New Volume/testing/dumpfile/*")
# fileNames = glob.glob("/home/shivam/WikiSearch/testing/dumpfile/*")
fileCount = len(fileNames)          #number of files
filePointer = dict()                #file pointers
processedFiles = [0]*len(fileNames) #flag for processed file
heapList = []                       #heap list
fileRowData = dict()  #current data read from file
words = dict()
total = 0
chunkSize = 70000  #number of terms to write in the file at a time
indexFileCount = 0
secondaryIndex = dict()

def writePrimaryIndex():
    '''
    Create primary index
    '''
    global indexFileCount
    global globalDict

    firstWord = True
    indexFileCount += 1
    file = open("/media/shivam/New Volume/testing/index1/"+str(indexFileCount)+".txt", 'w')
    # file = open("/home/shivam/WikiSearch/testing/index/"+str(indexFileCount)+".txt", 'w')

    for i in sorted(globalDict):
        if firstWord:
            print(i, indexFileCount)
            if i not in secondaryIndex:
                secondaryIndex[i] = indexFileCount
            else:
                print('Collision found ',i, ' prev ', secondaryIndex[i])
            firstWord = False
        # toWrite = i+":"+globalDict[i]
        toWrite = []
        # toWrite = i+":"
        toWrite.append(i+':')
        # file.write(toWrite)
        first = True
        # print(i, globalDict[i])
        for w in globalDict[i]:
            if first:
                # file.write(w)
                toWrite.append(w)
                first = False
            else:
                # file.write('|'+w)
                toWrite.append('|'+w)
        # file.write(toWrite+"\n")
        file.write(''.join(toWrite)+"\n")


def writeSecondaryIndex():
    '''
    create seconday index
    for each primary index file first term will be entry for the secondary index
    '''
    global secondaryIndex
    file = open('/media/shivam/New Volume/testing/index1/secondary.txt', 'w')
    # file = open('/home/shivam/WikiSearch/testing/index/secondary.txt', 'w')

    for i in sorted(secondaryIndex):
        toWrite = i+':'+str(secondaryIndex[i])
        file.write(toWrite+'\n')


for i in range(fileCount):
    filePointer[i] = open(fileNames[i], 'r') #open all the files
    processedFiles[i] = 1 #set flag
    fileRowData[i] = filePointer[i].readline() #read first line of each file
    words[i] = fileRowData[i].split(':') #split term and it's posting
    #words[i] is a list of [term, posting]
    if str(words[i][0]) not in heapList: #if word is not in the heap push it
        heappush(heapList, str(words[i][0]))


while True:
    #if all the files are processed then break
    if processedFiles.count(0) == fileCount:
        break

    total += 1
    word = str(heappop(heapList)) #extract top(smallest word) from heap
    for i in range(fileCount):
        if processedFiles[i] and words[i][0] == word: #word belongs to this file
            if word in globalDict: #add posting to the dictionary
                # globalDict[word] += '|'+ words[i][1][:-1] #to escape newline
                globalDict[word].append(words[i][1][:-1]) #to escape newline
            else:
                globalDict[word] = [words[i][1][:-1]] #to escape newline

            if total >= chunkSize: #write primary index
                total = 0
                writePrimaryIndex()
                globalDict.clear()  #clear it

            fileRowData[i] = filePointer[i].readline() #read next line

            if(fileRowData[i]):
                words[i] = fileRowData[i].split(':')
                if str(words[i][0]) not in heapList:
                    heappush(heapList, str(words[i][0]))
            else:
                processedFiles[i] = 0
                filePointer[i].close()
                # os.remove(fileNames[i])


writePrimaryIndex() # write last processed chunk of primary index
writeSecondaryIndex() #create secondary index

