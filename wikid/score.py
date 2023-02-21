from difflib import SequenceMatcher
from collections import Counter
from nltk.corpus import wordnet as wn
import math
import spacy
from time import perf_counter_ns

# Load during startup to help speed up processing
print("Loading spacy...")
start = perf_counter_ns()
_nlp = spacy.load("en_core_web_lg")
length = (perf_counter_ns() - start) * 0.001
print(f"Loading time: {length:,.1f} microseconds")



from typing import (
    List
)

def core_web_score(a: str, b: str) -> float:
    """Compute the semantic similarity between two words a and b using a pre-trained language model."""

    # Get the spaCy token objects for each word
    a_token = _nlp.vocab[a]
    b_token = _nlp.vocab[b]

    # Compute the similarity score between the two tokens
    similarity = a_token.similarity(b_token)
    return similarity


def wordnet_score(a: str, b: str) -> float:
    """Compute the semantic similarity between two words a and b using the WordNet lexical database."""
    synsets_a = wn.synsets(a)
    synsets_b = wn.synsets(b)
    if not synsets_a or not synsets_b:
        return 0.0
    else:
        # Compute the maximum similarity score between each pair of synsets
        scores = [max(s1.path_similarity(s2) or 0 for s2 in synsets_b) for s1 in synsets_a]
        return max(scores)

def exact_match_score(title, dest_title):
    return 1 if title.lower() == dest_title.lower() else 0

def sequence_score(title, dest_title):
    similarity = SequenceMatcher(None, title, dest_title).ratio()
    return similarity

def cosine_score(a: str, b: str) -> float:
    """Compute the cosine similarity between two strings a and b."""

    # Compute the word frequencies for each string
    a_freq = Counter(a.split())
    b_freq = Counter(b.split())

    # Create a set of all words that appear in either string
    words = set(a_freq.keys()).union(set(b_freq.keys()))

    # Compute the dot product and magnitudes for each string
    dot_product = sum(a_freq.get(w, 0) * b_freq.get(w, 0) for w in words)
    a_mag = math.sqrt(sum(a_freq.get(w, 0)**2 for w in words))
    b_mag = math.sqrt(sum(b_freq.get(w, 0)**2 for w in words))

    # Compute the cosine similarity between the two strings
    if a_mag == 0 or b_mag == 0:
        return 0.0
    else:
        return dot_product / (a_mag * b_mag)

def main():
    word_pairs = [
        ("fish", "sneaker"),
        ("father", "mother"),
        ("dog", "cat"),
        ("bark", "bite"),
        ("meow", "scratch"),
        ("hospital", "doctor"),
        ("surgeon", "nurse"),
        ("shark", "tank"),
        ("aquarium", "tank"),
        ("gasoline", "tank"),
        ("fish", "shrimp"),
    ]
    for pairs in word_pairs: 
        score = core_web_score(*pairs)
        print(pairs, f"Score: {score}")



if __name__ == '__main__':
    start = perf_counter_ns()
    main()
    length = (perf_counter_ns() - start) * 0.001
    print(f"Execution time: {length:,.1f} microseconds")

