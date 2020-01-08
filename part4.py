import os
import re

from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim

import numpy as np
from nltk.corpus import wordnet as wn
import time

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


def computeCounterArray(path: str, algorithm=l.original_lesk, simOption: str = None):
    """
    compute an result array to represent the synsets disambiguation by the meaning inside the dataset
    :param path: string of the path of the file
    :param algorithm: the name of the function's algorithm
    :param simOption: option for the maxsim algorithm
    :return: the array of the synsets by meaning numbers
    """

    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    if len(wordSynsets) != 0:
        disambiguationArray = np.zeros((word.meaningNumber, len(wordSynsets)), dtype=int)
        noneCounter = 0
        i = 0
        for example in word.examples:
            # print(f"example {example.sentence}")
            i = i + 1
            if simOption == None:
                syn = algorithm(example.sentence, word.word)
            elif simOption == "path":
                syn = maxsim(example.sentence, word.word, option="path")
            elif simOption == "resnik":
                syn = maxsim(example.sentence, word.word, option="resnik")
            # print(f"syn type : {type(syn)}/ value : {syn}")
            if syn is not None:
                for j in range(0, len(wordSynsets)):
                    # print(f"word type : {type(wordSynsets[j])}/ value : {wordSynsets[j]}")
                    if wordSynsets[j] == syn:
                        disambiguationArray[example.meaning - 1][j] = disambiguationArray[example.meaning - 1][j] + 1
            else:
                noneCounter = noneCounter + 1
                # print(example.sentence)
        # print(f"NoneCounter : {noneCounter}")
        return disambiguationArray
    else:
        return None


def computeAverageAccuracy(path: str, printRelsult: bool = True, algorithm=l.original_lesk, simOption: str = None):
    """
    Compute the average accuracy for a file
    :param path: path to a file associated to a word
    :param printRelsult: boolean to specify if you want to print the intermediate result
    :param algorithm: the name of the function's algorithm
    :param simOption: option for the maxsim algorithm
    :return: the percent of the disambiguation accuracy
    """

    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    counter = computeCounterArray(path, algorithm, simOption)
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


def computeTotalAverageAccuracy(listOfFiles, printintermediateResult: bool = False, algorithm=l.original_lesk,
                                simOption: str = None):
    """
    Compute the average accuracy and the number or errors according to a list of files
    WARNING : do not set simOption with you are not using similarity algorithms
    :param listOfFiles: list of string of paths
    :param printintermediateResult: boolean to specify if you want to print the intermediate result
    :param algorithm: the name of the function's algorithm
    :param simOption: option for the maxsim algorithm
    :return: totalAccuracy: the mean percent of the disambiguation accuracy; errorCounter : the number of file that can't be computed (not in Wordnet)
    """
    files = listOfFiles
    errorCounter = 0
    totalAccuracy = 0
    for file in files:
        print(f"file : {file}")
        tempAccuracy = computeAverageAccuracy(file, printintermediateResult, algorithm, simOption)
        if tempAccuracy == None:
            errorCounter = errorCounter + 1
        else:
            totalAccuracy = totalAccuracy + tempAccuracy
    totalAccuracy = totalAccuracy / (len(files) - errorCounter)
    return totalAccuracy, errorCounter


# you can modify this part to run different algorithms on different dataset in a directory
list = getfileListFromDirectory("terms")

totalAccuracy, errorCounter = computeTotalAverageAccuracy(list, False, algorithm=maxsim, simOption="path")
print(f"path similarity : {totalAccuracy * 100}% considering {errorCounter} missing word")

"""
#uncomment to test the Speed
sent = "Effect of the duration of prefeeding on amino acid digestibility of wheat distillers dried grains with solubles in broiler chicken.The objective of this study was to determine the effect of the duration of prefeeding on prececal amino acid (AA) digestibility of wheat distillers dried grains with solubles (DDGS) in broilers. The experimental diets with DDGS at levels of 0, 10, and 20% were offered ad libitum for 7, 5, and 3 d, starting on 14, 16, and 18 d of age. Titanium dioxide was used as an indigestible marker. Six pens of 10 birds were allocated to each treatment. Digesta was sampled on a pen basis from the distal two-thirds of the intestine section between Meckel's diverticulum and 2 cm anterior to the ileo-ceca-colonic junction. Ingested and digested amounts of AA were determined for each pen. Digestibility of AA in the diets was not significantly affected by the duration of prefeeding but was significantly reduced by inclusion of DDGS. Digestibility of AA in DDGS was determined by using a linear regression approach. The digestibility of AA in DDGS ranged from 76% (Arg, 5 d of feeding) to 33% (Asp, 3 d of feeding). There was no significant effect of prefeeding time on AA digestibility of DDGS. Lysine digestibility of DDGS was 72%. The mean digestibility of the AA Arg, Cys, Ile, Leu, Lys, Met, Phe, Thr, and Val of DDGS across the 3 prefeeding times was 66%. This study gave evidence that 3 d of prefeeding a diet is sufficient in studying prececal AA digestibility in broilers when low-digestible feeds are used."
start = time.time()
r1 = dis.disambiguate(sent, maxsim, similarity_option="path", keepLemmas=True)
end = time.time()
print(f"result : {r1}")
print(f"time needed for this sentence:\n{sent}\n\n {end - start}s")

sent = "Effect of the duration of prefeeding on amino acid digestibility of wheat distillers dried grains with solubles in broiler chicken.The objective of this study was to determine the effect of the duration of prefeeding on prececal amino acid (AA) digestibility of wheat distillers dried grains with solubles (DDGS) in broilers. The experimental diets with DDGS at levels of 0, 10, and 20% were offered ad libitum for 7, 5, and 3 d, starting on 14, 16, and 18 d of age. Titanium dioxide was used as an indigestible marker. Six pens of 10 birds were allocated to each treatment. Digesta was sampled on a pen basis from the distal two-thirds of the intestine section between Meckel's diverticulum and 2 cm anterior to the ileo-ceca-colonic junction. Ingested and digested amounts of AA were determined for each pen. Digestibility of AA in the diets was not significantly affected by the duration of prefeeding but was significantly reduced by inclusion of DDGS. Digestibility of AA in DDGS was determined by using a linear regression approach. The digestibility of AA in DDGS ranged from 76% (Arg, 5 d of feeding) to 33% (Asp, 3 d of feeding). There was no significant effect of prefeeding time on AA digestibility of DDGS. Lysine digestibility of DDGS was 72%. The mean digestibility of the AA Arg, Cys, Ile, Leu, Lys, Met, Phe, Thr, and Val of DDGS across the 3 prefeeding times was 66%. This study gave evidence that 3 d of prefeeding a diet is sufficient in studying prececal AA digestibility in broilers when low-digestible feeds are used."
start = time.time()
r1 = maxsim(sent, "aa","path")
end = time.time()
print(f"result : {r1}")
print(f"time needed for this sentence:\n{sent}\n\n {end - start}s")
"""
