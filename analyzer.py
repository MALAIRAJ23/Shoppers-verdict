'''
This script performs sentiment and aspect analysis on a list of reviews.
'''
import string
from collections import Counter

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load('en_core_web_sm')
        except OSError:
            from spacy.cli import download
            download('en_core_web_sm')
            import spacy as _spacy
            _nlp = _spacy.load('en_core_web_sm')
    return _nlp


def preprocess_text(text: str) -> str:
    """Converts text to lowercase and removes punctuation."""
    return text.lower().translate(str.maketrans('', '', string.punctuation))

def perform_analysis(reviews_list: list[str]) -> dict:
    """
    Performs sentiment and aspect analysis on a list of review texts.

    Args:
        reviews_list: A list of review strings.

    Returns:
        A dictionary with overall sentiment distribution and aspect-based sentiment scores.
    """
    if not reviews_list:
        return {
            "overall_sentiment": {"positive": 0, "negative": 0, "neutral": 0},
            "aspect_sentiments": {}
        }

    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    sentiment_counts = Counter()
    all_sentences = []
    nlp = get_nlp()

    # 1. Calculate overall sentiment and gather sentences for aspect analysis
    for review in reviews_list:
        # Use the raw review for accurate sentence tokenization and sentiment
        doc = nlp(review)
        all_sentences.extend([sent.text for sent in doc.sents])

        # Calculate sentiment for the entire review
        sentiment_score = analyzer.polarity_scores(review)
        if sentiment_score['compound'] >= 0.05:
            sentiment_counts['positive'] += 1
        elif sentiment_score['compound'] <= -0.05:
            sentiment_counts['negative'] += 1
        else:
            sentiment_counts['neutral'] += 1

    # 2. Extract and count aspects (meaningful noun phrases)
    # Process all reviews together for better frequency counting
    full_text = preprocess_text(" ".join(reviews_list))
    doc = nlp(full_text)
    
    # Filter for multi-word noun chunks that are likely to be specific aspects
    aspects = [
        chunk.text for chunk in doc.noun_chunks 
        if len(chunk.text.split()) > 1 and chunk.root.pos_ == 'NOUN'
    ]
    # If not enough multi-word aspects, fall back to single nouns
    if len(Counter(aspects).most_common(5)) < 5:
        aspects.extend([token.text for token in doc if token.pos_ == 'NOUN'])

    # Get the 5 most common aspects
    top_5_aspects = [aspect for aspect, count in Counter(aspects).most_common(5)]

    # 3. Calculate sentiment for each top aspect
    aspect_sentiments = {}
    for aspect in top_5_aspects:
        aspect_related_sentences = [sent for sent in all_sentences if aspect in preprocess_text(sent)]
        
        if not aspect_related_sentences:
            continue

        total_score = sum(analyzer.polarity_scores(sent)['compound'] for sent in aspect_related_sentences)
        average_score = total_score / len(aspect_related_sentences)
        aspect_sentiments[aspect] = round(average_score, 2)

    # 4. Compile and return the final results
    results = {
        "overall_sentiment": dict(sentiment_counts),
        "aspect_sentiments": aspect_sentiments
    }

    return results

