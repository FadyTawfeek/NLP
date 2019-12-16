from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim
from pywsd import baseline as base
from pywsd import allwords_wsd as dis

sentence = "Outcomes of AA for special populations."
ambiguousWord = "AA"

print(f"\nambiguous word {ambiguousWord} in the sentence \"{sentence}\"")
print(f"original lesk : {l.original_lesk(sentence, ambiguousWord)}")
print(f"adapted lesk : {l.adapted_lesk(sentence, ambiguousWord)}")
print(f"cosine lesk : {l.cosine_lesk(sentence, ambiguousWord)}")
print(f"simple lesk : {l.simple_lesk(sentence, ambiguousWord)}")


def getTheAmbiguousSynset(disambiguateSentenceArray):
    for element in disambiguateSentenceArray:
        if element[0] == ambiguousWord:
            return element[2]


r1 = dis.disambiguate(sentence, algorithm=maxsim, similarity_option="path", keepLemmas=True)
r1 = getTheAmbiguousSynset(r1)
print(f"path-semantic similarity : {r1}")

r2 = dis.disambiguate(sentence, algorithm=maxsim, similarity_option="resnik", keepLemmas=True)
r2 = getTheAmbiguousSynset(r2)
print(f"content-semantic similarity : {r2}")

print(f"max lemma count : {base.max_lemma_count(ambiguousWord)}")
