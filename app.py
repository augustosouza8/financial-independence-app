# app.py
from flask import Flask, render_template

# Initialize the Flask application
app = Flask(__name__)

# Set a secret key for session management and flash messages.
# In a production environment, use a secure and unpredictable key.
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    """
    Home route that renders the main page.
    """
    return render_template('index.html')

if __name__ == '__main__':
    # Run the app in debug mode for development.
    # Remove debug=True when deploying to production.
    app.run(debug=True, port=5001)
