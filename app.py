from flask import Flask, render_template, request
from scraper import scrape_reviews
from analyzer import perform_analysis

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main page with the submission form."""
    return render_template('index.html')

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

    # 1. Scrape reviews
    reviews = scrape_reviews(product_url)
    if reviews is None:
        return render_template('error.html', message=f"Failed to scrape the URL. It might be invalid or the site may be blocking scrapers.")
    if not reviews:
        return render_template('error.html', message="No reviews were found on the page.")

    # 2. Perform analysis
    analysis_results = perform_analysis(reviews)

    # 3. Calculate 'Worth-to-Buy' Score
    score = 0
    overall = analysis_results.get("overall_sentiment", {})
    aspects = analysis_results.get("aspect_sentiments", {})
    
    total_reviews = sum(overall.values())
    if total_reviews > 0:
        positive_ratio = overall.get("positive", 0) / total_reviews
    else:
        positive_ratio = 0

    if aspects:
        # Normalize average aspect sentiment from [-1, 1] to [0, 1]
        avg_aspect_sentiment = sum(aspects.values()) / len(aspects)
        normalized_aspect_sentiment = (avg_aspect_sentiment + 1) / 2
    else:
        normalized_aspect_sentiment = 0.5 # Neutral assumption if no aspects found

    # Formula: 70% from positive review ratio, 30% from aspect sentiment
    score = (positive_ratio * 0.7 + normalized_aspect_sentiment * 0.3) * 100

    # 4. Generate Pros and Cons
    sorted_aspects = sorted(aspects.items(), key=lambda item: item[1], reverse=True)
    
    pros = sorted_aspects[:2]
    cons = sorted_aspects[-2:]
    cons.reverse() # Show the most negative first

    return render_template(
        'results.html',
        score=round(score),
        pros=pros,
        cons=cons,
        analysis=analysis_results,
        product_url=product_url
    )

if __name__ == '__main__':
    app.run(debug=True)
