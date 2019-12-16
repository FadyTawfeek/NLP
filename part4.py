from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim
from pywsd import baseline as base
from pywsd import allwords_wsd as dis
import random
import numpy as np
from nltk.corpus import wordnet as wn

from part2 import getfileListFromDirectory, Word


##########PROBLEM
# acronyms/EMS_pmids_tagged.arff has html wrong encoding character and create bugs &amp;	instead of &

def computeCounterArray(path: str, algorithm=l.original_lesk):
    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    if len(wordSynsets) != 0:
        disambiguationArray = np.zeros((word.meaningNumber, len(wordSynsets)), dtype=int)
        noneCounter = 0
        i = 0
        for example in word.examples:
            # print(f"example {example.sentence}")
            i = i + 1
            syn = algorithm(example.sentence, word.word)
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


def computeAverageAccuracy(path: str, printRelsult: bool = True, algorithm=l.original_lesk):
    word = Word(path)
    wordSynsets = wn.synsets(word.word)
    counter = computeCounterArray(path, algorithm)
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


def computeTotalAverageAccuracy(listOfFiles, printintermediateResult: bool = False, algorithm=l.original_lesk):
    files = listOfFiles
    errorCounter = 0
    totalAccuracy = 0
    for file in files:
        print(f"file : {file}")
        tempAccuracy = computeAverageAccuracy(file, printintermediateResult, algorithm)
        if tempAccuracy == None:
            errorCounter = errorCounter + 1
        else:
            totalAccuracy = totalAccuracy + tempAccuracy
    totalAccuracy = totalAccuracy / (len(files) - errorCounter)
    return totalAccuracy, errorCounter


acronymsList = getfileListFromDirectory("acronyms")
totalAccuracy, errorCounter = computeTotalAverageAccuracy(acronymsList, False, l.adapted_lesk)
print(f"adapted lesk average : {totalAccuracy * 100}% considering {errorCounter} missing word")
