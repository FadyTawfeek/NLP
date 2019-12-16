from pywsd import lesk as l

sentence = "Outcomes of AA for special populations."
ambiguousWord = "AA"
print(f"\nambiguous word {ambiguousWord} in the sentence \"{sentence}\"")
print(f"original lesk : {l.original_lesk(sentence, ambiguousWord)}")
print(f"adapted lesk : {l.adapted_lesk(sentence, ambiguousWord)}")
print(f"cosine lesk : {l.cosine_lesk(sentence, ambiguousWord)}")
print(f"simple lesk : {l.simple_lesk(sentence, ambiguousWord)}")
