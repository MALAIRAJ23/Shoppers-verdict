import sys
import flask

def test_flask():
    print("Python version:", sys.version)
    print("Flask version:", flask.__version__)
    
    app = flask.Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello, Flask is working!"
    
    print("Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    test_flask()
