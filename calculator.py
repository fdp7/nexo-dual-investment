import technical_analysis as ta
import ta_report_feedback as tafb

def calculate_net_gain(s, apy, t, deal, symbol):
    """
    Calculate the net gain based on the formula: G = S*I - S*dB
    
    Parameters:
    s (int): Investment amount
    apy (int): Annual Percentage Yield
    t (int): Time period in days
    deal (int): Deal price
    
    Returns:
    dict: A dictionary containing the calculation results
    """
    # Calculate interest (I) based on APY and time period
    # Convert APY from percentage to decimal and adjust for the time period
    interest_rate = (apy / 100) * (t / 365)
    interest = s * interest_rate

    # Calculate breakeven price
    breakeven_price = deal * (1 - interest_rate)

    # Technical analysis
    analysis_report = ta.auto_ta_analysis(symbol=symbol, timeframe="1h", lookback_days=t*2, target=deal)
    analysis_feedback = tafb.ta_report_feedback(analysis_report)

    # Calculate purchase loss
    predicted_price = analysis_report["montecarlo"]["base_case"]
    if predicted_price <= deal:
        # I'm buying
        purchase_loss = s * (1 - predicted_price / deal)
    else:
        # I'm not buying
        purchase_loss = 0

    # Calculate net gain
    net_gain = interest - purchase_loss

    return {
        "investment_amount": s,
        "apy": apy,
        "time_period": t,
        "deal_price": deal,
        "interest_rate": interest_rate,
        "interest": interest,
        "analysis_feedback": analysis_feedback,
        "breakeven_price": breakeven_price,
        "predicted_price": predicted_price,
        "purchase_loss": purchase_loss,
        "net_gain": net_gain
    }