import math
import nltk
import fuzzy
from nltk.corpus import wordnet as wn

example = 'I have been prescribed two important drugs today during my visit to clinic'
words = example.split() #s plit the sentence into words
print (words)
phonetic_words = [] # initializing an empty array
# for all the words in the given sentence we convert each word and put it in phonetic_words array
for z in words:
    soundex = fuzzy.Soundex(4)
    z=soundex(z)
    phonetic_words.append(z)

# the function for the getting the edit distance between 2 words
def levenshtein(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1 
    distances = range(len(s1) + 1) 
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1]) 
            else:
                 newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1]))) 
        distances = newDistances 
    return distances[-1]


print (phonetic_words)

# initiating an empty array
rows = 13 
cols = 13
arr = [[0 for i in range(cols)] for j in range(rows)] 

# calling the edit distance function for all combinations of 2 words and put them into "arr" array
for x1 in phonetic_words:
        for x2 in phonetic_words:
                arr[phonetic_words.index(x1)][phonetic_words.index(x2)] = levenshtein(x1,x2)

# print the matrix of edit distances of all 2 words combinations in the given sentence
# you will notice the diagonal edit distances are always = 0 because that is the edit distance between the word and itself
for row in arr:
    # Loop over columns.
    for column in row:
        print(column, end=" ")
    print(end="\n")
