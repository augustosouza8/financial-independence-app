# Financial Independence Calculators
A Flask-based web application that helps users plan their financial independence by providing two powerful calculators for retirement planning.

## Features
- Calculator 1: Determine future investment value based on monthly savings
- Calculator 2: Calculate required monthly investment for target retirement income
- Supports custom initial investments
- Calculations for investment durations from 10 to 50 years
- Localized number formatting
- Responsive web interface using Bootstrap
- Error handling and user feedback
- Persistent session storage for form inputs

## Technologies Used
- Python 3.x
- Flask 3.1.0
- Bootstrap 5.3.0
- Gunicorn (for production deployment)
- Supports localized number parsing

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/financial-independence-app.git
cd financial-independence-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Start the development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5001
```

3. Use the web interface to:
   - Calculate future investment value (Calculator 1)
   - Determine required monthly investment (Calculator 2)
   - Set initial investment, annual return rate, and safe withdrawal rate
   - View projections for multiple investment durations

## Project Structure
```
financial-independence-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Project dependencies
└── templates/
    ├── home.html          # Home page with calculator selection
    ├── calculator1_index.html  # Calculator 1 input form
    ├── calculator2_index.html  # Calculator 2 input form
    ├── result.html        # Results for Calculator 1
    └── calculator2_result.html  # Results for Calculator 2
```

## Calculation Methodology
The application uses advanced financial formulas to calculate:
- Future investment value
- Compound interest projections
- Safe withdrawal rate calculations
- Required monthly investments

Key calculations include:
- Annuity formula for investment growth
- Discrete compounding interest calculations
- Safe withdrawal rate projections

## Error Handling
The application includes comprehensive error handling for:
- Invalid number inputs
- Zero or negative rate inputs
- Calculation edge cases
- User input validation

## Development
### Running in Debug Mode
```bash
flask run --debug --port=5001
```

### Adding New Features
1. Create a new branch for your feature
2. Implement the feature
3. Test thoroughly
4. Submit a pull request

## Production Deployment

### Deploying to Render (Free Tier)
This application includes a `render.yaml` file, making it incredibly easy to deploy to [Render.com](https://render.com/).

1. Create a GitHub repository and push your code (ensure `.env` is **not** committed).
2. Log in to Render and create a new **Blueprint Instance**.
3. Connect your GitHub repository.
4. Render will automatically detect the `render.yaml` configuration and deploy the app.
5. Render will generate a secure `SECRET_KEY` automatically.

*Note: Render's free tier spins down the server after 15 minutes of inactivity. The first request after a spin-down may take ~50 seconds to load.*

### Manual Gunicorn Deployment
If deploying manually to another server:
```bash
# 1. Ensure you have a .env file with a secure SECRET_KEY
cp .env.example .env

# 2. Run with Gunicorn
gunicorn app:app
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Built with assistance from ChatGPT ([click here to access the main used chat](https://chatgpt.com/share/67a112fe-0794-8013-beb1-6d258cae37a8))
- Inspired by financial independence planning tools
- Developed to help users visualize the financial independence journey 
- Deployed by Augusto
