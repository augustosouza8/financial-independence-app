"""
app.py

This is the main Flask application for the Financial Independence Calculators project.
It defines routes for three calculators:
  - Calculator 1: User-set Monthly Investment Calculator.
  - Calculator 2: User-set Future Monthly Income Calculator.
  - Calculator 3: Monthly Savings Potential Calculator.
It also includes a Home page for users to choose which calculator to use.
User input values are stored in the session to pre-fill forms on subsequent visits.
"""

from flask import Flask, render_template, request, redirect, flash, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key in production

def parse_localized_number(s):
    """
    Converts a localized number string (e.g., "1.234,56") to a float.
    Assumes dot (.) is used as the thousands separator and comma (,) as the decimal separator.
    Returns 0.0 if the string is empty.
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
    formatted = f"{value:,.2f}"  # Format using US conventions (e.g., "1,234.56")
    formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted

# -------------------------------------------------------------
# Home Page Route
# -------------------------------------------------------------
@app.route('/')
def home():
    """
    Renders the Home page, allowing the user to choose among the three calculators.
    """
    return render_template('home.html')

# -------------------------------------------------------------
# Calculator 1: User-Set Monthly Investment Calculator
# -------------------------------------------------------------
@app.route('/calculator-1-user-set-monthly-investment')
def calculator1_index():
    """
    Renders the input form for Calculator 1.
    Pre-fills fields using session values or defaults.
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
    Processes the form submission for Calculator 1.
    Calculates future investment value and projected monthly passive income over various durations.
    Uses the annuity formula:
      FV = PV*(1 + r)^n + PMT * (((1 + r)^n - 1)/r)
      Monthly Income = FV * ((safe_withdrawal_rate/100) / 12)
    Durations: 10, 15, 20, 25, 30, 35, 40, 45, and 50 years.
    """
    # Retrieve form inputs
    monthly_savings_str = request.form.get('monthly_savings', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()

    # Store inputs in session (using defaults if empty)
    session['monthly_savings'] = monthly_savings_str if monthly_savings_str else "3.000,00"
    session['initial_investment'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"

    # Parse inputs
    monthly_savings = parse_localized_number(monthly_savings_str) if monthly_savings_str else 0.0
    initial_investment = parse_localized_number(initial_investment_str) if initial_investment_str else 0.0
    annual_rate = parse_localized_number(annual_rate_str) if annual_rate_str else None
    safe_withdrawal_rate = parse_localized_number(safe_withdrawal_rate_str) if safe_withdrawal_rate_str else 4.0

    # Validate required fields
    if annual_rate is None or annual_rate <= 0:
        flash("Please enter a valid Annual Return Rate greater than 0.", "danger")
        return redirect(url_for('calculator1_index'))
    if safe_withdrawal_rate is None or safe_withdrawal_rate <= 0:
        flash("Please enter a valid Safe Withdrawal Rate greater than 0.", "danger")
        return redirect(url_for('calculator1_index'))
    if monthly_savings <= 0 and initial_investment <= 0:
        flash("Please provide a value for either Monthly Savings or Initial Investment.", "danger")
        return redirect(url_for('calculator1_index'))

    # Calculate monthly interest rate using discrete compounding
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    # Define durations (years)
    durations = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []
    for years in durations:
        n = years * 12
        try:
            fv = initial_investment * (1 + monthly_rate) ** n + \
                 monthly_savings * (((1 + monthly_rate) ** n - 1) / monthly_rate)
        except ZeroDivisionError:
            flash("An error occurred during calculation (division by zero).", "danger")
            return redirect(url_for('calculator1_index'))
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
    Users input target future monthly retirement income, optional initial investment,
    annual return rate, and safe withdrawal rate.
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
    Processes form submission for Calculator 2.
    Calculates the required monthly investment (PMT) to achieve the target future monthly retirement income.
    Uses the rearranged future value formula:
      PMT = (R - PV*(1 + r)^n) / [((1 + r)^n - 1)/r]
    where R = target_income * 1200 / safe_withdrawal_rate.
    If PMT is negative, a message is displayed indicating that no additional investment is needed.
    """
    # Retrieve and trim inputs
    target_income_str = request.form.get('target_income', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()

    # Store inputs in session (using distinct keys for Calculator 2)
    session['target_income'] = target_income_str if target_income_str else "7.000,00"
    session['initial_investment_c2'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate_c2'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate_c2'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"

    # Parse inputs
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

    # Calculate monthly interest rate
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    # Calculate required accumulated amount R such that safe withdrawal yields the target income
    R = target_income * 1200 / safe_withdrawal_rate

    # Define durations
    durations = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []
    for years in durations:
        n = years * 12
        compounded_initial = initial_investment * (1 + monthly_rate) ** n
        annuity_factor = ((1 + monthly_rate) ** n - 1) / monthly_rate
        try:
            pmt = (R - compounded_initial) / annuity_factor
        except ZeroDivisionError:
            flash("An error occurred during calculation (division by zero).", "danger")
            return redirect(url_for('calculator2_index'))
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

# -------------------------------------------------------------
# Calculator 3: Monthly Savings Potential Calculator
# -------------------------------------------------------------
@app.route('/calculator-3-user-set-monthly-savings')
def calculator3_index():
    """
    Renders the input form for Calculator 3.
    Users enter their salary after taxes (required) and various expense categories (optional).
    The calculator computes the available monthly savings as:
         Savings = Salary after taxes - (Sum of expenses)
    """
    salary = session.get('salary', '')
    housing = session.get('housing', '')
    utilities = session.get('utilities', '')
    transportation = session.get('transportation', '')
    food = session.get('food', '')
    hobbies = session.get('hobbies', '')
    subscriptions = session.get('subscriptions', '')
    healthcare = session.get('healthcare', '')
    debt = session.get('debt', '')
    other = session.get('other', '')
    return render_template('calculator3_index.html',
                           salary=salary,
                           housing=housing,
                           utilities=utilities,
                           transportation=transportation,
                           food=food,
                           hobbies=hobbies,
                           subscriptions=subscriptions,
                           healthcare=healthcare,
                           debt=debt,
                           other=other)

@app.route('/calculator-3-user-set-monthly-savings/calculate', methods=['POST'])
def calculator3_calculate():
    """
    Processes the form submission for Calculator 3.
    Calculates the available monthly savings by subtracting total expenses from the salary after taxes.
    If the result is negative, it displays a "Deficit" message.
    """
    # Retrieve and trim inputs
    salary_str = request.form.get('salary', '').strip()
    housing_str = request.form.get('housing', '').strip()
    utilities_str = request.form.get('utilities', '').strip()
    transportation_str = request.form.get('transportation', '').strip()
    food_str = request.form.get('food', '').strip()
    hobbies_str = request.form.get('hobbies', '').strip()
    subscriptions_str = request.form.get('subscriptions', '').strip()
    healthcare_str = request.form.get('healthcare', '').strip()
    debt_str = request.form.get('debt', '').strip()
    other_str = request.form.get('other', '').strip()

    # Store inputs in session
    session['salary'] = salary_str
    session['housing'] = housing_str
    session['utilities'] = utilities_str
    session['transportation'] = transportation_str
    session['food'] = food_str
    session['hobbies'] = hobbies_str
    session['subscriptions'] = subscriptions_str
    session['healthcare'] = healthcare_str
    session['debt'] = debt_str
    session['other'] = other_str

    # Parse required salary input
    salary = parse_localized_number(salary_str)
    if salary is None or salary <= 0:
        flash("Please enter a valid Salary after taxes (must be greater than 0).", "danger")
        return redirect(url_for('calculator3_index'))

    # Parse optional expense inputs; default to 0 if empty
    housing_val = parse_localized_number(housing_str) if housing_str else 0.0
    utilities_val = parse_localized_number(utilities_str) if utilities_str else 0.0
    transportation_val = parse_localized_number(transportation_str) if transportation_str else 0.0
    food_val = parse_localized_number(food_str) if food_str else 0.0
    hobbies_val = parse_localized_number(hobbies_str) if hobbies_str else 0.0
    subscriptions_val = parse_localized_number(subscriptions_str) if subscriptions_str else 0.0
    healthcare_val = parse_localized_number(healthcare_str) if healthcare_str else 0.0
    debt_val = parse_localized_number(debt_str) if debt_str else 0.0
    other_val = parse_localized_number(other_str) if other_str else 0.0

    # Calculate total expenses and available savings
    total_expenses = (housing_val + utilities_val + transportation_val +
                      food_val + hobbies_val + subscriptions_val +
                      healthcare_val + debt_val + other_val)
    savings = salary - total_expenses

    # Format the result; if negative, show as a deficit
    if savings < 0:
        result_display = "Deficit: " + format_currency(abs(savings))
    else:
        result_display = format_currency(savings)

    return render_template('calculator3_result.html',
                           result=result_display,
                           salary=session['salary'],
                           housing=session['housing'],
                           utilities=session['utilities'],
                           transportation=session['transportation'],
                           food=session['food'],
                           hobbies=session['hobbies'],
                           subscriptions=session['subscriptions'],
                           healthcare=session['healthcare'],
                           debt=session['debt'],
                           other=session['other'])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
