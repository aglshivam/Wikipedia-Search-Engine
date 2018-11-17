import re
from bisect import bisect
from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
from Stemmer import Stemmer
from math import log10
from operator import itemgetter
import timeit

secondaryIndex = [] #store secondary index
totalDoc = 0 # total number of pages in wikipedia dump
searchResult = dict(list()) #store the normal query search result
searchFieldResult = dict() #store the field query search result
docIdTitleMap = dict()


######################################################################################

def readDocTitle():
    '''
    read docId and it's corresponding title
    to display the result as a title
    '''
    global docIdTitleMap

    with open('/media/shivam/New Volume/testing/index/docTitle.txt', 'r') as infile:
    # with open('/home/shivam/WikiSearch/testing/index/docTitle.txt', 'r') as infile:
        for line in infile:
            docId, title = line.split(':',1)
            docIdTitleMap[docId] = title


def readtotalDoc():
    """
    store the total number of pages in global valiable
    written in the totalPage.txt, created will parsing the XML
    """
    global totalDoc
    with open('/media/shivam/New Volume/testing/index/totalPage.txt', 'r') as infile:
    # with open('/home/shivam/WikiSearch/testing/index/totalPage.txt', 'r') as infile:
        totalDoc = int(infile.read())


def readSecondaryIndex():
    '''
    read secondary index in dictionary
    '''
    global secondaryIndex
    with open('/media/shivam/New Volume/testing/index/secondary.txt', 'r') as secondary:
    # with open('/home/shivam/WikiSearch/testing/index/secondary.txt', 'r') as secondary:
        lines = secondary.readlines()
        for line in lines:
            secondaryIndex.append(line.split(':')[0])


def languageProcessing(queryTerm):
    """
    remove stem word
    perfom stemming
    :param queryTerm:
    :return: stemmed query word
    """
    #stop words removal
    # print(queryTerm)
    stop_word = set(stopwords.words('english'))
    queryTerm = [w for w in queryTerm if w not in stop_word]

    #stemming
    #use this stemmer later
    ps = Stemmer('porter')
    queryTerm = [ps.stemWord(w) for w in queryTerm]

    # ps = PorterStemmer()
    # queryTerm = [ps.stem(w) for w in queryTerm]
    return queryTerm


def readIndex(loc, word):
    '''
    read file loc.txt and search for posting of word
    if word not found return empty list else return the posting of the word
    '''

    indexFile = open('/media/shivam/New Volume/testing/index/' + str(loc) + '.txt', 'r')
    # indexFile = open('/home/shivam/WikiSearch/testing/index/' + str(loc) + '.txt', 'r')
    data = indexFile.read()
    matcher = re.search('^'+word + ':', data, re.M)
    queryData = []
    if (matcher): #word found
        startInd = matcher.start()
        endInd = data.find('\n', startInd + 1)
        queryData = data[startInd:endInd].split(':')[1].split('|') #posting for word
    return queryData

######################################################################################
#Field Query processing

def parseFieldQuery(query):
    """
    create a dictionary of tagName corresponding to words that needs to be search
    assumption after field tag there will be : without any spaces
    take field
    :param query:
    """
    # print('query', query)
    dict = {}
    curword = ''
    tagName = ''
    wordList = []
    for i in range(len(query)):
        # print(query[i])
        if query[i] == ':':
            curword = ''
            if len(tagName) > 0:
                tempList = list(wordList)
                wordList.clear()
                # print('templist', tempList)
                for w in tempList:
                    wordList.extend((' '.join(re.findall("\d+|[\w]+", w))).split())
                if tagName in dict:
                    dict[tagName] += list(wordList)
                else:
                    dict[tagName] = list(wordList)
                wordList = []
            tagName = query[i-1]
        elif query[i] == ' ':
            if len(curword) > 0:
                wordList.append(curword)
            curword = ''
        else:
            curword += query[i]
    if len(curword) > 0:
        wordList.append(curword)

    # print('dict',dict)
    if len(wordList) > 0:
        tempList = list(wordList)
        wordList.clear()
        for w in tempList:
            wordList.extend((' '.join(re.findall("\d+|[\w]+", w))).split())
        # wordList = [re.findall("\d+|[\w]+", w) for w in wordList]
        # print('wordList ',wordList)
        if tagName in dict:
            dict[tagName] += wordList
        else:
            dict[tagName] = wordList
    return dict


def readIndexForFieldQuery(tag, word):
    '''
    given word read the found the posting for that word
    :param tag:
    :param word:
    '''
    global secondaryIndex
    global totalDoc
    global searchFieldResult

    data = []
    loc = bisect(secondaryIndex, word)
    try:
        # print('loc',loc)
        if loc-1 > 0 and secondaryIndex[loc-1] == word:
            #it will be present in previous file as well
            data += readIndex(loc-1, word)
        #search in current file
        data += readIndex(loc, word)
        doc_count = len(data)
        # print('word', word)

        #calculate idf
        idf = log10(totalDoc/doc_count)

        for i in data:
            docId, entry = i.split('#')
            weighted_freq = 0
            x = entry.split('+')
            # print(x)
            for y in x:
                # print(y)
                tagName = y[0]
                frequency = int(y[1:])
                if tagName == tag:
                    weighted_freq += frequency * 10000
                else :
                    weighted_freq += frequency
            if docId in searchFieldResult:
                searchFieldResult[docId] += weighted_freq
            else:
                searchFieldResult[docId] = weighted_freq

            weighted_freq = searchFieldResult[docId]
            searchFieldResult[docId] = float(log10(1+weighted_freq)*float(idf))
    except:
        pass



def processFieldQueryResult():
    '''
    print result for field query
    '''
    global searchFieldResult

    resultSize = 10
    count = 0

    print('\n-----Results----------\n')
    global docIdTitleMap
    for k1,v1 in sorted(searchFieldResult.items(), key=itemgetter(1), reverse=True):
        print(str(count+1),'. ',k1, ' - ', docIdTitleMap[k1],sep='')
        count += 1
        if(count == resultSize):
            break

    searchFieldResult.clear()

def processFieldQuery(query):
    dictionary = parseFieldQuery(query) #tagname, word
    ranking = dict(list())
    # print('dictionary', dictionary)
    for key in dictionary:
        queryTerms = languageProcessing(dictionary[key])
        if len(queryTerms) > 0:
            # dictionary[key] = queryTerms
            for terms in queryTerms:
                if terms in ranking:
                    ranking[terms].append(key)
                else:
                    ranking[terms] = [key]

    # dictionary = {k: v for k, v in dictionary.items() if v is not ''}
    # print(ranking)

    for w in ranking:
        for tag in ranking[w] :
            readIndexForFieldQuery(tag, w)

    processFieldQueryResult()


######################################################################################
#Normal Query Processing

#given word read the found the posting for that word
def readIndexForQuery(word):
    global secondaryIndex
    global totalDoc
    global searchResult
    data = []
    loc = bisect(secondaryIndex, word)
    try:
        # print('loc',loc)
        if loc-1 > 0 and secondaryIndex[loc-1] == word:
            #it will be present in previous file as well
            data += readIndex(loc-1, word)
        #search in current file
        data += readIndex(loc, word)
        doc_count = len(data)
        # print('word', word)

        #calculate idf
        idf = log10(totalDoc/doc_count)
        for i in data:
            docId, entry = i.split('#')
            if docId in searchResult:
                searchResult[docId].append(entry +'_'+str(idf))
            else:
                searchResult[docId] = [entry+'_'+str(idf)]
        # print('dict', searchResult)
    except:
        pass


def processResult():
    global searchResult
    # print('search', searchResult)
    lenDict = dict(dict())

    for k in searchResult:
        weighted_freq = 0
        idf = 0
        n = len(searchResult[k])
        for x in searchResult[k]:
            x, idf = x.split('_')
            x = x.split('+')
            # print(x)
            for y in x:
                # print(y)
                tagName = y[0]
                frequency = int(y[1:])
                if tagName == 't':
                    weighted_freq += frequency*10000
                elif tagName == 'r' or tagName == 'e' or tagName == 'i' or tagName == 'c' :
                    weighted_freq += frequency*50
                elif tagName == 'b':
                    weighted_freq += frequency

        if n in lenDict:
            lenDict[n][k] = float(log10(1+weighted_freq)*float(idf))
        else:
            lenDict[n] = {k: float(log10(1+weighted_freq)*float(idf))}


    resultSize = 10
    count = 0

    print('\n-----Results----------\n')
    global docIdTitleMap
    for k, v in sorted(lenDict.items(), reverse=True):
        for k1,v1 in sorted(v.items(), key=itemgetter(1), reverse=True):
            print(str(count+1),'. ',k1, ' - ', docIdTitleMap[k1],sep='')
            count += 1
            if(count == resultSize):
                break
        if count == resultSize:
            break

    searchResult.clear()

def processNormalQuery(query):
    #tokenize based on the spaces
    re6 = re.compile(r'[\_]', re.DOTALL)
    query = re6.sub(' ', query)

    query = re.findall("\d+|[\w]+", str(query))
    # query = query.split()

    query = languageProcessing(query)

    # print('query-after language processing---', query)
    for word in query:
        readIndexForQuery(word)
    processResult()

######################################################################################

def processQuery(query):
    query = query.strip()
    query = query.casefold()
    if re.search('[tbicer]:', query[:2]): #field Query
        processFieldQuery(query)
    else:                                 #Normal Query
        processNormalQuery(query)

######################################################################################
#Main

readSecondaryIndex()
readtotalDoc()
readDocTitle()

while True:
    query = input("---Enter your query---\n")

    start = timeit.default_timer()
    processQuery(query)
    stop = timeit.default_timer()
    print('Time: ', stop - start)
    print('-----------------------------')