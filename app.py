"""
app.py

This is the main Flask application for the Financial Independence Calculators project.
It defines routes for three calculators:
  - Calculator 1: User-set Monthly Investment Calculator.
  - Calculator 2: User-set Future Monthly Income Calculator.
  - Calculator 3: Monthly Savings Potential Calculator.
"""

import os
import datetime
from flask import Flask, render_template, request, redirect, flash, url_for, session
from dotenv import load_dotenv

# Import utilities
from utils import parse_localized_number, calculate_calculator1, calculate_calculator2, calculate_calculator3

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use environment variable for secret key
app.secret_key = os.environ.get('SECRET_KEY', 'default_fallback_key')

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
    birth_year = session.get('birth_year', '')
    return render_template('calculator1_index.html',
                           monthly_savings=monthly_savings,
                           initial_investment=initial_investment,
                           annual_rate=annual_rate,
                           safe_withdrawal_rate=safe_withdrawal_rate,
                           birth_year=birth_year)

@app.route('/calculator-1-user-set-monthly-investment/calculate', methods=['POST'])
def calculator1_calculate():
    """
    Processes the form submission for Calculator 1.
    Calculates future investment value and projected monthly passive income over various durations.
    """
    monthly_savings_str = request.form.get('monthly_savings', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()
    birth_year_str = request.form.get('birth_year', '').strip()
    
    # Read period-specific savings from form
    period_savings_strs = request.form.getlist('period_savings')
    if not period_savings_strs:
        # Default to global monthly savings if not present (submitting from index page)
        period_savings_strs = [monthly_savings_str] * 10

    # Read period-specific one-off extra deposits
    period_extra_deposits_strs = request.form.getlist('period_extra_deposits')
    if not period_extra_deposits_strs:
        period_extra_deposits_strs = ["0,00"] * 10

    session['monthly_savings'] = monthly_savings_str if monthly_savings_str else "3.000,00"
    session['initial_investment'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"
    session['birth_year'] = birth_year_str
    session['period_savings'] = period_savings_strs
    session['period_extra_deposits'] = period_extra_deposits_strs

    monthly_savings = parse_localized_number(monthly_savings_str) if monthly_savings_str else 0.0
    initial_investment = parse_localized_number(initial_investment_str) if initial_investment_str else 0.0
    annual_rate = parse_localized_number(annual_rate_str) if annual_rate_str else None
    safe_withdrawal_rate = parse_localized_number(safe_withdrawal_rate_str) if safe_withdrawal_rate_str else 4.0
    
    # Parse period savings list
    period_savings = []
    for s in period_savings_strs:
        val = parse_localized_number(s)
        period_savings.append(val if val is not None else monthly_savings)

    # Parse period extra deposits list
    period_extra_deposits = []
    for e in period_extra_deposits_strs:
        val = parse_localized_number(e)
        period_extra_deposits.append(val if val is not None else 0.0)

    birth_year = None
    current_year = datetime.date.today().year
    if birth_year_str:
        try:
            birth_year = int(birth_year_str)
            if birth_year < 1900 or birth_year > current_year:
                flash(f"O ano de nascimento deve ser entre 1900 e {current_year}.", "danger")
                return redirect(url_for('calculator1_index'))
        except ValueError:
            flash("Por favor, insira um ano de nascimento válido.", "danger")
            return redirect(url_for('calculator1_index'))

    if annual_rate is None or annual_rate <= 0:
        flash("Por favor, insira uma Taxa de Retorno Anual válida e maior que 0.", "danger")
        return redirect(url_for('calculator1_index'))
    if safe_withdrawal_rate is None or safe_withdrawal_rate <= 0:
        flash("Por favor, insira uma Taxa de Retirada Segura válida e maior que 0.", "danger")
        return redirect(url_for('calculator1_index'))
    if all(val <= 0 for val in period_savings) and all(val <= 0 for val in period_extra_deposits) and initial_investment <= 0:
        flash("Por favor, forneça um valor para a Economia Mensal, Aporte Extra ou Investimento Inicial.", "danger")
        return redirect(url_for('calculator1_index'))

    # Check if user customized savings (different savings than global, or any non-zero extra deposits)
    has_custom_savings = any(s != monthly_savings_str for s in period_savings_strs) or \
                         any(e != "0,00" and e != "" for e in period_extra_deposits_strs)

    try:
        results = calculate_calculator1(period_savings, initial_investment, annual_rate, safe_withdrawal_rate, birth_year, current_year, period_extra_deposits)
    except ValueError:
        flash("Ocorreu um erro durante o cálculo.", "danger")
        return redirect(url_for('calculator1_index'))

    return render_template('result.html', results=results,
                           monthly_savings=session['monthly_savings'],
                           initial_investment=session['initial_investment'],
                           annual_rate=session['annual_rate'],
                           safe_withdrawal_rate=session['safe_withdrawal_rate'],
                           birth_year=session['birth_year'],
                           has_custom_savings=has_custom_savings)

# -------------------------------------------------------------
# Calculator 2: Future Monthly Income Calculator
# -------------------------------------------------------------
@app.route('/calculator-2-user-set-future-monthly-income')
def calculator2_index():
    """
    Renders the input form for Calculator 2.
    """
    target_income = session.get('target_income', '7.000,00')
    initial_investment = session.get('initial_investment_c2', '10.000,00')
    annual_rate = session.get('annual_rate_c2', '6,00')
    safe_withdrawal_rate = session.get('safe_withdrawal_rate_c2', '4,00')
    birth_year = session.get('birth_year_c2', '')
    extra_deposit = session.get('extra_deposit_c2', '0,00')
    extra_deposit_year = session.get('extra_deposit_year_c2', '')
    return render_template('calculator2_index.html',
                           target_income=target_income,
                           initial_investment=initial_investment,
                           annual_rate=annual_rate,
                           safe_withdrawal_rate=safe_withdrawal_rate,
                           birth_year=birth_year,
                           extra_deposit=extra_deposit,
                           extra_deposit_year=extra_deposit_year)

@app.route('/calculator-2-user-set-future-monthly-income/calculate', methods=['POST'])
def calculator2_calculate():
    """
    Processes form submission for Calculator 2.
    Calculates the required monthly investment (PMT) to achieve the target future monthly retirement income.
    """
    target_income_str = request.form.get('target_income', '').strip()
    initial_investment_str = request.form.get('initial_investment', '').strip()
    annual_rate_str = request.form.get('annual_rate', '').strip()
    safe_withdrawal_rate_str = request.form.get('safe_withdrawal_rate', '').strip()
    birth_year_str = request.form.get('birth_year', '').strip()
    extra_deposit_str = request.form.get('extra_deposit', '').strip()
    extra_deposit_year_str = request.form.get('extra_deposit_year', '').strip()

    session['target_income'] = target_income_str if target_income_str else "7.000,00"
    session['initial_investment_c2'] = initial_investment_str if initial_investment_str else "10.000,00"
    session['annual_rate_c2'] = annual_rate_str if annual_rate_str else "6,00"
    session['safe_withdrawal_rate_c2'] = safe_withdrawal_rate_str if safe_withdrawal_rate_str else "4,00"
    session['birth_year_c2'] = birth_year_str
    session['extra_deposit_c2'] = extra_deposit_str if extra_deposit_str else "0,00"
    session['extra_deposit_year_c2'] = extra_deposit_year_str

    target_income = parse_localized_number(target_income_str)
    initial_investment = parse_localized_number(initial_investment_str) if initial_investment_str else 0.0
    annual_rate = parse_localized_number(annual_rate_str) if annual_rate_str else None
    safe_withdrawal_rate = parse_localized_number(safe_withdrawal_rate_str) if safe_withdrawal_rate_str else 4.0
    extra_deposit = parse_localized_number(extra_deposit_str) if extra_deposit_str else 0.0
    
    extra_deposit_year = None
    if extra_deposit_year_str:
        try:
            extra_deposit_year = int(extra_deposit_year_str)
            if extra_deposit_year <= 0 or extra_deposit_year > 100:
                flash("Por favor, insira um ano válido para o aporte extra (entre 1 e 100).", "danger")
                return redirect(url_for('calculator2_index'))
        except ValueError:
            flash("Por favor, insira um ano válido para o aporte extra.", "danger")
            return redirect(url_for('calculator2_index'))

    birth_year = None
    current_year = datetime.date.today().year
    if birth_year_str:
        try:
            birth_year = int(birth_year_str)
            if birth_year < 1900 or birth_year > current_year:
                flash(f"O ano de nascimento deve ser entre 1900 e {current_year}.", "danger")
                return redirect(url_for('calculator2_index'))
        except ValueError:
            flash("Por favor, insira um ano de nascimento válido.", "danger")
            return redirect(url_for('calculator2_index'))

    if target_income is None or target_income <= 0:
        flash("Por favor, insira uma Renda Alvo válida e maior que 0.", "danger")
        return redirect(url_for('calculator2_index'))
    if annual_rate is None or annual_rate <= 0:
        flash("Por favor, insira uma Taxa de Retorno Anual válida e maior que 0.", "danger")
        return redirect(url_for('calculator2_index'))
    if safe_withdrawal_rate is None or safe_withdrawal_rate <= 0:
        flash("Por favor, insira uma Taxa de Retirada Segura válida e maior que 0.", "danger")
        return redirect(url_for('calculator2_index'))

    try:
        results = calculate_calculator2(target_income, initial_investment, annual_rate, safe_withdrawal_rate, birth_year, current_year, extra_deposit, extra_deposit_year)
    except ValueError:
        flash("Ocorreu um erro durante o cálculo.", "danger")
        return redirect(url_for('calculator2_index'))

    return render_template('calculator2_result.html', results=results,
                           target_income=session['target_income'],
                           initial_investment=session['initial_investment_c2'],
                           annual_rate=session['annual_rate_c2'],
                           safe_withdrawal_rate=session['safe_withdrawal_rate_c2'],
                           birth_year=session['birth_year_c2'],
                           extra_deposit=session['extra_deposit_c2'],
                           extra_deposit_year=session['extra_deposit_year_c2'])

# -------------------------------------------------------------
# Calculator 3: Monthly Savings Potential Calculator
# -------------------------------------------------------------
@app.route('/calculator-3-user-set-monthly-savings')
def calculator3_index():
    """
    Renders the input form for Calculator 3.
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
    """
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

    salary = parse_localized_number(salary_str)
    if salary is None or salary <= 0:
        flash("Por favor, insira um Salário Líquido válido (deve ser maior que 0).", "danger")
        return redirect(url_for('calculator3_index'))

    housing_val = parse_localized_number(housing_str) if housing_str else 0.0
    utilities_val = parse_localized_number(utilities_str) if utilities_str else 0.0
    transportation_val = parse_localized_number(transportation_str) if transportation_str else 0.0
    food_val = parse_localized_number(food_str) if food_str else 0.0
    hobbies_val = parse_localized_number(hobbies_str) if hobbies_str else 0.0
    subscriptions_val = parse_localized_number(subscriptions_str) if subscriptions_str else 0.0
    healthcare_val = parse_localized_number(healthcare_str) if healthcare_str else 0.0
    debt_val = parse_localized_number(debt_str) if debt_str else 0.0
    other_val = parse_localized_number(other_str) if other_str else 0.0

    total_expenses = (housing_val + utilities_val + transportation_val +
                      food_val + hobbies_val + subscriptions_val +
                      healthcare_val + debt_val + other_val)

    result_display = calculate_calculator3(salary, total_expenses)

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
