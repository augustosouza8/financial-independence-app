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

def calculate_calculator1(monthly_savings, initial_investment, annual_rate, safe_withdrawal_rate, birth_year=None, current_year=None, period_extra_deposits=None):
    """
    Calculates future investment value and projected monthly passive income over various durations.
    Supports either a single monthly_savings float or a list of period-specific savings floats.
    Also supports a list of one-off extra deposits at the end of each period.
    Returns a list of dictionaries with raw and formatted results.
    """
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
    durations = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    
    if not isinstance(monthly_savings, list):
        monthly_savings = [monthly_savings] * len(durations)
        
    if period_extra_deposits is None:
        period_extra_deposits = [0.0] * len(durations)
        
    results = []
    current_fv = initial_investment

    for i, years in enumerate(durations):
        prev_years = durations[i-1] if i > 0 else 0
        interval_years = years - prev_years
        n = interval_years * 12
        
        savings = monthly_savings[i]
        extra = period_extra_deposits[i]
        
        try:
            if monthly_rate > 0:
                current_fv = current_fv * (1 + monthly_rate) ** n + \
                             savings * (((1 + monthly_rate) ** n - 1) / monthly_rate)
            else:
                current_fv = current_fv + savings * n
        except ZeroDivisionError:
            raise ValueError("Zero division error during calculation.")
            
        # Add the one-time extra deposit at the end of the milestone period
        current_fv += extra
            
        monthly_income = current_fv * ((safe_withdrawal_rate / 100) / 12)
        
        age = None
        future_year = None
        if birth_year and current_year:
            future_year = current_year + years
            age = (current_year - birth_year) + years
            
        results.append({
            "years": years,
            "future_value_raw": current_fv,
            "monthly_income_raw": monthly_income,
            "future_value": format_currency(current_fv),
            "monthly_income": format_currency(monthly_income),
            "period_savings_raw": savings,
            "period_savings": format_currency(savings),
            "period_extra_raw": extra,
            "period_extra": format_currency(extra),
            "age": age,
            "future_year": future_year
        })

    return results

def calculate_calculator2(target_income, initial_investment, annual_rate, safe_withdrawal_rate, birth_year=None, current_year=None, extra_deposit=0.0, extra_deposit_year=None):
    """
    Calculates the required monthly investment (PMT) to achieve the target future monthly retirement income.
    Supports a one-off extra deposit at a specific year in the future.
    Returns a list of dictionaries with raw and formatted results.
    """
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
    R = target_income * 1200 / safe_withdrawal_rate
    durations = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    results = []

    for years in durations:
        n = years * 12
        compounded_initial = initial_investment * (1 + monthly_rate) ** n
        annuity_factor = ((1 + monthly_rate) ** n - 1) / monthly_rate
        
        # Deduct the compounded value of the one-off extra deposit if years >= extra_deposit_year
        compounded_extra = 0.0
        if extra_deposit > 0 and extra_deposit_year and years >= extra_deposit_year:
            compounded_extra = extra_deposit * (1 + monthly_rate) ** ((years - extra_deposit_year) * 12)

        try:
            pmt = (R - compounded_initial - compounded_extra) / annuity_factor
        except ZeroDivisionError:
            raise ValueError("Zero division error during calculation.")
            
        pmt_raw = pmt if pmt > 0 else 0
        if pmt < 0:
            required_investment_display = "Já aposentado! (Nenhum investimento adicional necessário)"
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
