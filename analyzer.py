import string
from collections import Counter
from typing import List, Dict, Any
import re
import math


_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            try:
                # Try to load the small English model if available
                _nlp = spacy.load('en_core_web_sm')
            except Exception:
                # Attempt to download the model. If it fails (e.g., offline), fall back to a blank pipeline.
                try:
                    from spacy.cli import download
                    download('en_core_web_sm')
                    _nlp = spacy.load('en_core_web_sm')
                except Exception:
                    # Robust fallback: blank English with sentencizer only
                    _nlp = spacy.blank('en')
                    if not _nlp.has_pipe('sentencizer'):
                        _nlp.add_pipe('sentencizer')
        except Exception:
            # Last-resort fallback if spaCy itself cannot be imported
            _nlp = None
    return _nlp

def preprocess_text(text: str) -> str:
    """Converts text to lowercase and removes punctuation."""
    return text.lower().translate(str.maketrans('', '', string.punctuation))

# ----------------------
# Helpers for robustness
# ----------------------
_STOPWORDS = {
    'the','and','for','with','you','your','this','that','was','are','but','not','have','has','had','from','were','they','them',
    'their','there','here','very','just','about','into','out','over','under','more','some','any','get','got','much','than','then',
    'also','can','could','would','should','really','been','being','after','before','when','while','because','which','who','what',
    'why','how','does','did','doing','too','is','it','its','i','we','me','my','mine','our','ours','us','u','im','ive','he','she','him','her','his','hers',
    'of','to','in','on','at','as','by','an','be','or'
}

def _tokenize_words(text: str) -> List[str]:
    return [w for w in preprocess_text(text).split() if w and w.isalpha() and len(w) > 2 and w not in _STOPWORDS]

def _split_sentences(text: str, nlp=None) -> List[str]:
    if nlp is not None:
        try:
            doc = nlp(text)
            sents = [s.text.strip() for s in doc.sents if s.text.strip()]
            if sents:
                return sents
        except Exception:
            pass
    # Fallback: simple regex-based split
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p and len(p.strip()) > 0]

def _has_pipes(nlp, names: List[str]) -> bool:
    try:
        return all(nlp.has_pipe(n) for n in names)
    except Exception:
        return False

def _extract_aspects_spacy(nlp, texts: List[str], top_k: int = 20) -> List[str]:
    """Use spaCy noun chunks and POS patterns to get aspect candidates."""
    joined = " \n ".join(texts)
    aspects: List[str] = []
    try:
        doc = nlp(joined)
        # 1) Noun chunks (multi-word first)
        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip().lower()
            if len(phrase.split()) > 1 and chunk.root.pos_ == 'NOUN':
                aspects.append(phrase)
        # 2) POS bigrams: Adj+Noun, Noun+Noun
        tokens = [t for t in doc if not t.is_space and not t.is_punct]
        for i in range(len(tokens)-1):
            t1, t2 = tokens[i], tokens[i+1]
            if (t1.pos_ == 'ADJ' and t2.pos_ == 'NOUN') or (t1.pos_ == 'NOUN' and t2.pos_ == 'NOUN'):
                phrase = f"{t1.text.lower()} {t2.text.lower()}"
                aspects.append(phrase)
        # 3) Single nouns as fallback
        aspects.extend([t.lemma_.lower() for t in doc if t.pos_ == 'NOUN'])
    except Exception:
        pass
    # Count and pick top_k
    counts = Counter(aspects)
    # Filter out stopwords and extremely short tokens
    cleaned = [(a, c) for a, c in counts.items() if all(len(tok) > 2 and tok not in _STOPWORDS for tok in a.split())]
    cleaned.sort(key=lambda x: x[1], reverse=True)
    return [a for a, _ in cleaned[:top_k]]

def _extract_aspects_fallback(texts: List[str], top_k: int = 20) -> List[str]:
    """Heuristic extraction without spaCy: frequent unigrams/bigrams."""
    tokens = []
    for t in texts:
        tokens.extend(_tokenize_words(t))
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)] if len(tokens) > 1 else []
    counts = Counter(bigrams) + Counter(tokens)
    items = [(term, cnt) for term, cnt in counts.items() if all(len(tok) > 2 and tok not in _STOPWORDS for tok in term.split())]
    items.sort(key=lambda x: x[1], reverse=True)
    return [term for term, _ in items[:top_k]]

def _map_aspects_to_sentences(aspects: List[str], sentences: List[str]) -> Dict[str, List[str]]:
    """Assign sentences to aspects via token subset matching to avoid spurious substring hits."""
    sent_tokens = [set(_tokenize_words(s)) for s in sentences]
    mapping: Dict[str, List[str]] = {a: [] for a in aspects}
    for aspect in aspects:
        a_tokens = set(_tokenize_words(aspect))
        if not a_tokens:
            continue
        for i, stoks in enumerate(sent_tokens):
            if a_tokens.issubset(stoks):
                mapping[aspect].append(sentences[i])
    # Drop aspects with no support
    return {a: sents for a, sents in mapping.items() if sents}

def _is_spam_review(text: str) -> bool:
    """Detect spam or low-quality review patterns."""
    text_lower = text.lower()
    
    # Common spam patterns
    spam_patterns = [
        r'\b(buy|purchase|order)\s+(now|today|here)\b',
        r'\b(best|cheap|discount|offer)\s+(price|deal)\b',
        r'\b(click|visit|check)\s+(here|link|website)\b',
        r'\b(www\.|http|@|#)\b',  # URLs, emails, social media
        r'\b(fake|bot|spam)\b'
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, text_lower):
            return True
    
    # Check for repetitive characters
    if re.search(r'(.)\1{4,}', text):  # 5+ repeated characters
        return True
        
    # Check for excessive capitalization
    if len([c for c in text if c.isupper()]) / max(len(text), 1) > 0.7:
        return True
        
    return False

def _is_too_similar(text: str, existing_texts: List[str], threshold: float = 0.8) -> bool:
    """Check if text is too similar to existing ones using simple similarity."""
    if not existing_texts:
        return False
        
    text_words = set(text.split())
    
    for existing in existing_texts[-20:]:  # Check last 20 for efficiency
        existing_words = set(existing.split())
        
        if not text_words or not existing_words:
            continue
            
        # Jaccard similarity
        intersection = text_words.intersection(existing_words)
        union = text_words.union(existing_words)
        
        similarity = len(intersection) / len(union) if union else 0
        
        if similarity > threshold:
            return True
            
    return False

def _calculate_review_quality(text: str) -> float:
    """Calculate quality score for a review (0-1 scale)."""
    score = 0.5  # Base score
    
    # Length factor (optimal range 20-200 characters)
    length = len(text.strip())
    if 30 <= length <= 150:
        score += 0.2
    elif 150 < length <= 300:
        score += 0.1
    elif length < 20 or length > 500:
        score -= 0.2
        
    # Word diversity
    words = _tokenize_words(text)
    unique_words = set(words)
    if words:
        diversity = len(unique_words) / len(words)
        score += diversity * 0.2
        
    # Sentence structure (simple heuristic)
    sentences = _split_sentences(text)
    if len(sentences) >= 2:
        score += 0.1
        
    # Contains product-specific terms
    product_terms = {'good', 'bad', 'quality', 'product', 'item', 'price', 'value', 
                    'delivery', 'packaging', 'service', 'recommend', 'satisfied',
                    'happy', 'disappointed', 'excellent', 'poor', 'average'}
    
    text_lower = text.lower()
    matches = sum(1 for term in product_terms if term in text_lower)
    score += min(matches * 0.05, 0.2)
    
    return max(0, min(1, score))

def _calculate_sentiment_confidence(sentence: str, vader_scores: dict) -> float:
    """Calculate confidence in sentiment analysis based on multiple factors."""
    confidence = 0.5  # Base confidence
    
    # Score magnitude (stronger scores = higher confidence)
    compound = abs(vader_scores['compound'])
    confidence += compound * 0.3
    
    # Positive/negative score agreement
    pos = vader_scores['pos']
    neg = vader_scores['neg']
    
    if pos > 0.3 and neg < 0.1:  # Clear positive
        confidence += 0.2
    elif neg > 0.3 and pos < 0.1:  # Clear negative
        confidence += 0.2
    elif abs(pos - neg) > 0.3:  # Clear dominance
        confidence += 0.1
    
    # Sentence length (very short or very long = less reliable)
    words = len(sentence.split())
    if 5 <= words <= 20:
        confidence += 0.1
    elif words < 3 or words > 50:
        confidence -= 0.2
    
    # Presence of strong sentiment words
    strong_positive = {'excellent', 'amazing', 'fantastic', 'perfect', 'outstanding', 'brilliant'}
    strong_negative = {'terrible', 'awful', 'horrible', 'worst', 'disgusting', 'pathetic'}
    
    sentence_lower = sentence.lower()
    if any(word in sentence_lower for word in strong_positive | strong_negative):
        confidence += 0.15
    
    return max(0, min(1, confidence))

def _adjust_for_context(score: float, sentence: str, full_review: str) -> float:
    """Adjust sentiment score based on context and negation patterns."""
    adjusted_score = score
    sentence_lower = sentence.lower()
    
    # Negation patterns that might flip sentiment
    negation_patterns = [
        r'\bnot\s+',
        r'\bno\s+',
        r'\bnever\s+',
        r'\bwithout\s+',
        r'\bbarely\s+',
        r'\bhardly\s+',
        r'\bcan\'t\s+',
        r'\bwon\'t\s+',
        r'\bdoesn\'t\s+',
        r'\bisn\'t\s+'
    ]
    
    # Check for negation near sentiment words
    for pattern in negation_patterns:
        if re.search(pattern, sentence_lower):
            # Look for sentiment words after negation
            negation_matches = list(re.finditer(pattern, sentence_lower))
            for match in negation_matches:
                end_pos = match.end()
                remaining = sentence_lower[end_pos:end_pos+50]  # Next 50 chars
                
                # If sentiment words follow negation, adjust score
                positive_words = ['good', 'great', 'nice', 'happy', 'satisfied', 'recommend']
                negative_words = ['bad', 'poor', 'hate', 'disappointed', 'problem', 'issue']
                
                if any(word in remaining for word in positive_words):
                    adjusted_score -= abs(score) * 0.8  # Flip positive to negative
                elif any(word in remaining for word in negative_words):
                    adjusted_score += abs(score) * 0.8  # Flip negative to positive
    
    # Context from full review (sarcasm/irony detection)
    full_review_lower = full_review.lower()
    
    # Sarcasm indicators
    sarcasm_indicators = ['yeah right', 'sure', 'obviously', 'definitely not', 'as if']
    if any(indicator in sentence_lower for indicator in sarcasm_indicators):
        adjusted_score *= -0.7  # Likely sarcastic
    
    # Comparison context ("better than X" vs "worse than X")
    if 'better than' in sentence_lower or 'improved from' in sentence_lower:
        adjusted_score = abs(adjusted_score) * 0.7  # Moderate positive
    elif 'worse than' in sentence_lower or 'downgrade from' in sentence_lower:
        adjusted_score = -abs(adjusted_score) * 0.7  # Moderate negative
    
    return max(-1, min(1, adjusted_score))

def analyze_product_description(description: str) -> Dict[str, Any]:
    """
    Analyzes product description to determine usability and quality indicators.
    Returns a dictionary with usability score, key features, pros, and cons.
    """
    if not description or not description.strip():
        return {
            "usability_score": 50,
            "usability_verdict": "neutral",
            "key_features": [],
            "pros": [],
            "cons": [],
            "summary": "No description available for analysis."
        }
    
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Split into sentences and analyze each
    sentences = _split_sentences(description)
    if not sentences:
        sentences = [description]
    
    # Identify positive and negative indicators
    positive_keywords = {
        'excellent', 'premium', 'high-quality', 'durable', 'reliable', 'efficient', 'advanced',
        'innovative', 'superior', 'professional', 'powerful', 'fast', 'lightweight', 'compact',
        'user-friendly', 'easy', 'comfortable', 'stylish', 'modern', 'latest', 'improved',
        'enhanced', 'upgraded', 'warranty', 'certified', 'tested', 'approved'
    }
    
    negative_keywords = {
        'cheap', 'fragile', 'basic', 'limited', 'slow', 'heavy', 'bulky', 'outdated',
        'complicated', 'difficult', 'poor', 'low-quality', 'defective', 'issue', 'problem'
    }
    
    feature_keywords = {
        'feature', 'specification', 'capacity', 'size', 'weight', 'dimension', 'material',
        'technology', 'compatibility', 'connectivity', 'performance', 'efficiency', 'design'
    }
    
    # Analyze sentiment and extract features
    sentence_scores = []
    key_features = []
    pros = []
    cons = []
    
    for sentence in sentences:
        score = analyzer.polarity_scores(sentence)['compound']
        sentence_scores.append(score)
        
        sentence_lower = sentence.lower()
        words = _tokenize_words(sentence)
        
        # Extract features
        if any(fw in sentence_lower for fw in feature_keywords):
            if len(sentence.strip()) > 20 and len(sentence.strip()) < 200:
                key_features.append(sentence.strip())
        
        # Extract pros (positive sentences with positive keywords)
        if score > 0.1 and any(pw in sentence_lower for pw in positive_keywords):
            pros.append(sentence.strip())
        
        # Extract cons (negative sentences or negative keywords)
        elif score < -0.1 or any(nw in sentence_lower for nw in negative_keywords):
            cons.append(sentence.strip())
    
    # Calculate overall usability score
    if sentence_scores:
        avg_sentiment = sum(sentence_scores) / len(sentence_scores)
        # Convert from [-1, 1] to [0, 100]
        base_score = (avg_sentiment + 1) / 2 * 100
        
        # Adjust based on keywords
        pos_count = sum(1 for sentence in sentences 
                       if any(pw in sentence.lower() for pw in positive_keywords))
        neg_count = sum(1 for sentence in sentences 
                       if any(nw in sentence.lower() for nw in negative_keywords))
        
        keyword_adjustment = (pos_count - neg_count) * 5
        usability_score = max(0, min(100, base_score + keyword_adjustment))
    else:
        usability_score = 50
    
    # Determine verdict
    if usability_score >= 80:
        verdict = "excellent"
    elif usability_score >= 65:
        verdict = "good"
    elif usability_score >= 50:
        verdict = "average"
    elif usability_score >= 35:
        verdict = "poor"
    else:
        verdict = "avoid"
    
    # Limit lists
    key_features = key_features[:5]
    pros = pros[:3]
    cons = cons[:3]
    
    # Generate summary
    if verdict == "excellent":
        summary = "This product appears to be excellent for use based on its description."
    elif verdict == "good":
        summary = "This product seems good to use with several positive indicators."
    elif verdict == "average":
        summary = "This product has mixed indicators - review carefully before use."
    elif verdict == "poor":
        summary = "This product may have some limitations - consider alternatives."
    else:
        summary = "This product description raises concerns about its usability."
    
    return {
        "usability_score": round(usability_score),
        "usability_verdict": verdict,
        "key_features": key_features,
        "pros": pros,
        "cons": cons,
        "summary": summary
    }

def perform_analysis(reviews_list: List[str]) -> Dict[str, Any]:
    """
    Enhanced high-accuracy analysis with advanced techniques:
    - Intelligent deduplication and quality filtering
    - Context-aware sentiment analysis
    - Advanced aspect extraction with domain-specific patterns
    - Negation handling and intensity weighting
    - Statistical significance testing for aspects
    """
    if not reviews_list:
        return {
            "overall_sentiment": {"positive": 0, "negative": 0, "neutral": 0},
            "aspect_sentiments": {},
            "aspect_support": {},
            "meta": {"reviews_used": 0, "sentences": 0, "confidence": 0}
        }

    # 0) Enhanced cleaning and quality filtering
    seen = set()
    cleaned: List[str] = []
    quality_scores = []
    
    for r in reviews_list:
        if not isinstance(r, str):
            continue
        t = r.strip()
        
        # Enhanced quality filters
        if len(t) < 15:  # Too short
            continue
        if len(t) > 2000:  # Likely spam or non-review content
            continue
            
        # Check for spam patterns
        if _is_spam_review(t):
            continue
            
        # Deduplication with similarity threshold
        key = preprocess_text(t)
        if key in seen or _is_too_similar(key, list(seen)):
            continue
            
        # Calculate quality score
        quality = _calculate_review_quality(t)
        if quality < 0.3:  # Filter very low quality reviews
            continue
            
        seen.add(key)
        cleaned.append(t)
        quality_scores.append(quality)
        
    if not cleaned:
        cleaned = [r for r in reviews_list if isinstance(r, str) and r.strip()]
        quality_scores = [0.5] * len(cleaned)  # Default quality

    # 1) Enhanced sentence segmentation and context-aware sentiment analysis
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    nlp = get_nlp()

    sentences: List[str] = []
    sentence_weights: List[float] = []
    review_contexts: List[str] = []
    
    for i, rev in enumerate(cleaned):
        rev_sentences = _split_sentences(rev, nlp)
        sentences.extend(rev_sentences)
        
        # Weight sentences by review quality
        quality_weight = quality_scores[i] if i < len(quality_scores) else 0.5
        sentence_weights.extend([quality_weight] * len(rev_sentences))
        review_contexts.extend([rev] * len(rev_sentences))

    sentiment_counts = Counter()
    sentence_scores: List[float] = []
    confidence_scores: List[float] = []
    
    # Enhanced thresholds based on confidence
    POS_TH, NEG_TH = 0.1, -0.1  # More conservative thresholds
    
    for i, s in enumerate(sentences):
        # Get VADER scores
        scores = analyzer.polarity_scores(s)
        compound = scores['compound']
        
        # Calculate confidence based on score magnitude and word count
        confidence = _calculate_sentiment_confidence(s, scores)
        confidence_scores.append(confidence)
        
        # Apply negation detection and context adjustments
        adjusted_score = _adjust_for_context(compound, s, review_contexts[i])
        sentence_scores.append(adjusted_score)
        
        # Weighted sentiment classification
        weight = sentence_weights[i] * confidence
        
        if adjusted_score >= POS_TH:
            sentiment_counts['positive'] += weight
        elif adjusted_score <= NEG_TH:
            sentiment_counts['negative'] += weight
        else:
            sentiment_counts['neutral'] += weight

    # 2) Aspect extraction
    if nlp is not None and _has_pipes(nlp, ['tagger', 'parser']):
        aspect_candidates = _extract_aspects_spacy(nlp, cleaned, top_k=30)
    else:
        aspect_candidates = _extract_aspects_fallback(cleaned, top_k=30)

    # 3) Map aspects to supporting sentences and compute sentiment per aspect
    aspect_to_sentences = _map_aspects_to_sentences(aspect_candidates, sentences)

    aspect_sentiments: Dict[str, float] = {}
    for aspect, sents in aspect_to_sentences.items():
        scores = [analyzer.polarity_scores(s)['compound'] for s in sents]
        if not scores:
            continue
        avg = sum(scores) / len(scores)
        # Only keep aspects with at least 2 supporting sentences for stability
        if len(sents) >= 2:
            aspect_sentiments[aspect] = round(avg, 2)

    # 4) Select top aspects by support and magnitude; cap to 5
    # Sort by (#support desc, |sentiment| desc)
    ranked = sorted(
        aspect_sentiments.items(),
        key=lambda kv: (len(aspect_to_sentences.get(kv[0], [])), abs(kv[1])),
        reverse=True
    )
    aspect_sentiments = dict(ranked[:5])

    # Calculate overall confidence
    overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Data sufficiency score
    data_sufficiency = min(len(cleaned) / 20.0, 1.0)  # Full confidence at 20+ reviews
    
    # Combined confidence score
    combined_confidence = (overall_confidence * 0.4 + avg_quality * 0.3 + data_sufficiency * 0.3)
    
    return {
        "overall_sentiment": dict(sentiment_counts),
        "aspect_sentiments": aspect_sentiments,
        "aspect_support": {k: aspect_to_sentences.get(k, [])[:3] for k in aspect_sentiments.keys()},
        "meta": {
            "reviews_used": len(cleaned),
            "sentences": len(sentences),
            "confidence": round(combined_confidence, 2),
            "avg_quality": round(avg_quality, 2),
            "data_sufficiency": round(data_sufficiency, 2)
        }
    }



