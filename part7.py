from tkinter import *
from tkinter import messagebox

from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim


class Window(Frame):

    # class Initialization
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.setWindow()

    # Init the window
    def setWindow(self):
        self.master.title("NLP Disambiguation terms")
        self.pack(fill=BOTH, expand=1)

        # set process button
        self.disambiguateButton = Button(self, text="disambiguate", command=self.disambiguate)
        self.disambiguateButton.place(x=700, y=550)

        # set the list of algorithm
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
        self.ambiguousLabelText.set("print the word you want to disambiguate")

        self.ambiguousLabel.place(x=290, y=10)

        # set ambiguous word input panel
        self.ambiguousWordText = Entry(self, width=20)
        self.ambiguousWordText.place(x=300, y=30)

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
        self.result.insert(INSERT, "TEST Testfsasfagfsaf fsa fsa fsa fsa gfdagfdasf")
        self.result.configure(state=DISABLED)
        self.result.pack()
        self.result.place(x=290, y=75)

    # return the context sentence
    def getContext(self):
        return self.context.get("1.0", "end-1c")

    # retun the ambiguous word
    def getAmbiguousWord(self):
        return self.ambiguousWordText.get()

    def disambiguate(self):
        context = self.getContext()
        if context == "":
            print("No input")

    def printResult(self, result: str):
        self.result.configure(state=NORMAL)
        self.result.delete('1.0', END)
        self.result.insert(INSERT, result)
        self.result.configure(state=DISABLED)

    def clearResult(self):
        self.result.configure(state=NORMAL)
        self.result.delete('1.0', END)
        self.result.configure(state=DISABLED)

    def isAmbiguousWordInContext(self):
        if self.ambiguousWord in self.sentence.split():
            return True
        else:
            return False

    def disambiguate(self):
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
        elif selectedAlgorithm[0] == 4:
            result = maxsim(self.sentence, self.ambiguousWord, option="path")
        elif selectedAlgorithm[0] == 5:
            result = maxsim(self.sentence, self.ambiguousWord, option="resnik")

        self.printResult(result)


root = Tk()
root.geometry("800x600")

app = Window(root)
root.mainloop()
