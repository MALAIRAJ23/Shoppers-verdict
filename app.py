from flask import Flask, render_template, request, jsonify
from scraper import scrape_data
from analyzer import perform_analysis, analyze_product_description
import traceback

class ExceptionMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception:
            error_traceback = traceback.format_exc()
            start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/plain')])
            return [error_traceback.encode('utf-8')]

app = Flask(__name__)

# Apply the middleware
app.wsgi_app = ExceptionMiddleware(app.wsgi_app)

@app.route('/')

def index():
    """Renders the main page with the submission form."""
    return render_template('index.html')

@app.route('/features')
def features():
    """Features hub page with interactive feature cards."""
    return render_template('features.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Handles form submission, scrapes reviews, analyzes them,
    and renders the results page.
    """
    product_url = request.form.get('product_url')
    if not product_url:
        return render_template('error.html', message="No product URL was provided.")

    # Normalize URL: prepend https:// if missing
    if not product_url.lower().startswith(('http://', 'https://')):
        product_url = 'https://' + product_url.lstrip('/ ')

    # 1. Scrape data (reviews, price, title, description)
    data = scrape_data(product_url)
    if data is None or not data.get('reviews'):
        return render_template('error.html', message=f"Failed to scrape the URL. It might be invalid or the site may be blocking scrapers.")
    
    reviews = data['reviews']
    product_title = data.get('title', 'Unknown Product')
    product_description = data.get('description', '')

    # 2. Perform review analysis
    analysis_results = perform_analysis(reviews)
    
    # 3. Perform description analysis for usability
    description_analysis = analyze_product_description(product_description)

    # 4. Enhanced 'Worth-to-Buy' Score Calculation
    overall = analysis_results.get("overall_sentiment", {})
    aspects = analysis_results.get("aspect_sentiments", {})
    meta = analysis_results.get('meta', {})
    
    # Base sentiment metrics
    total_reviews = sum(overall.values())
    reviews_used = meta.get('reviews_used', total_reviews)
    sentences_count = meta.get('sentences', 0)
    
    if total_reviews > 0:
        positive_ratio = overall.get("positive", 0) / total_reviews
        negative_ratio = overall.get("negative", 0) / total_reviews
        neutral_ratio = overall.get("neutral", 0) / total_reviews
    else:
        positive_ratio = negative_ratio = neutral_ratio = 0

    # Aspect sentiment analysis
    if aspects:
        avg_aspect_sentiment = sum(aspects.values()) / len(aspects)
        normalized_aspect_sentiment = (avg_aspect_sentiment + 1) / 2
        
        # Calculate aspect diversity (more aspects = more comprehensive analysis)
        aspect_diversity_bonus = min(len(aspects) / 5.0, 1.0) * 0.05
        
        # Strong negative aspects penalty
        strong_negative_aspects = sum(1 for score in aspects.values() if score < -0.3)
        negative_penalty = strong_negative_aspects * 0.08
        
        # Strong positive aspects bonus
        strong_positive_aspects = sum(1 for score in aspects.values() if score > 0.3)
        positive_bonus = strong_positive_aspects * 0.05
    else:
        normalized_aspect_sentiment = 0.5
        aspect_diversity_bonus = 0
        negative_penalty = 0
        positive_bonus = 0

    # Data quality factor (more reviews = more reliable)
    data_quality_factor = min(reviews_used / 50.0, 1.0)  # Max boost at 50+ reviews
    quality_bonus = data_quality_factor * 0.05
    
    # Sentiment consistency factor (penalize if too much neutral sentiment)
    sentiment_consistency = 1 - (neutral_ratio * 0.3)  # Small penalty for too much neutrality
    
    # Enhanced formula with multiple factors
    base_score = positive_ratio * 0.6 + normalized_aspect_sentiment * 0.3 + quality_bonus + aspect_diversity_bonus
    adjusted_score = base_score + positive_bonus - negative_penalty
    final_score = adjusted_score * sentiment_consistency
    
    score = max(0, min(100, final_score * 100))  # Clamp between 0-100

    # 4. Generate Pros and Cons (robust filtering)
    sorted_desc = sorted(aspects.items(), key=lambda item: item[1], reverse=True)
    sorted_asc = list(reversed(sorted_desc))

    POS_TH = 0.05
    NEG_TH = -0.05

    pros = [(a, s) for a, s in sorted_desc if s >= POS_TH][:2]
    cons = [(a, s) for a, s in sorted_asc if s <= NEG_TH][:2]

    # Fallbacks to ensure at least two items if data is scarce
    if len(pros) < 2:
        extras = [(a, s) for a, s in sorted_desc if (a, s) not in pros][:2 - len(pros)]
        pros.extend(extras)
    if len(cons) < 2:
        extras = [(a, s) for a, s in sorted_asc if (a, s) not in cons][:2 - len(cons)]
        cons.extend(extras)

    # 5. Generate voice verdict summary
    voice_verdict = generate_voice_verdict(score, pros, cons)

    # 6. Build human-readable insight/description
    meta = analysis_results.get('meta', {})
    reviews_used = meta.get('reviews_used', total_reviews)
    sentences_count = meta.get('sentences', 0)
    pros_names = ", ".join([a for a, _ in pros]) if pros else ""
    cons_names = ", ".join([a for a, _ in cons]) if cons else ""
    if score >= 70:
        recommendation = "recommended"
    elif score >= 50:
        recommendation = "acceptable"
    else:
        recommendation = "not recommended"

    insight_parts = []
    insight_parts.append(f"Analyzed {reviews_used} reviews and {sentences_count} sentences.")
    if pros_names:
        insight_parts.append(f"Customers praise the {pros_names}.")
    if cons_names:
        insight_parts.append(f"Common complaints include the {cons_names}.")
    insight_parts.append(f"Overall, this product is {recommendation}.")
    insight = " ".join(insight_parts)

    return render_template(
        'results.html',
        score=round(score),
        pros=pros,
        cons=cons,
        analysis=analysis_results,
        product_url=product_url,
        product_title=product_title,
        product_description=product_description,
        description_analysis=description_analysis,
        price_history=data.get('price_history', []),
        voice_verdict=voice_verdict,
        insight=insight
    )

@app.route('/api/scrape_preview', methods=['POST'])
def api_scrape_preview():
    """API: Scrape product URL and return review count and price history."""
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()
    if not url:
        return jsonify(ok=False, error="Missing 'url'"), 400
    if not url.lower().startswith(('http://', 'https://')):
        url = 'https://' + url.lstrip('/ ')
    res = scrape_data(url)
    if not res:
        return jsonify(ok=False, error='Failed to scrape or no data available.'), 502
    reviews = res.get('reviews') or []
    price_history = res.get('price_history') or []
    sample_reviews = reviews[:5]
    return jsonify(ok=True, reviews_count=len(reviews), price_history=price_history, sample_reviews=sample_reviews)

@app.route('/api/analyze_text', methods=['POST'])
def api_analyze_text():
    """API: Analyze provided texts and return sentiment/aspects."""
    data = request.get_json(silent=True) or {}
    texts = data.get('texts')
    if not isinstance(texts, list):
        return jsonify(ok=False, error="'texts' must be a list of strings."), 400
    analysis = perform_analysis(texts)
    return jsonify(ok=True, analysis=analysis)

def generate_voice_verdict(score, pros, cons):
    """
    Generates a concise verdict summary for voice output.
    
    Args:
        score: The worth-to-buy score (0-100)
        pros: List of positive aspects with their sentiment scores
        cons: List of negative aspects with their sentiment scores
        
    Returns:
        A string with the verdict summary suitable for voice output
    """
    # Determine recommendation based on score
    if score >= 70:
        recommendation = "recommended"
    elif score >= 50:
        recommendation = "acceptable"
    else:
        recommendation = "not recommended"
    
    # Format the verdict
    verdict = f"This product is {recommendation} with a score of {round(score)}%."
    
    # Add pros if available
    if pros:
        pros_text = ", ".join([aspect for aspect, _ in pros])
        verdict += f" Customers love the {pros_text}."
    
    # Add cons if available
    if cons:
        cons_text = ", ".join([aspect for aspect, _ in cons])
        verdict += f" However, they complain about the {cons_text}."
    
    return verdict

if __name__ == '__main__':
    app.run(debug=True)