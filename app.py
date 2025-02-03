"""
app.py

This is the main Flask application file for the Financial Independence Calculators project.
It includes routes for:
  - Home page: Letting the user choose between Calculator 1 and Calculator 2.
  - Calculator 1 ("calculator-1-user-set-monthly-investment"):
       Determines the future investment value and monthly passive income based on a user-set monthly investment.
  - Calculator 2 ("calculator-2-user-set-future-monthly-income"):
       Calculates the required monthly investment to achieve a target future monthly retirement income.

The application uses session storage to persist form inputs between requests.
"""

from flask import Flask, render_template, request, redirect, flash, url_for, session

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
        # Remove thousands separator and replace comma with period for float conversion.
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except ValueError:
        return None


def format_currency(value):
    """
    Formats a float into a currency string with dot as thousands separator and comma as decimal separator.
    For example, 1234.56 becomes "1.234,56".
    """
    formatted = f"{value:,.2f}"  # Format using US conventions, e.g. "1,234.56"
    # Swap the comma and period to match the desired localization.
    formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted


# -------------------------------------------------------------
# Home Page Route
# -------------------------------------------------------------
@app.route('/')
def home():
    """
    Renders the Home Page where users can choose between Calculator 1 and Calculator 2.
    """
    return render_template('home.html')


# -------------------------------------------------------------
# Calculator 1: Monthly Investment Calculator
# -------------------------------------------------------------
@app.route('/calculator-1-user-set-monthly-investment')
def calculator1_index():
    """
    Renders the input form for Calculator 1.
    Pre-fills form values with data from the session or defaults if not available.
    """
    monthly_savings = session.get('monthly_savings', '3.000,00')
    initial_investment = session.get('initial_investment', '10.000,00')
    annual_rate = session.get('annual_rate', '6,00')
    safe_withdrawal_rate = session.get('safe_withdrawal_rate', '4,00')
    return render_template('calculator1_index.html',
                           monthly_savings=monthly_savings,
                           initial_investment=initial_investment,
                           annual_rate=annual_rate,
                           safe_withdrawal_rate=safe_withdrawal_rate)


@app.route('/calculator-1-user-set-monthly-investment/calculate', methods=['POST'])
def calculator1_calculate():
    """
    Processes form submission for Calculator 1:
      - Retrieves and validates user inputs.
      - Stores inputs in the session for persistence.
      - Calculates the future value (FV) and monthly passive income using the annuity formula:
            FV = PV*(1 + r)^n + PMT * [((1 + r)^n - 1) / r]
        and computes the monthly income as:
            Monthly Income = FV * ((safe_withdrawal_rate/100) / 12)
      - Displays results for durations of 10, 15, 20, 25, 30, 35, 40, 45, and 50 years.
    """
    # Retrieve and trim inputs
    monthly_savings_str = request.form.get('monthly_savings', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()

    # Store values in session (or use defaults if empty)
    session['monthly_savings'] = monthly_savings_str if monthly_savings_str else "3.000,00"
    session['initial_investment'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"

    # Convert localized strings to float values
    monthly_savings = parse_localized_number(monthly_savings_str) if monthly_savings_str else 0.0
    initial_investment = parse_localized_number(initial_investment_str) if initial_investment_str else 0.0
    annual_rate = parse_localized_number(annual_rate_str) if annual_rate_str else None
    safe_withdrawal_rate = parse_localized_number(safe_withdrawal_rate_str) if safe_withdrawal_rate_str else 4.0

    # Validate inputs
    if annual_rate is None or annual_rate <= 0:
        flash("Please enter a valid Annual Return Rate greater than 0.", "danger")
        return redirect(url_for('calculator1_index'))
    if safe_withdrawal_rate is None or safe_withdrawal_rate <= 0:
        flash("Please enter a valid Safe Withdrawal Rate greater than 0.", "danger")
        return redirect(url_for('calculator1_index'))
    if monthly_savings <= 0 and initial_investment <= 0:
        flash("Please provide a value for either Monthly Savings or Initial Investment.", "danger")
        return redirect(url_for('calculator1_index'))

    # Calculate the monthly interest rate using discrete compounding:
    # r = (1 + annual_rate/100)^(1/12) - 1
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    # Define investment durations (in years)
    durations = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []
    for years in durations:
        n = years * 12  # total number of months
        try:
            # Future Value calculation using annuity formula
            fv = initial_investment * (1 + monthly_rate) ** n + \
                 monthly_savings * (((1 + monthly_rate) ** n - 1) / monthly_rate)
        except ZeroDivisionError:
            flash("An error occurred during calculation (division by zero).", "danger")
            return redirect(url_for('calculator1_index'))

        # Calculate Monthly Passive Income:
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


# -------------------------------------------------------------
# Calculator 2: Future Monthly Income Calculator
# -------------------------------------------------------------
@app.route('/calculator-2-user-set-future-monthly-income')
def calculator2_index():
    """
    Renders the input form for Calculator 2.
    Users can input:
      - Target Future Monthly Retirement Passive Income (default: "7.000,00")
      - Initial Investment (default: "10.000,00", optional)
      - Annual Return Rate (%) (default: "6,00")
      - Safe Withdrawal Rate (%) (default: "4,00")
    """
    target_income = session.get('target_income', '7.000,00')
    initial_investment = session.get('initial_investment_c2', '10.000,00')
    annual_rate = session.get('annual_rate_c2', '6,00')
    safe_withdrawal_rate = session.get('safe_withdrawal_rate_c2', '4,00')
    return render_template('calculator2_index.html',
                           target_income=target_income,
                           initial_investment=initial_investment,
                           annual_rate=annual_rate,
                           safe_withdrawal_rate=safe_withdrawal_rate)


@app.route('/calculator-2-user-set-future-monthly-income/calculate', methods=['POST'])
def calculator2_calculate():
    """
    Processes the form submission for Calculator 2:
      - Retrieves and validates user inputs.
      - Stores values in session (using distinct keys for Calculator 2).
      - Calculates the required monthly investment (PMT) needed to achieve the target future monthly retirement income.
      - Uses the rearranged future value formula:
            PMT = (R - PV*(1 + r)^n) / [((1 + r)^n - 1) / r]
        where R = target_income * 1200 / safe_withdrawal_rate.
      - If PMT is negative, displays a message indicating that no additional investment is needed.
      - Displays results for durations of 10, 15, 20, 25, 30, 35, 40, 45, and 50 years.
    """
    # Retrieve and trim inputs
    target_income_str = request.form.get('target_income', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()

    # Store inputs in session using distinct keys for Calculator 2
    session['target_income'] = target_income_str if target_income_str else "7.000,00"
    session['initial_investment_c2'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate_c2'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate_c2'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"

    # Convert inputs to float values
    target_income = parse_localized_number(target_income_str)
    initial_investment = parse_localized_number(initial_investment_str) if initial_investment_str else 0.0
    annual_rate = parse_localized_number(annual_rate_str) if annual_rate_str else None
    safe_withdrawal_rate = parse_localized_number(safe_withdrawal_rate_str) if safe_withdrawal_rate_str else 4.0

    # Validate inputs
    if target_income is None or target_income <= 0:
        flash("Please enter a valid Target Future Monthly Retirement Passive Income greater than 0.", "danger")
        return redirect(url_for('calculator2_index'))
    if annual_rate is None or annual_rate <= 0:
        flash("Please enter a valid Annual Return Rate greater than 0.", "danger")
        return redirect(url_for('calculator2_index'))
    if safe_withdrawal_rate is None or safe_withdrawal_rate <= 0:
        flash("Please enter a valid Safe Withdrawal Rate greater than 0.", "danger")
        return redirect(url_for('calculator2_index'))

    # Calculate monthly interest rate using discrete compounding:
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    # Calculate the required accumulated amount (R) such that safe withdrawal yields the target income:
    # R = target_income * 1200 / safe_withdrawal_rate
    R = target_income * 1200 / safe_withdrawal_rate

    # Define durations (in years)
    durations = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []
    for years in durations:
        n = years * 12  # total number of months
        # Calculate compounded value of the initial investment
        compounded_initial = initial_investment * (1 + monthly_rate) ** n
        # Calculate annuity factor: ((1 + r)^n - 1) / r
        annuity_factor = ((1 + monthly_rate) ** n - 1) / monthly_rate
        try:
            pmt = (R - compounded_initial) / annuity_factor
        except ZeroDivisionError:
            flash("An error occurred during calculation (division by zero).", "danger")
            return redirect(url_for('calculator2_index'))

        # Handle negative PMT by displaying an informational message.
        if pmt < 0:
            required_investment_display = "Already retired! (No additional investment needed)"
        else:
            required_investment_display = format_currency(pmt)

        results.append({
            "years": years,
            "required_investment": required_investment_display
        })

    return render_template('calculator2_result.html', results=results,
                           target_income=session['target_income'],
                           initial_investment=session['initial_investment_c2'],
                           annual_rate=session['annual_rate_c2'],
                           safe_withdrawal_rate=session['safe_withdrawal_rate_c2'])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
