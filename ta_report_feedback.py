def ta_report_feedback(report, current_price=None):
    """
    Analizza il report di auto_ta_analysis e restituisce un feedback testuale e una valutazione sintetica
    sulla decisione di entrare nel mercato.

    Parametri:
    - report (dict): Il report generato da auto_ta_analysis.
    - current_price (float, opzionale): Prezzo attuale dell'asset (se non fornito, usa base_case Monte Carlo).

    Restituisce:
    - dict: {
        "score": float (0-1),
        "feedback": str,
        "warnings": list di str,
        "suggested_action": str ("entra", "aspetta", "evita")
      }
    """
    warnings = []
    score = 0
    max_score = 4  # uno per ogni filtro principale

    # 1. RSI e divergenza
    score = rsi_fb(report, score, warnings)

    # 2. Supporti (Fibonacci)
    score = fibo_fb(current_price, report, score, warnings)

    # 3. Volumi
    score = volumes_fb(report, score, warnings)

    # 4. Monte Carlo: probabilità di superare il target
    score = montecarlo_fb(report, score, warnings)

    # Decisione sintetica
    feedback, score_norm_perc, suggested_action = suggestion_fb(max_score, score)

    return {
        "score": round(score, 2),
        "max_score": max_score,
        "feedback": feedback,
        "warnings": warnings,
        "suggested_action": suggested_action
    }


def suggestion_fb(max_score, score):
    score_norm_perc = (score / max_score) * 100
    if score_norm_perc >= 75:
        suggested_action = "entra"
        feedback = "Condizioni tecniche favorevoli: puoi considerare di entrare nel mercato."
    elif score_norm_perc >= 50:
        suggested_action = "aspetta"
        feedback = "Condizioni tecniche miste: valuta con cautela, potresti aspettare conferme."
    else:
        suggested_action = "evita"
        feedback = "Condizioni tecniche sfavorevoli: meglio evitare l'ingresso ora."
    return feedback, score_norm_perc, suggested_action


def montecarlo_fb(report, score, warnings):
    prob = report["montecarlo"]["prob_Bx_gt_target"]
    if prob > 60:
        score += 1
        warnings.append(f"Probabilità Monte Carlo di superare il target elevata: {prob}%.")
    elif prob < 30:
        warnings.append(f"Probabilità Monte Carlo di superare il target bassa: {prob}%.")
    return score


def volumes_fb(report, score, warnings):
    vol_perc = report["volumi"]["sopra_media_perc"]
    vol_spike = report["volumi"]["spike_supporto_perc"]
    if vol_perc > 10:
        score += 1
        warnings.append("Volumi sopra la media: conferma di interesse sul mercato.")
    elif vol_perc < -10:
        warnings.append("Volumi sotto la media: attenzione a segnali deboli.")
    if vol_spike > 20:
        warnings.append("Spike di volume recente: possibile fase di accumulazione/distribuzione.")
    return score


def fibo_fb(current_price, report, score, warnings):
    fibo_levels = []
    for level in report["supporti"]["fibonacci"].values():
        fibo_levels.append(level[0])
    min_support = min(fibo_levels)
    max_resistance = max(fibo_levels)
    if current_price is None:
        current_price = report["montecarlo"]["base_case"]
    if current_price <= min_support * 1.02:
        score += 1
        warnings.append("Prezzo vicino a un supporto chiave: rischio drawdown limitato.")
    elif current_price >= max_resistance * 0.98:
        warnings.append("Prezzo vicino a una resistenza importante: attenzione a possibili ritracciamenti.")
    return score


def rsi_fb(report, score, warnings):
    rsi_val = report["rsi"]["valore"]
    rsi_div = report["rsi"]["divergenza"]
    if rsi_div == "nessuna":
        score += 1
    elif rsi_div == "positiva":
        score += 1
        warnings.append("Divergenza RSI positiva: possibile inversione rialzista.")
    elif rsi_div == "negativa":
        warnings.append("Divergenza RSI negativa: possibile inversione ribassista.")
    if rsi_val > 70:
        warnings.append(f"RSI molto alto ({rsi_val}): rischio ipercomprato.")
    elif rsi_val < 30:
        warnings.append(f"RSI molto basso ({rsi_val}): possibile rimbalzo tecnico.")
        score += 0.5
    return score