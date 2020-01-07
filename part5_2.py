import math
import nltk
import fuzzy
from nltk.corpus import wordnet as wn

example = 'I have been prescribed two important drugs today during my visit to clinic'
words = example.split()
print (words)
phonetic_words = []
for z in words:
    soundex = fuzzy.Soundex(4)
    z=soundex(z)
    phonetic_words.append(z)


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

rows = 13 
cols = 13
arr = [[0 for i in range(cols)] for j in range(rows)] 

for x1 in phonetic_words:
        for x2 in phonetic_words:
                arr[phonetic_words.index(x1)][phonetic_words.index(x2)] = levenshtein(x1,x2)

for row in arr:
    # Loop over columns.
    for column in row:
        print(column, end=" ")
    print(end="\n")
