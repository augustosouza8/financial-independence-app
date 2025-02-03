# app.py
from flask import Flask, render_template, request, redirect, flash, url_for, session

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key in production


def parse_localized_number(s):
    """
    Converts a localized number string (e.g., "1.234,56") to a float.
    Assumes dot (.) is used as the thousands separator and comma (,) as the decimal separator.
    If the string is empty, returns 0.0.
    """
    if not s:
        return 0.0
    try:
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except ValueError:
        return None


def format_currency(value):
    """
    Formats a float into a currency string with dot as thousands separator and comma as decimal separator.
    For example, 1234.56 becomes "1.234,56".
    """
    formatted = f"{value:,.2f}"  # Example: "1,234.56"
    # Swap the separators: temporarily replace commas, then periods, then the temporary marker.
    formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted


@app.route('/')
def index():
    """
    Home route that renders the main page with the input form.
    Uses session values if they exist, otherwise defaults.
    """
    monthly_savings = session.get('monthly_savings', '3.000,00')
    initial_investment = session.get('initial_investment', '10.000,00')
    annual_rate = session.get('annual_rate', '6,00')
    safe_withdrawal_rate = session.get('safe_withdrawal_rate', '4,00')
    return render_template('index.html',
                           monthly_savings=monthly_savings,
                           initial_investment=initial_investment,
                           annual_rate=annual_rate,
                           safe_withdrawal_rate=safe_withdrawal_rate)


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Route to process form submission:
    - Retrieves and validates inputs.
    - Stores the submitted values in session so they persist when returning to the form.
    - Calculates future value and monthly passive income using discrete compounding.
    - Renders the results page.
    """
    # Retrieve form values and remove any extra whitespace.
    monthly_savings_str = request.form.get('monthly_savings', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()

    # Store submitted values in session (or default if empty)
    session['monthly_savings'] = monthly_savings_str if monthly_savings_str else "3.000,00"
    session['initial_investment'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"

    # Convert localized strings to float values for calculations.
    monthly_savings = parse_localized_number(monthly_savings_str) if monthly_savings_str else 0.0
    initial_investment = parse_localized_number(initial_investment_str) if initial_investment_str else 0.0
    annual_rate = parse_localized_number(annual_rate_str) if annual_rate_str else None
    safe_withdrawal_rate = parse_localized_number(safe_withdrawal_rate_str) if safe_withdrawal_rate_str else 4.0

    # Validate Annual Return Rate (must be greater than 0)
    if annual_rate is None or annual_rate <= 0:
        flash("Please enter a valid Annual Return Rate greater than 0.", "danger")
        return redirect(url_for('index'))

    # Validate Safe Withdrawal Rate (must be greater than 0)
    if safe_withdrawal_rate is None or safe_withdrawal_rate <= 0:
        flash("Please enter a valid Safe Withdrawal Rate greater than 0.", "danger")
        return redirect(url_for('index'))

    # Ensure that at least one of Monthly Savings or Initial Investment is provided.
    if monthly_savings <= 0 and initial_investment <= 0:
        flash("Please provide a value for either Monthly Savings or Initial Investment.", "danger")
        return redirect(url_for('index'))

    # Calculate the monthly interest rate using discrete compounding:
    # r = (1 + annual_rate/100)^(1/12) - 1
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    # Define investment durations in years.
    durations = [10, 20, 30, 40]
    results = []

    for years in durations:
        n = years * 12  # total number of months
        try:
            # Calculate the Future Value (FV):
            # FV = PV*(1 + r)^n + PMT * (((1 + r)^n - 1) / r)
            fv = initial_investment * (1 + monthly_rate) ** n + \
                 monthly_savings * (((1 + monthly_rate) ** n - 1) / monthly_rate)
        except ZeroDivisionError:
            flash("An error occurred during calculation (division by zero).", "danger")
            return redirect(url_for('index'))

        # Calculate Monthly Passive Income using the provided safe withdrawal rate:
        # monthly_income = FV * ((safe_withdrawal_rate/100) / 12)
        monthly_income = fv * ((safe_withdrawal_rate / 100) / 12)

        results.append({
            "years": years,
            "future_value": format_currency(fv),
            "monthly_income": format_currency(monthly_income)
        })

    return render_template('result.html', results=results,
                           monthly_savings=session['monthly_savings'],
                           initial_investment=session['initial_investment'],
                           annual_rate=session['annual_rate'],
                           safe_withdrawal_rate=session['safe_withdrawal_rate'])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
