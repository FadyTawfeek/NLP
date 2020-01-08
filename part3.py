from pywsd import lesk as l
from pywsd.similarity import max_similarity as maxsim
from pywsd import baseline as base

sentence = "Outcomes of AA for special populations."
ambiguousWord = "AA"

print(f"\nambiguous word {ambiguousWord} in the sentence \"{sentence}\"")
print(f"original lesk : {l.original_lesk(sentence, ambiguousWord)}")
print(f"adapted lesk : {l.adapted_lesk(sentence, ambiguousWord)}")
print(f"cosine lesk : {l.cosine_lesk(sentence, ambiguousWord)}")
print(f"simple lesk : {l.simple_lesk(sentence, ambiguousWord)}")

pathOption = "path"
resnikOption = "resnik"
print(f"path-semantic similarity : {maxsim(sentence, ambiguousWord, option=pathOption)}")
print(f"content-semantic similarity : {maxsim(sentence, ambiguousWord, option=resnikOption)}")

print(f"max lemma count : {base.max_lemma_count(ambiguousWord)}")
