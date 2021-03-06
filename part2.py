import os
import random
import re

import numpy as np
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk

# regex to represent the tag < > around the ambiguous word
TAG_REGEX = re.compile(r'<[^>]+>')


# function to remove tags from a string
def removeTags(line: str):
    return TAG_REGEX.sub('', line)


class Example():
    """
    class which associate a sentence and a meaning number according to the dataset
    sentence : string of a sentence where the example word is used
    meaning : an integer which corresponds to the meaning number at the end of the example in the dataset
    """

    def __init__(self, sentence: str, meaning: int):
        self.sentence = sentence
        self.meaning = meaning


class Word():
    """
    class which parse a file to be understandable and usable by our program
    path : string of the path of the file
    word : string of the ambiguous word
    examples : list of Example objects
    meaningNumber : integer which represents amount of meaning associated with the word
    """

    def __init__(self, path: str):
        self.path = path
        self.word = self.getWordnameFromFilename()
        self.examples = []
        self.meaningNumber = -1
        self.parseFileToArray()

    def getWordnameFromFilename(self):
        """
        get the string of the word from the name of the file
        :return: the string of the word
        """
        filename = os.path.basename(self.path)
        filename = os.path.splitext(filename)
        word = filename[0].split('_')
        return word[0]

    def parseLineToExample(self, line: str):
        """
        parse each line inside an Example object
        :param line: string of a line from a file of the dataset
        :return: an Example Object of the line parsed
        """
        begining = line.index("\"")
        tempString = line[begining + 1:]
        meaningNumber = (int)(line[-2:-1])
        tempString = tempString[:-5]
        tempString = removeTags(tempString)
        return Example(tempString, meaningNumber)

    def parseFileToArray(self):
        """
        parse the whole file to a Word object
        :return: nothing
        """
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
    """
    compute an result array to represent the synsets disambiguation by the meaning inside the dataset
    :param path: string of the path of the file
    :return: the array of the synsets by meaning numbers
    """
    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    if len(wordSynsets) != 0:
        disambiguationArray = np.zeros((word.meaningNumber, len(wordSynsets)), dtype=int)
        i = 0
        for example in word.examples:
            i = i + 1
            syn = lesk(example.sentence.split(), word.word, None, wordSynsets)
            for j in range(0, len(wordSynsets)):
                if wordSynsets[j] == syn:
                    disambiguationArray[example.meaning - 1][j] = disambiguationArray[example.meaning - 1][j] + 1
        return disambiguationArray
    else:
        return None


def computeAverageAccuracy(path: str, printRelsult: bool = True):
    """
    Compute the average accuracy for a file
    :param path: path to a file associated to a word
    :param printRelsult: boolean to specify if you want to print the intermediate result
    :return: the percent accuracy
    """
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

            if printRelsult:
                print(f"M{index + 1} was disambiguated as:")
            for j in range(len(wordSynsets)):
                if printRelsult:
                    print(f"{counter[index][j]} times as the synset {wordSynsets[j]}")
            for j in range(0, len(wordSynsets)):
                if maximum == counter[index][j]:
                    if printRelsult:
                        print(f"M{index + 1} has an accuracy of {'{:2.2f}'.format(meaningAccuracy * 100)}" \
                              f"% corresponding to the synset {wordSynsets[j]}")
        totalAccuracy = totalAccuracy / len(counter)
        if printRelsult:
            print(
                f"\nThe word {word.word} has an average accuracy equals to {'{:2.2f}'.format(totalAccuracy * 100)}%\n")
        return totalAccuracy
    else:
        if printRelsult:
            print(f"The word {word.word} is not in the Wordnet database\n")
        return None


def getfileListFromDirectory(directoryPath: str):
    """
    get the list strings which represent the list of filename from a directory
    :param directoryPath: string of the path to the directory
    :return: a list of files path inside it
    """
    files = []
    for r, d, f in os.walk(directoryPath):
        for file in f:
            files.append(os.path.join(r, file))
    return files


def computeAcronymsAverageAccuracy(numberOfAcronyms: int, printintermediateResult: bool = False):
    """
    compute the average accuracy for files in the acronyms directory
    :param numberOfAcronyms: number of random acronyms selected
    :param printintermediateResult: boolean value to print intermediate result for each files
    :return: totalAccuracy: the percent of the disambiguation accuracy; errorCounter : the number of file that can't be computed (not in Wordnet)
    """
    directoryPath = "acronyms"
    files = set(getfileListFromDirectory(directoryPath))
    selectedFiles = random.sample(files, numberOfAcronyms)
    # print(f"samples : {selectedFiles}")
    errorCounter = 0
    totalAccuracy = 0
    for file in selectedFiles:
        # print(f"file : {file}")
        tempAccuracy = computeAverageAccuracy(file, printintermediateResult)
        if tempAccuracy == None:
            errorCounter = errorCounter + 1
        else:
            totalAccuracy = totalAccuracy + tempAccuracy
    totalAccuracy = totalAccuracy / (numberOfAcronyms - errorCounter)
    return totalAccuracy, errorCounter


def computeTermsAverageAccuracy(numberOfTerms: int, printintermediateResult: bool = False):
    """
    compute the average accuracy for files in the terms directory
    :param numberOfTerms: number of random terms selected
    :param printintermediateResult: boolean value to print intermediate result for each files
    :return: totalAccuracy: the percent of accuracy; errorCounter : the number of file that can't be computed (not in Wordnet)
    """
    directoryPath = "terms"
    files = set(getfileListFromDirectory(directoryPath))
    selectedFiles = random.sample(files, numberOfTerms)
    # print(f"samples : {selectedFiles}")
    errorCounter = 0
    totalAccuracy = 0
    for file in selectedFiles:
        # print(f"file : {file}")
        tempAccuracy = computeAverageAccuracy(file, printintermediateResult)
        if tempAccuracy == None:
            errorCounter = errorCounter + 1
        else:
            totalAccuracy = totalAccuracy + tempAccuracy
    totalAccuracy = totalAccuracy / (numberOfTerms - errorCounter)
    return totalAccuracy, errorCounter


numberOfElements = 10
acronymsAverage, acronymsError = computeAcronymsAverageAccuracy(numberOfElements)
print(
    f"for {numberOfElements} acronyms: {'{:2.2f}'.format(acronymsAverage * 100)}% considering {acronymsError} missing from the wordnet database")

termsAverage, termsError = computeTermsAverageAccuracy(numberOfElements)
print(
    f"for {numberOfElements} terms: {'{:2.2f}'.format(termsAverage * 100)}% considering {termsError} missing from the wordnet database")
