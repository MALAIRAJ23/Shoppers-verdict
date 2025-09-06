@echo off
echo Starting Flask application...
python -c "import os; os.environ['FLASK_APP'] = 'app.py'; os.environ['FLASK_DEBUG'] = '1'; import flask; print(f'Flask version: {flask.__version__}'); from app import app; print('Flask app imported successfully'); print('Starting server...'); app.run(host='0.0.0.0', port=5000, debug=True)"
pause
