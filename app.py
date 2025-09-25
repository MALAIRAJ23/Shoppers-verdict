from flask import Flask, render_template, request, jsonify
<<<<<<< HEAD
from flask_cors import CORS
from enhanced_scraper import scrape_data
from analyzer import perform_analysis, analyze_product_description
import traceback
import time
=======
from scraper import scrape_data
from analyzer import perform_analysis, analyze_product_description
import traceback
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887

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

<<<<<<< HEAD
# Enable CORS for browser extension
CORS(app, origins=['*'], allow_headers=['Content-Type'], methods=['GET', 'POST', 'OPTIONS'])

# Apply the middleware
app.wsgi_app = ExceptionMiddleware(app.wsgi_app)

@app.route('/', methods=['GET', 'POST'])
=======
# Apply the middleware
app.wsgi_app = ExceptionMiddleware(app.wsgi_app)

@app.route('/')

>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887
def index():
    """Renders the main page with the submission form or processes analysis requests."""
    # Handle GET requests with URL parameter (from extension)
    if request.method == 'GET':
        product_url = request.args.get('url')
        if product_url:
            # Process the URL and redirect to analysis
            return analyze_product(product_url)
        else:
            # Show the main form
            return render_template('index.html')
    
    # Handle POST requests from the form
    else:
        product_url = request.form.get('product_url')
        if not product_url:
            return render_template('error.html', message="No product URL was provided.")
        return analyze_product(product_url)

@app.route('/features')
def features():
    """Features hub page with interactive feature cards."""
    return render_template('features.html')

def analyze_product(product_url):
    """Common analysis logic for both GET and POST requests."""
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
    
    # 6. Get product recommendations if available
    product_recommendations = []
    try:
        from recommendation_engine import get_product_recommendations
        product_recommendations = get_product_recommendations(product_url, product_title, product_description, limit=5)
    except Exception as e:
        print(f"Recommendation engine not available: {e}")
        # Continue without recommendations

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
        insight=insight,
        recommendations=product_recommendations
    )

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
<<<<<<< HEAD
    
    return analyze_product(product_url)

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

@app.route('/api/extension/analyze', methods=['POST', 'OPTIONS'])
def api_extension_analyze():
    """API: Extension endpoint for product analysis with recommendations."""
    if request.method == 'OPTIONS':
        return jsonify(ok=True)
    
    try:
        data = request.get_json(silent=True) or {}
        product_url = data.get('url', '').strip()
        include_recommendations = data.get('include_recommendations', False)
        
        if not product_url:
            return jsonify(ok=False, error="Missing 'url' parameter"), 400
            
        # Normalize URL
        if not product_url.lower().startswith(('http://', 'https://')):
            product_url = 'https://' + product_url.lstrip('/ ')
        
        # Add timeout protection for scraping
        try:
            # 1. Scrape data
            start_time = time.time()
            print(f"Extension API: Starting analysis for {product_url}")
            
            data = scrape_data(product_url)
            
        except Exception as scrape_error:
            print(f"Scraping failed: {str(scrape_error)}")
            
            # Enhanced fallback for Amazon - provide intelligent analysis even without reviews
            if 'amazon' in product_url.lower():
                print("Amazon scraping failed - generating enhanced fallback analysis")
                
                # Extract product information from URL
                import re
                from urllib.parse import unquote
                
                # Try to get ASIN
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
                asin = asin_match.group(1) if asin_match else None
                
                # Extract category/keywords from URL
                url_decoded = unquote(product_url).lower()
                
                # Determine product category and generate appropriate analysis
                category_analysis = {
                    'electronics': {
                        'keywords': ['mobile', 'phone', 'laptop', 'computer', 'tv', 'headphone', 'speaker', 'tablet', 'camera'],
                        'base_score': 72,
                        'pros': [['features', 0.6], ['brand_reliability', 0.5], ['warranty', 0.4]],
                        'cons': [['price', -0.3], ['delivery_time', -0.2]]
                    },
                    'home_appliances': {
                        'keywords': ['refrigerator', 'washing', 'microwave', 'iron', 'cooker', 'mixer', 'grinder'],
                        'base_score': 70,
                        'pros': [['functionality', 0.7], ['durability', 0.6], ['energy_efficiency', 0.4]],
                        'cons': [['installation', -0.3], ['maintenance', -0.2]]
                    },
                    'fashion': {
                        'keywords': ['shirt', 'dress', 'shoe', 'watch', 'bag', 'clothing', 'apparel'],
                        'base_score': 62,
                        'pros': [['design', 0.6], ['material', 0.5], ['style', 0.4]],
                        'cons': [['sizing', -0.4], ['color_accuracy', -0.2]]
                    },
                    'books': {
                        'keywords': ['book', 'novel', 'guide', 'textbook'],
                        'base_score': 75,
                        'pros': [['content', 0.7], ['printing_quality', 0.5]],
                        'cons': [['delivery_condition', -0.2]]
                    },
                    'health': {
                        'keywords': ['vitamin', 'supplement', 'medicine', 'health', 'fitness'],
                        'base_score': 68,
                        'pros': [['effectiveness', 0.6], ['quality', 0.5]],
                        'cons': [['price', -0.3], ['availability', -0.2]]
                    }
                }
                
                detected_category = 'general'
                category_info = {
                    'base_score': 65,
                    'pros': [['quality', 0.5], ['value', 0.4]],
                    'cons': [['availability', -0.2], ['shipping', -0.1]]
                }
                
                # Detect category
                for category, info in category_analysis.items():
                    if any(keyword in url_decoded for keyword in info['keywords']):
                        detected_category = category
                        category_info = info
                        break
                
                # Amazon typically has reliable products, slight bonus
                base_score = category_info['base_score'] + 3
                base_score = min(85, max(45, base_score))
                
                recommendation = 'Recommended' if base_score >= 70 else 'Acceptable' if base_score >= 50 else 'Consider Alternatives'
                
                product_title = f"Amazon Product"
                if asin:
                    product_title = f"Amazon Product (ASIN: {asin})"
                
                # Generate intelligent voice verdict
                voice_verdict = f"Amazon product analysis: This item scores {base_score}% based on category assessment and Amazon's platform reliability. Category: {detected_category.replace('_', ' ')}. Note: Detailed review analysis unavailable due to access restrictions, but Amazon's return policy and customer service provide additional confidence."
                
                return jsonify({
                    'ok': True,
                    'score': base_score,
                    'recommendation': recommendation,
                    'pros': category_info['pros'],
                    'cons': category_info['cons'],
                    'voice_verdict': voice_verdict,
                    'product_title': product_title,
                    'product_url': product_url,
                    'reviews_analyzed': 0,
                    'processing_time': round(time.time() - start_time, 2),
                    'recommendations': [],
                    'meta': {
                        'confidence': 0.6,
                        'data_quality': 0.4,
                        'analysis_type': 'category_based',
                        'platform': 'amazon',
                        'category': detected_category,
                        'note': 'Category-based analysis due to review access restrictions'
                    }
                })
            
            # Try to return cached data if available for other sites
            try:
                from enhanced_scraper import init_db
                init_db()
                # Try direct cache access
                import sqlite3
                import json
                from datetime import datetime, timedelta
                
                try:
                    with sqlite3.connect('reviews_cache.db') as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                        cursor.execute("SELECT reviews_json, timestamp FROM reviews WHERE url = ?", (product_url,))
                        review_row = cursor.fetchone()
                        if review_row:
                            timestamp = datetime.fromisoformat(review_row['timestamp'])
                            if datetime.now() - timestamp < timedelta(days=7):
                                cached_reviews = json.loads(review_row['reviews_json'])
                                if cached_reviews:
                                    print(f"Using cached data: {len(cached_reviews)} reviews")
                                    data = {'reviews': cached_reviews, 'title': 'Cached Product'}
                                else:
                                    return jsonify(ok=False, error='Failed to scrape product data and no cached data available'), 502
                            else:
                                return jsonify(ok=False, error='Failed to scrape product data and cached data expired'), 502
                        else:
                            return jsonify(ok=False, error='Failed to scrape product data and no cached data available'), 502
                except Exception as cache_error:
                    print(f"Cache access error: {cache_error}")
                    return jsonify(ok=False, error='Failed to scrape product data and cache access failed'), 502
            except Exception as fallback_error:
                print(f"Fallback error: {fallback_error}")
                return jsonify(ok=False, error='Failed to scrape product data or no reviews found'), 502
        
        if data is None or not data.get('reviews'):
            # For Amazon, check if we have title/description even without reviews
            if data and data.get('title') and 'amazon' in product_url:
                print(f"Amazon product found but no reviews. Title: {data.get('title')}")
                # Try to provide basic analysis based on product title and description
                return jsonify({
                    'ok': True,
                    'score': 60,  # Neutral score when no reviews
                    'recommendation': 'Insufficient Data',
                    'pros': [['features', 0.3]],
                    'cons': [['no_reviews', -0.1]],
                    'voice_verdict': f"Analysis for {data.get('title', 'this product')}: Unable to find customer reviews for detailed analysis. This product appears to be available but lacks sufficient review data.",
                    'product_title': data.get('title', 'Amazon Product'),
                    'product_url': product_url,
                    'reviews_analyzed': 0,
                    'processing_time': round(time.time() - start_time, 2),
                    'recommendations': [],
                    'meta': {
                        'confidence': 0.2,
                        'data_quality': 0.1,
                        'note': 'No reviews found - basic analysis only'
                    }
                })
            
            return jsonify(ok=False, error='Failed to scrape product data or no reviews found'), 502
        
        reviews = data['reviews']
        product_title = data.get('title', 'Unknown Product')
        product_description = data.get('description', '')
        
        print(f"Extension API: Found {len(reviews)} reviews for analysis")
        
        # 2. Perform analysis
        analysis_results = perform_analysis(reviews)
        description_analysis = analyze_product_description(product_description)
        
        # 3. Calculate worth-to-buy score (same logic as main route)
        overall = analysis_results.get("overall_sentiment", {})
        aspects = analysis_results.get("aspect_sentiments", {})
        meta = analysis_results.get('meta', {})
        
        total_reviews = sum(overall.values())
        reviews_used = meta.get('reviews_used', total_reviews)
        
        if total_reviews > 0:
            positive_ratio = overall.get("positive", 0) / total_reviews
            negative_ratio = overall.get("negative", 0) / total_reviews
            neutral_ratio = overall.get("neutral", 0) / total_reviews
        else:
            positive_ratio = negative_ratio = neutral_ratio = 0
        
        if aspects:
            avg_aspect_sentiment = sum(aspects.values()) / len(aspects)
            normalized_aspect_sentiment = (avg_aspect_sentiment + 1) / 2
            aspect_diversity_bonus = min(len(aspects) / 5.0, 1.0) * 0.05
            strong_negative_aspects = sum(1 for score in aspects.values() if score < -0.3)
            negative_penalty = strong_negative_aspects * 0.08
            strong_positive_aspects = sum(1 for score in aspects.values() if score > 0.3)
            positive_bonus = strong_positive_aspects * 0.05
        else:
            normalized_aspect_sentiment = 0.5
            aspect_diversity_bonus = 0
            negative_penalty = 0
            positive_bonus = 0
        
        data_quality_factor = min(reviews_used / 50.0, 1.0)
        quality_bonus = data_quality_factor * 0.05
        sentiment_consistency = 1 - (neutral_ratio * 0.3)
        
        base_score = positive_ratio * 0.6 + normalized_aspect_sentiment * 0.3 + quality_bonus + aspect_diversity_bonus
        adjusted_score = base_score + positive_bonus - negative_penalty
        final_score = adjusted_score * sentiment_consistency
        score = max(0, min(100, final_score * 100))
        
        # 4. Generate pros and cons
        sorted_desc = sorted(aspects.items(), key=lambda item: item[1], reverse=True)
        sorted_asc = list(reversed(sorted_desc))
        POS_TH = 0.05
        NEG_TH = -0.05
        pros = [(a, s) for a, s in sorted_desc if s >= POS_TH][:2]
        cons = [(a, s) for a, s in sorted_asc if s <= NEG_TH][:2]
        
        if len(pros) < 2:
            extras = [(a, s) for a, s in sorted_desc if (a, s) not in pros][:2 - len(pros)]
            pros.extend(extras)
        if len(cons) < 2:
            extras = [(a, s) for a, s in sorted_asc if (a, s) not in cons][:2 - len(cons)]
            cons.extend(extras)
        
        # 5. Generate voice verdict
        voice_verdict = generate_voice_verdict(score, pros, cons)
        
        # 6. Get recommendations if requested
        recommendations = []
        if include_recommendations:
            try:
                from recommendation_engine import get_product_recommendations
                recommendations = get_product_recommendations(product_url, product_title, product_description, limit=3)
            except Exception as e:
                print(f"Recommendation engine error: {e}")
                # Continue without recommendations
        
        processing_time = time.time() - start_time
        
        response_data = {
            'ok': True,
            'score': round(score),
            'recommendation': getRecommendationText(score),
            'pros': pros,
            'cons': cons,
            'voice_verdict': voice_verdict,
            'product_title': product_title,
            'product_url': product_url,
            'reviews_analyzed': reviews_used,
            'processing_time': round(processing_time, 2),
            'recommendations': recommendations,
            'meta': {
                'confidence': meta.get('confidence', 0),
                'data_quality': meta.get('avg_quality', 0)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Extension API error: {str(e)}")
        return jsonify(ok=False, error=str(e)), 500

@app.route('/api/extension/test', methods=['POST', 'OPTIONS'])
def api_extension_test():
    """API: Test endpoint for extension with demo data."""
    if request.method == 'OPTIONS':
        return jsonify(ok=True)
    
    try:
        # Use demo data for quick testing
        demo_reviews = [
            "Great product! Really satisfied with the quality and performance.",
            "Good value for money. Works as expected.",
            "Delivery was fast and packaging was excellent.",
            "Battery life could be better but overall good product.",
            "Camera quality is amazing, very happy with this purchase."
        ]
        
        # Perform analysis on demo data
        analysis_results = perform_analysis(demo_reviews)
        
        # Calculate score (simplified)
        overall = analysis_results.get("overall_sentiment", {})
        total_reviews = sum(overall.values())
        
        if total_reviews > 0:
            positive_ratio = overall.get("positive", 0) / total_reviews
            score = positive_ratio * 100
        else:
            score = 50
        
        # Generate pros and cons
        aspects = analysis_results.get("aspect_sentiments", {})
        sorted_aspects = sorted(aspects.items(), key=lambda x: x[1], reverse=True)
        
        pros = sorted_aspects[:2] if sorted_aspects else [('quality', 0.5)]
        cons = sorted_aspects[-2:] if len(sorted_aspects) > 2 else [('battery', -0.2)]
        
        # Generate voice verdict
        voice_verdict = f"This product scores {round(score)}% based on customer reviews. Customers appreciate the quality and performance."
        
        response_data = {
            'ok': True,
            'score': round(score),
            'recommendation': 'Recommended' if score >= 70 else 'Acceptable' if score >= 50 else 'Not Recommended',
            'pros': pros,
            'cons': cons,
            'voice_verdict': voice_verdict,
            'product_title': 'Demo Product',
            'product_url': 'https://demo-product-url.com',
            'reviews_analyzed': len(demo_reviews),
            'processing_time': 0.5,
            'recommendations': [],
            'meta': {
                'confidence': 0.8,
                'data_quality': 0.9
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Extension test API error: {str(e)}")
        return jsonify(ok=False, error=str(e)), 500
@app.route('/api/extension/health', methods=['GET', 'OPTIONS'])
def api_extension_health():
    """API: Health check endpoint for extension."""
    if request.method == 'OPTIONS':
        return jsonify(ok=True)
    
    return jsonify({
        'ok': True,
        'status': 'healthy',
        'version': '1.0.0',
        'features': {
            'analysis': True,
            'recommendations': True,
            'voice_verdict': True
        }
    })

def getRecommendationText(score):
    """Helper function to get recommendation text based on score."""
    if score >= 70:
        return 'Recommended'
    elif score >= 50:
        return 'Acceptable'
    else:
        return 'Not Recommended'

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
=======

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
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887

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
<<<<<<< HEAD
    app.run(debug=True, host='localhost', port=5000)
=======
    app.run(debug=True)
>>>>>>> e9414c5600577b26d2ed2f3aaecc1bee4790b887
