from nltk.corpus import wordnet as wn
import spacy
from time import perf_counter_ns

from typing import List

# Load during startup to help speed up processing
print("Loading spacy...")
_nlp = spacy.load("en_core_web_lg")

def core_web_score(a: str, b: str, user_interests: List[str] = []) -> float:
    """Compute the semantic similarity between two words a and b using a pre-trained language model, adjusted by user interests."""
    if None in [a, b]:
        return 0.0
    # Get the spaCy token objects for each word
    a_token = _nlp.vocab[a]
    b_token = _nlp.vocab[b]

    # Compute the similarity score between the two tokens
    similarity = a_token.similarity(b_token)

    # Adjust the weight of the similarity score based on user interests
    for interest in user_interests:
        # Check if the interest is similar to either word a or word b
        interest_token = _nlp.vocab[interest]
        similarity_a = a_token.similarity(interest_token)
        similarity_b = b_token.similarity(interest_token)
        if similarity_a > 0.7 or similarity_b > 0.7:
            similarity *= 1.2

    return similarity

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

