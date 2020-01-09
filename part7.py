from tkinter import *
from tkinter import messagebox

from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim
from nltk.corpus import wordnet as wn
from pywsd import lemmatize, word_tokenize, sim
import fuzzy


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


class Window(Frame):
    """
    class of the window for our disambiguation application
    :param master : means it is the root element of the application
    :param disambiguateButton : button to press to disambiguate
    :param algorithmList : Listbox of all possible algorithms
    :param ambiguousLabelText : string of the label for ambiguous word
    :param ambiguousWordText : Text panel to get input for the ambiguous word
    :param ambiguousLabel : Label of the ambiguous word
    :param contextLabelText : string of the label for the context sentence
    :param contextLabel : Label of the context sentence
    :param context : Text input panel to get the context sentence
    :param resultLabelText : string of the label for the result
    :param resultLabel : Label of the result
    :param result : Text output panel to print the result of the disambiguation
    """

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.setWindow()

    def setWindow(self):
        """
        init all elements inside the window
        :return: nothing
        """
        self.master.title("NLP Disambiguation terms")
        self.pack(fill=BOTH, expand=1)

        # set process button
        self.disambiguateButton = Button(self, text="disambiguate", command=self.disambiguate, width=12, height=3)
        self.disambiguateButton.place(x=700, y=530)

        # set the label for list of algorithms
        self.algorithmListLabelText = StringVar()
        self.algorithmListLabel = Label(self, textvariable=self.algorithmListLabelText)
        self.algorithmListLabelText.set("choose an algorithm :")
        self.algorithmListLabel.place(x=10, y=0)

        # set the list of algorithms
        self.algorithmList = Listbox(self, selectmode="single", width=37)
        self.algorithmList.insert(0, "Original Lesk")
        self.algorithmList.insert(1, "Adapted Lesk")
        self.algorithmList.insert(2, "Simple Lesk")
        self.algorithmList.insert(3, "Cosine Lesk")
        self.algorithmList.insert(4, "Path-Semantic Similarity")
        self.algorithmList.insert(5, "Information content-semantic similarity")
        self.algorithmList.insert(6, "Path-Semantic with phonetics Similarity")

        self.algorithmList.place(x=50, y=20)

        # set label for ambiguous word label
        self.ambiguousLabelText = StringVar()
        self.ambiguousLabel = Label(self, textvariable=self.ambiguousLabelText)
        self.ambiguousLabelText.set("write the word you want to disambiguate :")

        self.ambiguousLabel.place(x=290, y=10)

        # set ambiguous word input panel
        self.ambiguousWordText = Entry(self, width=20)
        self.ambiguousWordText.place(x=300, y=30)

        # set context label
        self.contextLabelText = StringVar()
        self.contextLabel = Label(self, textvariable=self.contextLabelText)
        self.contextLabelText.set("write the context sentence :")

        self.contextLabel.place(x=10, y=183)

        # set the context input panel
        self.context = Text(self)
        self.context.place(x=50, y=200)

        # set the result label
        self.resultLabelText = StringVar()
        self.resultLabel = Label(self, textvariable=self.resultLabelText)
        self.resultLabelText.set("Result : ")

        self.resultLabel.place(x=290, y=55)

        # set the result panel
        self.result = Text(self, state=NORMAL, width=50, height=7, bg="#241F2E", fg="#F1F1F1")
        self.result.configure(state=DISABLED)
        self.result.pack()
        self.result.place(x=290, y=75)

    def getContext(self):
        """
        return the context sentence
        :return: all text inside the context panel
        """
        return self.context.get("1.0", "end-1c")

    def getAmbiguousWord(self):
        """
        retun the ambiguous word
        :return: string from the ambiguousWordText panel
        """
        return self.ambiguousWordText.get()

    def printResult(self, result: str):
        """
        print the result inside the result panel
        :param result: string that have to be printed
        :return: nothing
        """
        self.result.configure(state=NORMAL)
        self.result.delete('1.0', END)
        self.result.insert(INSERT, result)
        self.result.configure(state=DISABLED)

    def clearResult(self):
        """
        clear the result panel
        :return: nothing
        """
        self.result.configure(state=NORMAL)
        self.result.delete('1.0', END)
        self.result.configure(state=DISABLED)

    def isAmbiguousWordInContext(self):
        """
        check if the ambiguous word from the ambiguousWord panel is also inside the context panel
        :return: True if it is otherwise False
        """
        if self.ambiguousWord in self.sentence.split():
            return True
        else:
            return False

    def disambiguate(self):
        """
        do the disambiguation according to the sentence panel, the ambiguousWord panel and the algorithm selected
        :return: wn.Synset
        """
        self.sentence = self.getContext()
        self.ambiguousWord = self.getAmbiguousWord()
        selectedAlgorithm = self.algorithmList.curselection()
        if not self.sentence:
            print("No sentence written. Please write a context sentence")
            messagebox.showerror("Error", "No sentence written. Please write a context sentence")
            return
        if not self.ambiguousWord:
            print("No ambiguous word written. Please write an ambiguous word")
            messagebox.showerror("Error", "No ambiguous word written. Please write an ambiguous word")
            return
        if not self.isAmbiguousWordInContext():
            print("ambiguous word is not in the context. please check if you did a mistake")
            messagebox.showerror("Error", "ambiguous word is not in the context. please check if you did a mistake")
            return

        self.clearResult()
        if not selectedAlgorithm:
            print("Error", "No algorithm selected ! please select one")
            messagebox.showerror("Error", "No algorithm selected ! please select one")
            result = ""
        elif selectedAlgorithm[0] == 0:  # original Lesk
            result = l.original_lesk(self.sentence, self.ambiguousWord)
        elif selectedAlgorithm[0] == 1:  # adapted Lesk
            result = l.adapted_lesk(self.sentence, self.ambiguousWord)
        elif selectedAlgorithm[0] == 2:  # simple Lesk
            result = l.simple_lesk(self.sentence, self.ambiguousWord)
        elif selectedAlgorithm[0] == 3:  # cosine Lesk
            result = l.cosine_lesk(self.sentence, self.ambiguousWord)
        elif selectedAlgorithm[0] == 4:  # path-semantic similarity
            result = maxsim(self.sentence, self.ambiguousWord, option="path")
        elif selectedAlgorithm[0] == 5:  # Information content-semantic similarity
            result = maxsim(self.sentence, self.ambiguousWord, option="resnik")
        elif selectedAlgorithm[0] == 6:  # path-semantic mixed with phonetic similarity
            result = newMaxSimilarity(self.sentence, self.ambiguousWord, option="path")

        self.printResult(result)

root = Tk()
root.geometry("800x600")

app = Window(root)
root.mainloop()
