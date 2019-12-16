import os
import random
import re
import numpy as np

import nltk
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn

TAG_REGEX = re.compile(r'<[^>]+>')


def removeTags(line: str):
    return TAG_REGEX.sub('', line)


class Example():
    def __init__(self, sentence: str, meaning: int):
        self.sentence = sentence
        self.meaning = meaning


class Word():
    def __init__(self, path: str):
        self.path = path
        self.word = self.getWordnameFromFilename()
        self.examples = []
        self.meaningNumber = -1
        self.parseFileToArray()

    def getWordnameFromFilename(self):
        filename = os.path.basename(self.path)
        filename = os.path.splitext(filename)
        word = filename[0].split('_')
        return word[0]

    def parseLineToExample(self, line: str):
        begining = line.index("\"")
        tempString = line[begining + 1:]
        meaningNumber = (int)(line[-2:-1])
        tempString = tempString[:-5]
        tempString = removeTags(tempString)
        return Example(tempString, meaningNumber)

    def parseFileToArray(self):
        # open the file
        file = open(self.path, "r+")
        lines = file.readlines()

        # get the amount of meaning
        for l in lines:
            if re.match("(.*)@ATTRIBUTE class(.*)", l):
                self.meaningNumber = int(max([e for e in re.split("[^0-9]", l) if e != '']))
                break

        # parse example and add them to the examples list
        i = 0
        for l in lines:
            i = i + 1
            if i >= 8:
                tempString = l
                self.examples.append(self.parseLineToExample(l))
        file.close()


def computeCounterArray(path: str):
    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    if len(wordSynsets) != 0:
        disambiguationArray = np.zeros((word.meaningNumber, len(wordSynsets)), dtype=int)
        i = 0
        for example in word.examples:
            i = i + 1
            syn = lesk(example.sentence.split(), word.word, None, wordSynsets)
            for i in range(0, len(wordSynsets)):
                if wordSynsets[i] == syn:
                    disambiguationArray[example.meaning - 1][i] = disambiguationArray[example.meaning - 1][i] + 1
        return disambiguationArray
    else:
        return None


def computeAverageAccuracy(path: str):
    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    counter = computeCounterArray(path)
    totalAccuracy = 0
    index = -1
    if len(wordSynsets) != 0:
        for i in counter:
            index = index + 1
            maximum = max(i)
            total = sum(i)
            meaningAccuracy = maximum / total
            totalAccuracy = totalAccuracy + meaningAccuracy

            print(f"M{index + 1} was disambiguated as:")
            for j in range(len(wordSynsets)):
                print(f"{counter[index][j]} times as the synset {wordSynsets[j]}")
            for j in range(0, len(wordSynsets)):
                if maximum == counter[index][j]:
                    print(f"M{index + 1} has an accuracy of {'{:2.2f}'.format(meaningAccuracy * 100)}" \
                          f"% corresponding to the synset {wordSynsets[j]}")
        totalAccuracy = totalAccuracy / len(counter)
        print(f"\nThe word {word.word} has an average accuracy equals to {'{:2.2f}'.format(totalAccuracy * 100)}%\n")
        return totalAccuracy
    else:
        print(f"The word {word.word} is not in the Wordnet database\n")
        return None


def getfileListFromDirectory(directoryPath: str):
    files = []
    for r, d, f in os.walk(directoryPath):
        for file in f:
            files.append(os.path.join(r, file))
    return files


def computeAcronymsAverageAccuracy(numberOfAcronyms: int):
    directoryPath = "acronyms"
    files = set(getfileListFromDirectory(directoryPath))
    selectedFiles = random.sample(files, numberOfAcronyms)
    # print(f"samples : {selectedFiles}")
    errorCounter = 0
    totalAccuracy = 0
    for file in selectedFiles:
        # print(f"file : {file}")
        tempAccuracy = computeAverageAccuracy(file)
        if tempAccuracy == None:
            errorCounter = errorCounter + 1
        else:
            totalAccuracy = totalAccuracy + tempAccuracy
    totalAccuracy = totalAccuracy / (numberOfAcronyms - errorCounter)
    return totalAccuracy, errorCounter


def computeTermsAverageAccuracy(numberOfAcronyms: int):
    directoryPath = "terms"
    files = set(getfileListFromDirectory(directoryPath))
    selectedFiles = random.sample(files, numberOfAcronyms)
    # print(f"samples : {selectedFiles}")
    errorCounter = 0
    totalAccuracy = 0
    for file in selectedFiles:
        print(f"file : {file}")
        tempAccuracy = computeAverageAccuracy(file)
        if tempAccuracy == None:
            errorCounter = errorCounter + 1
        else:
            totalAccuracy = totalAccuracy + tempAccuracy
    totalAccuracy = totalAccuracy / (numberOfAcronyms - errorCounter)
    return totalAccuracy, errorCounter


numberOfElements = 10
acronymsAverage, acronymsError = computeAcronymsAverageAccuracy(numberOfElements)
print(
    f"for {numberOfElements} acronyms: {'{:2.2f}'.format(acronymsAverage * 100)}% considering {acronymsError} missing from the wordnet database")
# termsAverage, termsError = computeTermsAverageAccuracy(numberOfElements)
# print(f"for {numberOfElements} terms: {'{:2.2f}'.format(termsAverage * 100)}% considering {termsError} missing from the wordnet database")


# print(f"last result : {'{:2.2f}'.format(computeTermsAverageAccuracy(50) * 100)}%")
# computeAverageAccuracy("acronyms/US_pmids_tagged.arff")
