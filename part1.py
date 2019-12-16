import nltk
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn

context = "I have been prescribed two important drugs today during my visit to clinic"
ambigousWord = "drug"
rightSense_1 = lesk(context.split(), ambigousWord)
rightSense_2 = lesk(context.split(), ambigousWord, pos='n')

print("Synset, Definition of drug in the context: ", "\n", rightSense_1, ":", rightSense_1.definition())
print("Synset, Definition of drug in the context when we specified to noun: ", "\n", rightSense_2, ":",
      rightSense_2.definition())
