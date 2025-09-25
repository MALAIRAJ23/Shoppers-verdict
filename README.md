# Shopper's Verdict - AI-Powered Shopping Decision Assistant

An intelligent web application that analyzes product reviews to help users make informed shopping decisions. Using advanced NLP techniques, it provides comprehensive sentiment analysis, aspect-based evaluation, and generates a "Worth-to-Buy" score.

## 🚀 Features

### Core Functionality
- **Smart Review Analysis**: Scrapes and analyzes hundreds of product reviews automatically
- **Worth-to-Buy Score**: Generates a 0-100 score based on sentiment analysis and aspect evaluation
- **Pros & Cons Generation**: Automatically identifies top positive and negative aspects
- **Voice Verdict**: Text-to-speech functionality for accessibility
- **Price History Tracking**: Monitors price changes over time with visual charts
- **Aspect-based Sentiment**: Analyzes specific product features (battery, camera, build quality, etc.)

### AI Shopping Labs (Advanced Features)
- **Aspect Explorer**: Interactive tool to discover what customers discuss most
- **Price Insight Simulator**: Advanced price tracking with filtering and volatility analysis
- **Verdict Composer**: Customizable analysis with adjustable weights and thresholds

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework for API and routing
- **Python 3.10+**: Core language
- **Playwright**: Web scraping for dynamic content
- **spaCy**: Advanced NLP processing
- **VADER Sentiment**: Sentiment analysis engine
- **SQLite**: Local database for caching

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **Bootstrap 5**: UI framework
- **JavaScript**: Interactive features
- **Chart.js**: Price history visualization
- **Web Speech API**: Voice synthesis
- **GSAP**: Smooth animations

### Data Processing
- **NLTK**: Natural language processing
- **BeautifulSoup4**: HTML parsing
- **Numpy**: Numerical computations
- **Regex**: Text pattern matching

## 📁 Project Structure

```
shopper's-verdict/
├── app.py                 # Main Flask application
├── scraper.py             # Web scraping module
├── analyzer.py            # NLP analysis engine
├── requirements.txt       # Python dependencies
├── reviews_cache.db       # SQLite database
├── run_app.bat           # Windows launcher
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── results.html      # Analysis results
│   ├── features.html     # AI Labs interface
│   └── error.html        # Error handling
├── static/
│   └── css/
│       └── style.css     # Custom styling
├── venv/                 # Python virtual environment
└── __pycache__/          # Python cache files
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Windows/Linux/macOS
- Internet connection for web scraping

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shoppers-verdict
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the application**
   
   **Option A: Using batch file (Windows)**
   ```bash
   run_app.bat
   ```
   
   **Option B: Direct execution**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🎯 How to Use

### Basic Analysis
1. **Enter Product URL**: Paste a Flipkart or Amazon product URL
2. **Get Analysis**: Click "Get Verdict" to start processing
3. **View Results**: Review the worth-to-buy score, pros/cons, and detailed insights
4. **Voice Verdict**: Click the speaker icon to hear the verdict

### Advanced Features (AI Labs)
1. **Aspect Explorer**: Analyze what customers discuss most about products
2. **Price Simulator**: Track price history and analyze trends
3. **Verdict Composer**: Customize analysis parameters and generate personalized verdicts

## 🧠 How It Works

### Data Collection
1. **Web Scraping**: Uses Playwright to extract reviews from supported e-commerce sites
2. **Smart Caching**: Stores reviews locally to avoid repeated scraping (7-day cache)
3. **Price Tracking**: Continuously monitors and stores price changes

### NLP Analysis Pipeline
1. **Text Preprocessing**: Cleans and deduplicates review text
2. **Sentence Segmentation**: Breaks reviews into individual sentences
3. **Sentiment Analysis**: Uses VADER to score each sentence
4. **Aspect Extraction**: Identifies product features using spaCy NER and POS tagging
5. **Aspect-Sentiment Mapping**: Links aspects to their sentiment scores

### Score Calculation
- **70% Weight**: Overall positive review ratio
- **30% Weight**: Average aspect sentiment scores
- **Range**: 0-100 (higher = more worth buying)

### Intelligence Features
- **Robust Filtering**: Removes duplicate and low-quality reviews
- **Aspect Ranking**: Prioritizes aspects by support and sentiment magnitude
- **Dynamic Thresholds**: Adapts pros/cons detection based on data quality

## 🌐 Supported Platforms

- **Flipkart**: Full support for product reviews and pricing
- **Amazon**: Full support for product reviews and pricing
- **Generic Sites**: Basic review extraction (limited functionality)

## 📊 Database Schema

### Reviews Table
```sql
CREATE TABLE reviews (
    url TEXT PRIMARY KEY,
    reviews_json TEXT NOT NULL,
    timestamp DATETIME NOT NULL
);
```

### Price History Table
```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    price REAL NOT NULL,
    timestamp DATETIME NOT NULL
);
```

## 🔍 API Endpoints

### Web Interface
- `GET /` - Landing page
- `GET /features` - AI Labs interface
- `POST /analyze` - Main analysis endpoint

### API Endpoints
- `POST /api/scrape_preview` - Get review count and price history
- `POST /api/analyze_text` - Analyze custom text input

## 🎨 UI/UX Features

- **Glassmorphism Design**: Modern, clean interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Smooth animations and hover effects
- **Accessibility**: Voice synthesis and keyboard navigation
- **Visual Charts**: Price history graphs with Chart.js

## 🔧 Configuration

### Environment Variables
- `FLASK_APP=app.py`
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`

### Cache Settings
- **Cache Duration**: 7 days for reviews
- **Database**: SQLite (reviews_cache.db)
- **Auto-cleanup**: Expired entries handled automatically

## 📈 Performance Optimizations

- **Smart Caching**: Reduces redundant scraping operations
- **Async Processing**: Non-blocking web scraping with Playwright
- **Efficient NLP**: Optimized spaCy pipeline with fallbacks
- **Database Indexing**: Fast lookups with proper indexing
- **Frontend Optimization**: Lazy loading and progressive enhancement

## 🚨 Error Handling

- **Graceful Failures**: Comprehensive error catching and user feedback
- **Fallback Mechanisms**: Alternative processing when primary methods fail
- **User-Friendly Messages**: Clear error descriptions and suggestions
- **Debug Support**: Detailed logging for development

## 🛡️ Security Features

- **Input Validation**: URL sanitization and validation
- **XSS Protection**: Template escaping and input cleaning
- **Rate Limiting**: Prevents abuse through caching mechanisms
- **Error Information**: Secure error handling without exposing internals

## 🔮 Future Enhancements

### Planned Features
- **Multi-language Support**: Analysis in different languages
- **Comparison Tool**: Side-by-side product comparisons
- **User Accounts**: Save favorite analyses and track price drops
- **Mobile App**: Native mobile application
- **API Integration**: RESTful API for third-party integrations

### Technical Improvements
- **Cloud Deployment**: AWS/Azure hosting
- **Database Migration**: PostgreSQL for production
- **Microservices**: Separate scraping and analysis services
- **Machine Learning**: Custom sentiment models
- **Real-time Updates**: WebSocket integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Created as part of an NLP mini-project demonstrating practical applications of natural language processing in e-commerce.

## 🙏 Acknowledgments

- **spaCy**: For excellent NLP capabilities
- **VADER**: For robust sentiment analysis
- **Playwright**: For reliable web scraping
- **Flask**: For simple and effective web framework
- **Bootstrap**: For responsive UI components

---

**Shopper's Verdict** - Making shopping decisions smarter, one review at a time! 🛍️✨
