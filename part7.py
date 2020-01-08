from tkinter import *
from tkinter import messagebox

from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim


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

        self.printResult(result)


root = Tk()
root.geometry("800x600")

app = Window(root)
root.mainloop()
