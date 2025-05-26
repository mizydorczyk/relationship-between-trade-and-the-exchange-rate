import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot(trade: pd.DataFrame, exchange_rates: pd.DataFrame, filename: str, category: str, label: str):
    trade['Quarter'] = trade['Date'].dt.to_period('Q')
    trade_q = trade.groupby('Quarter')[[category]].sum().reset_index()
    trade_q['Date'] = trade_q['Quarter'].dt.to_timestamp()

    exchange_rates['Year'] = exchange_rates['Date'].dt.year
    exchange_rates['Month'] = exchange_rates['Date'].dt.month

    monthly_avg = exchange_rates.groupby(['Year', 'Month'])[['CNY', 'USD']].mean().reset_index()
    monthly_avg['Date'] = pd.to_datetime(monthly_avg[['Year', 'Month']].assign(DAY=1))
    monthly_avg['Quarter'] = monthly_avg['Date'].dt.to_period('Q')

    quarterly_avg = monthly_avg.groupby('Quarter')[['CNY', 'USD']].mean().reset_index()
    quarterly_avg['Date'] = quarterly_avg['Quarter'].dt.to_timestamp()
    quarterly_avg['CNY_per_USD'] = quarterly_avg['USD'] / quarterly_avg['CNY']

    merged = pd.merge(trade_q, quarterly_avg[['Date', 'CNY_per_USD']], on='Date', how='left')

    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=merged, x='Date', y=category, ax=ax1, label=label)
    ax1.set_ylabel(label)
    ax1.set_xlabel('Lata')

    ax2 = ax1.twinx()
    sns.lineplot(data=merged, x='Date', y='CNY_per_USD', ax=ax2, color='tab:red', label='Kurs CNY/USD', legend=False)
    ax2.set_ylabel('Kurs CNY/USD')
    ax2.grid(False)

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    for label in ax1.get_xticklabels():
        label.set_rotation(45)

    plt.xlim([trade_q['Date'].min(), trade_q['Date'].max()])

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

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

    plot(trade, exchange_rates, 'fig3a.png', 'Exports', 'Eksport Stanów Zjednoczonych do Chin (mln USD)')
    plot(trade, exchange_rates, 'fig3b.png', 'Imports', 'Import Stanów Zjednoczonych z Chin (mln USD)')
    plot(trade, exchange_rates, 'fig3c.png', 'Balance', 'Eksport netto Stanów Zjednoczonych do Chin (mln USD)')

if __name__ == '__main__':
    main()