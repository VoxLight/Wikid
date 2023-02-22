from nltk.corpus import wordnet as wn
import spacy
from time import perf_counter_ns

# Load during startup to help speed up processing
print("Loading spacy...")
_nlp = spacy.load("en_core_web_lg")

def core_web_score(a: str, b: str) -> float:
    """Compute the semantic similarity between two words a and b using a pre-trained language model."""
    # Get the spaCy token objects for each word
    a_token = _nlp.vocab[a]
    b_token = _nlp.vocab[b]

    # Compute the similarity score between the two tokens
    similarity = a_token.similarity(b_token)
    # print(a, b, "similarity score: ", similarity)
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

