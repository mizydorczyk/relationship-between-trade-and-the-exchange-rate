import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def detect_outliers(data, threshold=1.5):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    outliers = (data < lower_bound) | (data > upper_bound)
    
    return outliers

def plot(trade: pd.DataFrame, exchange_rates: pd.DataFrame, filename: str, category: str, label: str, detect_outliers_flag: bool = True):
    trade_quarterly = trade.copy()
    trade_quarterly['Quarter'] = trade_quarterly['Date'].dt.to_period('Q')
    trade_quarterly = trade_quarterly.groupby('Quarter')[[category]].sum().reset_index()
    trade_quarterly['Date'] = trade_quarterly['Quarter'].dt.to_timestamp()
    trade_quarterly[f'{category}_pct_change'] = trade_quarterly[category].pct_change() * 100

    exchange_rates['Quarter'] = exchange_rates['Date'].dt.to_period('Q')
    quarterly_avg = exchange_rates.groupby('Quarter')[['CNY', 'USD']].mean().reset_index()
    quarterly_avg['Date'] = quarterly_avg['Quarter'].dt.to_timestamp()
    quarterly_avg['CNY_per_USD'] = quarterly_avg['USD'] / quarterly_avg['CNY']
    quarterly_avg['CNY_per_USD_pct_change'] = quarterly_avg['CNY_per_USD'].pct_change() * 100

    merged = pd.merge(trade_quarterly, quarterly_avg[['Date', 'CNY_per_USD_pct_change']], on='Date', how='left')
    merged = merged.dropna()

    
    if detect_outliers_flag:
        trade_outliers = detect_outliers(merged[f'{category}_pct_change'], threshold=3.0)
        exchange_outliers = detect_outliers(merged['CNY_per_USD_pct_change'], threshold=3.0)
        combined_outliers = trade_outliers | exchange_outliers
        normal_points = merged[~combined_outliers]
        outlier_points = merged[combined_outliers]
    else:
        normal_points = merged
        outlier_points = pd.DataFrame()
        combined_outliers = pd.Series([False] * len(merged), index=merged.index)
    
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 8))
    
    if len(normal_points) > 0:
        sns.scatterplot(data=normal_points, 
                       x='CNY_per_USD_pct_change', 
                       y=f'{category}_pct_change',
                       ax=ax, 
                       alpha=0.7,
                       s=60,
                       label='Punkty normalne (kwartały)' if detect_outliers_flag else 'Punkty (kwartały)')
    
    if detect_outliers_flag and len(outlier_points) > 0:
        sns.scatterplot(data=outlier_points, 
                       x='CNY_per_USD_pct_change', 
                       y=f'{category}_pct_change',
                       ax=ax, 
                       color='red',
                       marker='x',
                       s=100,
                       alpha=0.8,
                       label=f'Punkty skrajne ({len(outlier_points)})')
    
    if len(normal_points) > 3:
        trend_label = 'Linia trendu (z wyłączeniem punktów skrajnych)' if detect_outliers_flag and len(outlier_points) > 0 else 'Linia trendu'
        sns.regplot(data=normal_points, 
                   x='CNY_per_USD_pct_change', 
                   y=f'{category}_pct_change',
                   ax=ax, 
                   scatter=False,
                   color='blue',
                   label=trend_label)
    
    if len(normal_points) > 1:
        correlation = normal_points['CNY_per_USD_pct_change'].corr(normal_points[f'{category}_pct_change'])
        r_squared = correlation ** 2
        corr_label = f'Korelacja ($R$) = {correlation:.3f}\n$R^2$ = {r_squared:.3f}'
        if detect_outliers_flag and len(outlier_points) > 0:
            corr_label += '\n(z wyłączeniem punktów skrajnych)'
        ax.text(0.025, 0.98, corr_label, 
                transform=ax.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.2),
                verticalalignment='top')
    
    ax.set_xlabel('Zmiana kursu CNY/USD')
    ax.set_ylabel(f'Zmiana {label}')
    ax.set_xlim(normal_points['CNY_per_USD_pct_change'].min(), normal_points['CNY_per_USD_pct_change'].max())
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    
def main():
    trade = pd.read_csv('assets/usa-china-trade-data.csv', sep=';')
    trade.rename(columns={'Month': 'Date'}, inplace=True)
    trade['Date'] = pd.to_datetime(trade['Date'], format='%B %Y')
    for col in ['Exports', 'Imports', 'Balance']:
        trade[col] = trade[col].replace(',', '', regex=True).astype(float)
    
    exchange_rates = pd.read_csv('assets/exchange-rates.csv', sep=';')
    exchange_rates['Date'] = pd.to_datetime(exchange_rates['Date'], format='%d-%b-%Y')
    for col in ['CNY', 'JPY', 'KRW', 'USD']:
        exchange_rates[col] = exchange_rates[col].astype(float)
    
    detect_outliers_mode = False
    plot(trade, exchange_rates, 'fig6a.png', 'Exports', 'eksport Stanów Zjednoczonych do Chin', detect_outliers_mode)
    plot(trade, exchange_rates, 'fig6b.png', 'Imports', 'import Stanów Zjednoczonych z Chin', detect_outliers_mode)
    plot(trade, exchange_rates, 'fig6c.png', 'Balance', 'eksport netto Stanów Zjednoczonych do Chin', detect_outliers_mode)

if __name__ == '__main__':
    main()