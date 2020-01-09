import os
import re
import fuzzy
import numpy as np
from pywsd import lesk as l
from nltk.corpus import wordnet as wn
from pywsd import lemmatize, word_tokenize, sim
from pywsd.similarity import max_similarity as maxsim

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
            elif simOption == "new":
                syn = newMaxSimilarity(example.sentence, word.word)
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


def levenshtein(s1, s2):
    """
    the function for the getting the phonetic distance between 2 words
    :param s1: string of the word 1
    :param s2: string of the word 2
    :return: a float value which is the phonetic distance between the 2 words
    """
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1 + 1], newDistances[-1])))
        distances = newDistances
    return distances[-1]


def fuzzy_output(wanted_sentence, wanted_word):
    """
    the function for the getting the mean phonetic distance between an ambiguous word and each word from the sentence
    :param wanted_sentence: the string of the context sentence
    :param wanted_word: the string of the ambiguous word
    :return: the mean phonetic distance between an ambiguous word and each word from the sentence
    """
    temp_res = 0

    phonetic_words = []
    example = wanted_sentence
    target_word = wanted_word
    soundex = fuzzy.Soundex(4)
    target_word = soundex(target_word)
    words = example.split()
    our_length = len(words)
    arr = [[0 for i in range(our_length)] for j in range(our_length)]
    # print (words)

    for z in words:
        soundex = fuzzy.Soundex(4)
        z = soundex(z)
        phonetic_words.append(z)

    for x1 in phonetic_words:
        arr[phonetic_words.index(x1)] = levenshtein(target_word, x1)
        temp_res += int(arr[phonetic_words.index(x1)])

    mean = temp_res / our_length
    mean_new = 4 - mean
    # print (mean_new)
    return mean_new


def newMaxSimilarity(context_sentence: str, ambiguous_word: str, option="path", lemma=True, context_is_lemmatized=False,
                     pos=None, best=True) -> "wn.Synset":
    """
    Perform WSD by maximizing the sum of maximum similarity between possible
    synsets of all words in the context sentence and the possible synsets of the
    ambiguous words (see https://ibin.co/4gG9zUlejUUA.png):
    {argmax}_{synset(a)}(\sum_{i}^{n}{{max}_{synset(i)}(sim(i,a))}

    :param context_sentence: String, a sentence.
    :param ambiguous_word: String, a single word.
    :return: If best, returns only the best Synset, else returns a dict.
    """
    ambiguous_word = lemmatize(ambiguous_word)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    if context_is_lemmatized:
        context_sentence = word_tokenize(context_sentence)
    else:
        context_sentence = [lemmatize(w) for w in word_tokenize(context_sentence)]
    # add to check the pos tag lead to an empty synsets
    if not wn.synsets(ambiguous_word, pos=pos):
        ambiguousSynset = wn.synsets(ambiguous_word)
    else:
        ambiguousSynset = wn.synsets(ambiguous_word, pos=pos)
    result = {}
    for i in ambiguousSynset:
        result[i] = 0
        for j in context_sentence:
            _result = [0]
            for k in wn.synsets(j):
                _result.append(sim(i, k, option))
            if option == "path":
                phonecticResult = fuzzy_output(ambiguous_word, j) / 2
                result[i] += 0.5 * phonecticResult
                result[i] += 0.5 * max(_result)
            else:
                result[i] += max(_result)

    if option in ["res", "resnik"]:  # lower score = more similar
        result = sorted([(v, k) for k, v in result.items()])
    else:  # higher score = more simila  r
        result = sorted([(v, k) for k, v in result.items()], reverse=True)

    return result[0][1] if best else result


def computeForAcronyms():
    """
    compute with the newMaxSimilarity algorithm we implemented on the acronyms and print the result
    :return: nothing
    """
    list = getfileListFromDirectory("acronyms")
    totalAccuracy, errorCounter = computeTotalAverageAccuracy(list, False, algorithm=maxsim, simOption="new")
    print(f"new max_similarity path and phonetic : {totalAccuracy * 100}% considering {errorCounter} missing word")


def computeForTerms():
    """
        compute with the newMaxSimilarity algorithm we implemented on the terms and print the result
        :return: nothing
        """
    list = getfileListFromDirectory("terms")
    totalAccuracy, errorCounter = computeTotalAverageAccuracy(list, False, algorithm=maxsim, simOption="new")
    print(f"new max_similarity path and phonetic : {totalAccuracy * 100}% considering {errorCounter} missing word")


computeForAcronyms()

"""uncomment it to compute for terms
computeForTerms()
"""
