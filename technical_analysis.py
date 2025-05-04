import numpy as np
import pandas as pd
import yfinance as yf
import talib
from datetime import datetime, timedelta

def fetch_ohlcv(symbol: str, interval: str = "1h", lookback_days: int = 60):
    """
    Scarica dati OHLCV (Open, High, Low, Close, Volume) da Yahoo Finance.

    Parametri:
    - `symbol` (str): Il simbolo del mercato o della criptovaluta (es. "BTC-USD").
    - `interval` (str): L'intervallo temporale dei dati (es. "1h" per dati orari, "1d" per dati giornalieri).
    - `lookback_days` (int): Il numero di giorni da cui partire per scaricare i dati storici.

    Restituisce:
    - `pd.DataFrame`: Un DataFrame contenente i dati OHLCV con colonne rinominate in minuscolo.

    Descrizione:
    Questa funzione utilizza la libreria `yfinance` per ottenere dati storici di mercato
    per un determinato simbolo e intervallo temporale. I dati vengono filtrati per il periodo
    specificato e restituiti come un DataFrame di pandas con colonne rinominate in minuscolo.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=lookback_days)
    df = yf.download(symbol, start=start, end=end, interval=interval)
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df = df.dropna()
    return df

def find_support_clusters(df, window=30, min_touches=3, tolerance=0.002):
    """
    Identifica cluster di minimi (supporti) negli ultimi `window` giorni.

    Parametri:
    - `df` (pd.DataFrame): DataFrame contenente i dati OHLCV con colonne come 'low'.
    - `window` (int): Numero di giorni da considerare per l'analisi (default: 30).
    - `min_touches` (int): Numero minimo di tocchi richiesti per identificare un supporto (default: 3).
    - `tolerance` (float): Tolleranza percentuale per considerare i prezzi vicini come parte dello stesso cluster (default: 0.002).

    Restituisce:
    - `list`: Una lista di prezzi che rappresentano i cluster di supporto identificati.

    Descrizione:
    Questa funzione analizza i prezzi minimi (`low`) di un DataFrame per identificare livelli di supporto
    basati su cluster di prezzi vicini. Un livello di supporto viene considerato valido se il numero di
    tocchi (prezzi vicini al livello) supera il valore di `min_touches`. I cluster vengono arrotondati
    per semplificare l'interpretazione e ordinati in ordine crescente.
    """
    lows = df['low'][-window*24:]  # window giorni, 24h per giorno
    clusters = []
    for i in range(len(lows)):
        price = lows.iloc[i].values[0]
        # Conta quanti minimi sono vicini a questo prezzo
        count = np.sum(np.abs(lows - price) < price * tolerance)
        if count.values[0] >= min_touches:
            clusters.append(price)
    # Rimuovi duplicati e ordina
    clusters = sorted(set([round(c, -2) for c in clusters]))
    return clusters

def fibonacci_retracement(df, lookback=60*24):
    """
    Calcola livelli di Fibonacci retracement sull'ultimo trend significativo.

    Parametri:
    - `df` (pd.DataFrame): DataFrame contenente i dati OHLCV con una colonna 'close' che rappresenta i prezzi di chiusura.
    - `lookback` (int): Numero di periodi da considerare per calcolare i livelli di Fibonacci.
      Ad esempio, 60*24 rappresenta 60 giorni di dati orari (24 ore al giorno).

    Restituisce:
    - `dict`: Un dizionario con i livelli di Fibonacci (0.0%, 23.6%, 38.2%, 50.0%, 61.8%, 78.6%, 100.0%)
      calcolati in base al massimo e minimo dei prezzi di chiusura nel periodo specificato.

    Descrizione:
    I livelli di Fibonacci sono utilizzati per identificare potenziali aree di supporto e resistenza
    basate su proporzioni matematiche derivate dalla sequenza di Fibonacci. Questi livelli sono
    ampiamente utilizzati nell'analisi tecnica per prevedere possibili inversioni di trend o
    continuazioni.
    """
    closes = df['close'][-lookback:]
    max_price = closes.max()
    min_price = closes.min()
    diff = max_price - min_price
    levels = {
        "0.0%": max_price,
        "23.6%": max_price - 0.236 * diff,
        "38.2%": max_price - 0.382 * diff,
        "50.0%": max_price - 0.5 * diff,
        "61.8%": max_price - 0.618 * diff,
        "78.6%": max_price - 0.786 * diff,
        "100.0%": min_price,
    }
    return levels

def rsi_analysis(df, period=14):
    """
    Calcola l'RSI (Relative Strength Index) e identifica eventuali divergenze.

    Parametri:
    - `df` (pd.DataFrame): DataFrame contenente i dati OHLCV con una colonna 'close' che rappresenta i prezzi di chiusura.
    - `period` (int): Periodo di calcolo per l'RSI (default: 14).

    Restituisce:
    - `tuple`: Una tupla contenente:
        - `current_rsi` (float): Valore corrente dell'RSI.
        - `divergence` (str): Tipo di divergenza rilevata ("positiva", "negativa" o "nessuna").

    Descrizione:
    L'RSI è un indicatore tecnico che misura la forza relativa di un asset confrontando i guadagni medi con le perdite medie
    in un determinato periodo. È utile per identificare condizioni di ipercomprato o ipervenduto e possibili divergenze
    tra il prezzo e l'indicatore.
    """
    close_array = df['close']
    if isinstance(close_array, pd.DataFrame):
        close_array = close_array.squeeze()
    close_array = close_array.astype(float).to_numpy().reshape(-1)
    rsi = talib.RSI(close_array, timeperiod=period)
    current_rsi = rsi[-1]
    # Divergenza: prezzo in calo, RSI in risalita
    price_trend = close_array[-5:].mean() - close_array[-10:-5].mean()
    rsi_trend = rsi[-5:].mean() - rsi[-10:-5].mean()
    divergence = "nessuna"
    if price_trend < 0 < rsi_trend:
        divergence = "positiva"
    elif price_trend > 0 > rsi_trend:
        divergence = "negativa"
    return current_rsi, divergence

def volume_analysis(df, window=30*24):
    """
    Analizza i volumi rispetto alla media mobile.

    Parametri:
    - `df` (pd.DataFrame): DataFrame contenente i dati OHLCV con una colonna 'volume' che rappresenta i volumi.
    - `window` (int): Numero di periodi da considerare per l'analisi (default: 30 giorni di dati orari, ovvero 30*24).

    Restituisce:
    - `tuple`: Una tupla contenente:
        - `perc_above_ma` (float): Percentuale del volume corrente sopra la media mobile.
        - `spike` (float): Percentuale di spike del volume rispetto alla media mobile recente.

    Descrizione:
    Questa funzione calcola la percentuale del volume corrente sopra la media mobile e identifica eventuali spike di volume
    rispetto alla media mobile recente. È utile per individuare anomalie nei volumi di trading che potrebbero indicare
    movimenti significativi del mercato.
    """
    vol = df['volume'][-window:]
    ma = vol.rolling(window=window//3).mean()
    current_vol = vol.iloc[-1].values[0]
    current_ma = ma.iloc[-1].values[0]
    perc_above_ma = 100 * (current_vol - current_ma) / current_ma if current_ma > 0 else 0
    # Picco volume su supporto: cerca spike negli ultimi 10 periodi
    recent_vol = vol[-10:].values
    recent_ma = ma[-10:].values
    spike = 100 * (recent_vol.max() - recent_ma.mean()) / recent_ma.mean() if recent_ma.mean() > 0 else 0
    return perc_above_ma, spike

def monte_carlo_forecast(df, days=30, n_sim=1000, target=95000):
    """
    Esegue una simulazione Monte Carlo per stimare la probabilità che il prezzo futuro superi un valore target.

    Parametri:
    - `df` (pd.DataFrame): DataFrame contenente i dati OHLCV con una colonna 'close' che rappresenta i prezzi di chiusura.
    - `days` (int): Numero di giorni per cui eseguire la simulazione (default: 1).
    - `n_sim` (int): Numero di simulazioni Monte Carlo da eseguire (default: 1000).
    - `target` (float): Prezzo target da confrontare con i risultati della simulazione.

    Restituisce:
    - `tuple`: Una tupla contenente:
        - `prob` (float): Probabilità che il prezzo simulato superi il valore target.
        - `bull` (float): Valore del prezzo previsto nel caso ottimistico (80° percentile).
        - `base` (float): Valore del prezzo previsto nel caso base (50° percentile).
        - `bear` (float): Valore del prezzo previsto nel caso pessimistico (20° percentile).
        - `sigma` (float): Volatilità giornaliera stimata basata sui rendimenti storici.

    Descrizione:
    La funzione utilizza i rendimenti logaritmici storici per stimare la distribuzione dei prezzi futuri.
    Per ogni simulazione, il prezzo iniziale viene moltiplicato per un fattore casuale basato su una distribuzione normale
    con media e deviazione standard calcolate dai rendimenti storici. I risultati delle simulazioni vengono analizzati
    per calcolare la probabilità di superare il target e i valori previsti nei diversi scenari (bull, base, bear).
    """
    log_returns = np.log(df['close'] / df['close'].shift(1)).dropna()
    mu = float(log_returns.mean())
    sigma = float(log_returns.std())
    min_sigma = 1e-4
    if sigma < min_sigma:
        sigma = min_sigma
    S0 = float(df['close'].iloc[-1])
    results = []

    # Se la volatilità è troppo bassa, restituisci valori costanti
    if np.isclose(sigma, 0):
        results = np.full(n_sim, S0)
    else: # Simulazione Monte Carlo
        for _ in range(n_sim):
            price = S0
            for _ in range(days):
                price *= np.exp(np.random.normal(mu, sigma))
            results.append(price)
        results = np.array(results)

    prob = np.mean(results > target)
    # Scenari
    bull = np.percentile(results, 80)
    base = np.percentile(results, 50)
    bear = np.percentile(results, 20)
    return prob, bull, base, bear, sigma

def auto_ta_analysis(symbol="BTC-USD", timeframe="1h", lookback_days=60, target=55000):
    """
    Esegue un'analisi tecnica automatizzata su un simbolo di mercato specifico.

    Parametri:
    - `symbol` (str): Il simbolo del mercato o della criptovaluta (es. "BTC-USD").
    - `timeframe` (str): L'intervallo temporale dei dati (es. "1h" per dati orari, "1d" per dati giornalieri).
    - `lookback_days` (int): Il numero di giorni da cui partire per scaricare i dati storici.
    - `target` (float): Prezzo target per la simulazione Monte Carlo.

    Restituisce:
    - `dict`: Un dizionario strutturato contenente:
        - `supporti`: Livelli di supporto identificati (Fibonacci e cluster di minimi).
        - `rsi`: Valore corrente dell'RSI e tipo di divergenza rilevata.
        - `volumi`: Analisi dei volumi rispetto alla media mobile.
        - `montecarlo`: Risultati della simulazione Monte Carlo, inclusa la probabilità di superare il target e scenari previsti.

    Descrizione:
    La funzione combina diverse tecniche di analisi tecnica, tra cui:
    - Livelli di Fibonacci e cluster di supporto.
    - RSI (Relative Strength Index) e divergenze.
    - Analisi dei volumi rispetto alla media mobile.
    - Simulazione Monte Carlo per stimare la probabilità di raggiungere un prezzo target.
    """
    df = fetch_ohlcv(symbol, interval=timeframe, lookback_days=lookback_days)
    # 1. Supporti chiave
    fibo = fibonacci_retracement(df)
    clusters = find_support_clusters(df)
    # 2. RSI
    rsi, divergence = rsi_analysis(df)
    # 3. Volumi
    perc_above_ma, spike = volume_analysis(df)
    # 4. Monte Carlo
    prob, bull, base, bear, sigma = monte_carlo_forecast(df, days=30, n_sim=1000, target=target)
    # Output strutturato
    report = {
        "supporti": {
            "fibonacci": fibo,
            "cluster_minimi": clusters,
        },
        "rsi": {
            "valore": round(rsi, 2),
            "divergenza": divergence,
        },
        "volumi": {
            "sopra_media_perc": round(perc_above_ma, 2),
            "spike_supporto_perc": round(spike, 2),
        },
        "montecarlo": {
            "prob_Bx_gt_target": round(100*prob, 1),
            "bull_case": round(bull, 2),
            "base_case": round(base, 2),
            "bear_case": round(bear, 2),
            "volatilita_giornaliera": round(100*sigma, 2),
        }
    }
    return report

