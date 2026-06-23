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

def calculate_calculator1(monthly_savings, initial_investment, annual_rate, safe_withdrawal_rate, birth_year=None, current_year=None):
    """
    Calculates future investment value and projected monthly passive income over various durations.
    Returns a list of dictionaries with raw and formatted results.
    """
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
    durations = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []

    for years in durations:
        n = years * 12
        try:
            fv = initial_investment * (1 + monthly_rate) ** n + \
                 monthly_savings * (((1 + monthly_rate) ** n - 1) / monthly_rate)
        except ZeroDivisionError:
            raise ValueError("Zero division error during calculation.")
            
        monthly_income = fv * ((safe_withdrawal_rate / 100) / 12)
        
        age = None
        future_year = None
        if birth_year and current_year:
            future_year = current_year + years
            age = (current_year - birth_year) + years
            
        results.append({
            "years": years,
            "future_value_raw": fv,
            "monthly_income_raw": monthly_income,
            "future_value": format_currency(fv),
            "monthly_income": format_currency(monthly_income),
            "age": age,
            "future_year": future_year
        })

    return results

def calculate_calculator2(target_income, initial_investment, annual_rate, safe_withdrawal_rate, birth_year=None, current_year=None):
    """
    Calculates the required monthly investment (PMT) to achieve the target future monthly retirement income.
    Returns a list of dictionaries with raw and formatted results.
    """
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
    R = target_income * 1200 / safe_withdrawal_rate
    durations = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []

    for years in durations:
        n = years * 12
        compounded_initial = initial_investment * (1 + monthly_rate) ** n
        annuity_factor = ((1 + monthly_rate) ** n - 1) / monthly_rate
        try:
            pmt = (R - compounded_initial) / annuity_factor
        except ZeroDivisionError:
            raise ValueError("Zero division error during calculation.")
            
        pmt_raw = pmt if pmt > 0 else 0
        if pmt < 0:
            required_investment_display = "Already retired! (No additional investment needed)"
        else:
            required_investment_display = format_currency(pmt)
            
        age = None
        future_year = None
        if birth_year and current_year:
            future_year = current_year + years
            age = (current_year - birth_year) + years

        results.append({
            "years": years,
            "required_investment_raw": pmt_raw,
            "required_investment": required_investment_display,
            "age": age,
            "future_year": future_year
        })

    return results

def calculate_calculator3(salary, expenses):
    """
    Calculates the available monthly savings by subtracting total expenses from the salary after taxes.
    Returns a formatted string representing the savings or deficit.
    """
    savings = salary - expenses
    if savings < 0:
        return "Deficit: " + format_currency(abs(savings))
    else:
        return format_currency(savings)
