import math
import nltk
import fuzzy
from nltk.corpus import wordnet as wn

example = 'I have been prescribed two important drugs today during my visit to clinic'
target_word = 'been'
soundex = fuzzy.Soundex(4)
target_word = soundex(target_word)
words = example.split()
length = len(words)
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

temp_res = 0
arr = [[0 for i in range(length)] for j in range(length)] 

for x1 in phonetic_words:
    arr[phonetic_words.index(x1)] = levenshtein(target_word,x1)
    temp_res += int (arr[phonetic_words.index(x1)])

mean = temp_res/length
mean_new = 4-mean
print (mean)
print (mean_new)
