import xml.sax
import sys
from Parser import driver, fieldSeparator
import collections
# import timeit

globalDic = {}
idTitleMap = dict()
totalPageCount = 0

# t : title          0
# b : body text      1
# c : category       2
# i : infobox        3
# e : external links 4
# r : references     5

# merge the local dictionary processedText with global dictionary
# id is document id
def mergeGlobalDict(id, processedText):
    global globalDic
    for w in processedText:
        lt = processedText[w]
        tempDict = {}
        if w in globalDic:
            tempDict = globalDic[w]
        tempDict[id] = lt
        globalDic[w] = tempDict


# combine and make local dictionary using title and fields of the text
def mergePageData(title, text, category, infobox, external, references):
    returnDict = {}

    # title
    for w in title:
        if w in returnDict:
            lt = returnDict[w]
            lt[0] += 1
            returnDict[w] = lt
        else:
            returnDict[w] = [1, 0, 0, 0, 0, 0]

    # body text
    for w in text:
        if w in returnDict:
            lt = returnDict[w]
            lt[1] += 1
            returnDict[w] = lt
        else:
            returnDict[w] = [0, 1, 0, 0, 0, 0]

    # category
    for w in category:
        if w in returnDict:
            lt = returnDict[w]
            lt[2] += 1
            returnDict[w] = lt
        else:
            returnDict[w] = [0, 0, 1, 0, 0, 0]

    # infobox
    for w in infobox:
        if w in returnDict:
            lt = returnDict[w]
            lt[3] += 1
            returnDict[w] = lt
        else:
            returnDict[w] = [0, 0, 0, 1, 0, 0]

    # external links
    for w in external:
        if w in returnDict:
            lt = returnDict[w]
            lt[4] += 1
            returnDict[w] = lt
        else:
            returnDict[w] = [0, 0, 0, 0, 1, 0]

    # references
    for w in references:
        if w in returnDict:
            lt = returnDict[w]
            lt[5] += 1
            returnDict[w] = lt
        else:
            returnDict[w] = [0, 0, 0, 0, 0, 1]
    return returnDict


class WikiHandler(xml.sax.ContentHandler):
    flag1 = 0
    global globalDic
    global idTitleMap
    # count = 0
    def __init(sefl):
        self.title = ""
        self.id = ""
        self.currentdata = ""
        self.text = ""

    def startElement(self, tag, attributes):
        self.currentdata = tag
        if tag == "page":
            # print("page")
            WikiHandler.flag1 = 1
            self.text = ""
            self.title = ""

    def characters(self, content):
        if self.currentdata == "title":
            self.title += content
        elif self.currentdata == "id" and self.flag1 == 1:
            self.id = content
        elif self.currentdata == "text":
            self.text += content

    def endElement(self, tag):
        if self.currentdata == "id" and WikiHandler.flag1 == 1:
            WikiHandler.flag1 = 0
        elif self.currentdata == "text":

            idTitleMap[self.id] = self.title

            title = str(self.title.encode('ascii', errors='ignore'))
            title = title.casefold()
            title = driver(title)

            body, category, infobox, external, reference = fieldSeparator(self.text)

            body = str(body.encode('ascii',errors='ignore'))
            category = str(category.encode('ascii',errors='ignore'))
            infobox = str(infobox.encode('ascii',errors='ignore'))
            external = str(external.encode('ascii',errors='ignore'))
            reference = str(reference.encode('ascii',errors='ignore'))

            body = driver(body)
            category = driver(category)
            infobox = driver(infobox)
            external = driver(external)
            reference = driver(reference)

            # title, body, category, infobox, external links, references
            dict = mergePageData(title, body, category, infobox, external, reference)

            # 3 param global dict, docid, processedtext
            # WikiHandler.count += 1
            mergeGlobalDict(self.id, dict)

            if int(self.id)%5000 == 0:
                writeindex(self.id)
                globalDic.clear()
                idTitleMap.clear()
            global totalPageCount
            totalPageCount += 1

        self.currentdata = ""


def writeindex(docid):
    file = '/media/shivam/New Volume/testing/dumpfile/'+str(docid)
    # file = '/home/shivam/WikiSearch/testing/dumpfile/'+str(docid)
    global globalDic
    # file = '/home/shivam/WikiSearch/indexfile'
    with open(file, "a") as outfile:
        for k, v in sorted(globalDic.items()):
            toWrite = []
            # res = k + ":" #term
            toWrite.append(k+':')
            for k1, lt in sorted(v.items()):
                # res += str(k1) +'#' #docid
                res = str(k1) +'#' #docid
                if lt[0] > 0:  # title
                    res += "t" + str(lt[0]) +'+'
                if lt[1] > 0:  # body text
                    res += "b" + str(lt[1]) +'+'
                if lt[2] > 0:  # category
                    res += "c" + str(lt[2]) +'+'
                if lt[3] > 0:  # infobox
                    res += "i" + str(lt[3]) +'+'
                if lt[4] > 0:  # external links
                    res += "e" + str(lt[4]) +'+'
                if lt[5] > 0:  # references
                    res += "r" + str(lt[5]) +'+'
                res = res[:-1]
                res +='|'
                toWrite.append(res)
            res = ''.join(toWrite)
            outfile.write(res[:-1] + '\n')
    outfile.close()

    global idTitleMap
    toWrite = []
    for k in idTitleMap:
        toWrite.append(k + ':' + idTitleMap[k] + '\n')
    toWrite = ''.join(toWrite)
    with open('/media/shivam/New Volume/testing/index/docTitle.txt', 'a') as outfile:
    # with open('/home/shivam/WikiSearch/testing/index/docTitle.txt', 'a') as outfile:
            outfile.write(toWrite)


if (__name__ == "__main__"):
    # sys.setdefaultencoding('utf8')
    wikiDump = sys.argv[1]
    # folder = sys.argv[2]

    parser = xml.sax.make_parser()

    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = WikiHandler()
    parser.setContentHandler(Handler)
    # parser.parse("/home/shivam/WikiSearch/wiki-search-small.xml")
    parser.parse(wikiDump)

    if len(globalDic) > 0:
        writeindex(len(globalDic))

    with open('/media/shivam/New Volume/testing/index/totalPage.txt','w') as outfile:
    # with open('/home/shivam/WikiSearch/testing/index/totalPage.txt', 'w') as outfile:
        outfile.write(str(totalPageCount))
        outfile.close()
