import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot(trade: pd.DataFrame, exchange_rates: pd.DataFrame, filename: str, category: str, label: str):
    trade['Quarter'] = trade['Date'].dt.to_period('Q')
    trade_q = trade.groupby('Quarter')[['Exports', 'Imports', 'Balance']].sum().reset_index()
    trade_q['Date'] = trade_q['Quarter'].dt.to_timestamp()

    exchange_rates['Year'] = exchange_rates['Date'].dt.year
    exchange_rates['Month'] = exchange_rates['Date'].dt.month

    monthly_avg = exchange_rates.groupby(['Year', 'Month'])[['KRW', 'CNY']].mean().dropna().reset_index()
    monthly_avg['Quarter'] = pd.to_datetime(monthly_avg[['Year', 'Month']].assign(DAY=1)).dt.to_period('Q')
    
    quarterly_exch = monthly_avg.groupby('Quarter').agg({'KRW': 'mean', 'CNY': 'mean'}).reset_index()
    quarterly_exch['CNY_per_KRW'] = quarterly_exch['KRW'] / quarterly_exch['CNY']
    quarterly_exch['Date'] = quarterly_exch['Quarter'].dt.to_timestamp()

    merged = trade_q.merge(quarterly_exch[['Date', 'CNY_per_KRW']], on='Date', how='left')

    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=merged, x='Date', y=category, ax=ax1, label=label)
    ax1.set_ylabel(label)
    ax1.set_xlabel('Lata')

    ax2 = ax1.twinx()
    sns.lineplot(data=merged, x='Date', y='CNY_per_KRW', ax=ax2, color='tab:red', label='Kurs CNY/KRW', legend=False)
    ax2.set_ylabel('Kurs CNY/KRW')
    ax2.grid(False)

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    for label in ax1.get_xticklabels():
        label.set_rotation(45)

    plt.xlim([trade_q['Date'].min(), trade_q['Date'].max()])
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    fig.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')

def main():
    trade = pd.read_csv('assets/korea-china-trade-data.csv', sep=',', dtype={"Date": str})
    del trade['Country']
    trade['Date'] = pd.to_datetime(trade['Date'], format='%Y.%m')
    for col in ['Exports', 'Imports']:
        trade[col] = trade[col].astype(float) / 1000
    trade['Balance'] = trade['Exports'] - trade['Imports']

    exchange_rates = pd.read_csv('assets/exchange-rates.csv', sep=';')
    exchange_rates['Date'] = pd.to_datetime(exchange_rates['Date'], format='%d-%b-%Y')
    for col in ['CNY', 'JPY', 'KRW', 'USD']:
        exchange_rates[col] = exchange_rates[col].astype(float)

    plot(trade, exchange_rates, 'fig2a.png', 'Exports', 'Eksport Republiki Korei do Chin (mln USD)')
    plot(trade, exchange_rates, 'fig2b.png', 'Imports', 'Import Republiki Korei z Chin (mln USD)')
    plot(trade, exchange_rates, 'fig2c.png', 'Balance', 'Eksport netto Republiki Korei do Chin (mln USD)')

if __name__ == '__main__':
    main()