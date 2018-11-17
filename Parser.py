import re
from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
from Stemmer import Stemmer



# tokenizer
def tokenizer(sentence):
    # tokens = nltk.word_tokenize(str(sentence))
    # return tokens
    return re.findall("\d+|[\w]+", str(sentence))


# case folding
def casefolder(tokens):
    # tokens = [e.casefold() for e in tokens]
    return tokens.casefold()


# stop word removal
def stopWordRemove(tokens):
    stop_word = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_word]
    return tokens


# stemming
def stemmer(tokens):
    # ps = PorterStemmer()
    # tokens = [ps.stem(w) for w in tokens]

    ps = Stemmer('porter')
    tokens = [ps.stemWord(w) for w in tokens]
    return tokens

def parseCSS(input):
    re2 = re.compile('{\|(.*?)\|}', re.DOTALL)
    re3 = re.compile(r'\[\[file:(.*?)\]\]', re.DOTALL)
    re4 = re.compile(r'{{v?cite(.*?)}}', re.DOTALL)
    re5 = re.compile(r'<(.*?)>', re.DOTALL)
    re6 = re.compile(r'[\_]', re.DOTALL)

    input = re2.sub(' ', input)
    input = re3.sub(' ', input)
    input = re4.sub(' ', input)
    input = re5.sub(' ', input)
    input = re6.sub(' ', input)

    return input

def driver(input):
    input = tokenizer(input)
    input = stopWordRemove(input)
    input = stemmer(input)
    # input.sort()
    dictionary = {}
    for w in input:
        if w in dictionary:
            dictionary[w] += 1
        else:
            dictionary[w] = 1
    return dictionary


# extract category from the text body
def extractCategory(body_text):
    o = re.compile(r'(\[\[category(.*?)\]\]\n\n)', re.DOTALL)
    o1 = re.compile(r'\[\[category:(.*?)\]\]')
    cat = o.search(body_text)

    if not cat:
        return body_text, ''
    cat1 = cat.group(0)
    body_text = body_text.replace(cat1, ' ')
    cat2 = cat.group(2)
    return body_text, cat2


# extract infobox from the body text
def extractInfoBox(body_text):
    o = re.compile('({{infobox(.*?)}}\n\n)', re.DOTALL)
    o1 = re.compile('{{infobox(.*?)}}', re.DOTALL)
    info = o.search(body_text)
    info2 = ''
    while info:
        info1 = info.group(0)
        body_text = body_text.replace(info1, ' ')
        info2 += info1
        info = o.search(body_text)
    return body_text, info2

# extract external links from the text body
def externalLinks(body_text):

    o = re.compile(r'(==\s?external links\s?==(.*?)\n\n)', re.DOTALL)
    o1 = re.compile('\[(.*?)\]', re.DOTALL)
    links = o.search(body_text)

    if not links:
        return body_text, ''
    links1 = links.group(0)
    body_text = body_text.replace(links1, ' ')
    links2 = links.group(2)
    return body_text, links2


# extract references from the body text
def extractRefernces(body_text):
    o = re.compile(r'(==\s?references\s?==(.*?)}}\n\n)', re.DOTALL)
    o1 = re.compile(r'==\s?references\s?==(.*?)}}', re.DOTALL)
    ref = o.search(body_text)
    ref1 = ''
    ref2 = ''
    if not ref:
        return body_text, ''
    ref1 = ref.group(0)
    body_text = body_text.replace(ref1, ' ')
    ref2 = ref.group(2)
    body_text = body_text.replace(ref1, ' ')
    return body_text, ref2

# separate out all the fields from the texts
def fieldSeparator(body_text):
    body = category = infobox = external = reference = []

    body_text = casefolder(body_text)
    body_text = parseCSS(body_text)
    # extract category from the text body
    body_text, category = extractCategory(body_text)
    # body_text = body_text.replace(category, ' ')

    # extract infobox from the text body
    body_text, infobox = extractInfoBox(body_text)
    # body_text = body_text.replace(infobox, ' ')

    # extract external links from body text
    body_text, external = externalLinks(body_text)
    # body_text = body_text.replace(external, ' ')

    # extract reference from the text body
    body_text, reference = extractRefernces(body_text)
    # body_text = body_text.replace(reference, ' ')

    return body_text, category, infobox, external, reference
