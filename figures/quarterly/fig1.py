import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot(trade: pd.DataFrame, exchange_rates: pd.DataFrame, filename: str, category: str, label: str):
    exchange_rates['Year'] = exchange_rates['Date'].dt.year
    exchange_rates['Quarter'] = exchange_rates['Date'].dt.to_period('Q')

    quarterly_avg = exchange_rates.groupby('Quarter')[['CNY', 'JPY']].mean().dropna().reset_index()
    quarterly_avg['CNY_per_JPY'] = quarterly_avg['JPY'] / quarterly_avg['CNY']
    quarterly_avg['Date'] = quarterly_avg['Quarter'].dt.to_timestamp()

    trade['Quarter'] = trade['Date'].dt.to_period('Q')

    trade_q = trade.groupby('Quarter')[['Exports', 'Imports']].sum().reset_index()
    trade_q['Balance'] = trade_q['Exports'] - trade_q['Imports']
    trade_q['Date'] = trade_q['Quarter'].dt.to_timestamp()

    merged = pd.merge(trade_q, quarterly_avg[['Quarter', 'JPY', 'CNY_per_JPY']], on='Quarter', how='left')

    merged['Exports'] = merged['Exports'] / merged['JPY']
    merged['Imports'] = merged['Imports'] / merged['JPY']
    merged['Balance'] = merged['Balance'] / merged['JPY']

    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=merged, x='Date', y=category, label=label, ax=ax1)
    ax1.set_ylabel(label)
    ax1.set_xlabel('Lata')

    ax2 = ax1.twinx()
    sns.lineplot(data=merged, x='Date', y='CNY_per_JPY', label='Kurs CNY/JPY', ax=ax2, color='tab:red', legend=False)
    ax2.set_ylabel('Kurs CNY/JPY')
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
    trade = pd.read_csv('assets/japan-china-trade-data.csv', sep=';')
    trade['Date'] = pd.to_datetime(trade['Date'], format='%Y/%m')
    for col in ['Exports', 'Imports']:
        trade[col] = trade[col].astype(float) / 1000
    trade['Balance'] = trade['Exports'] - trade['Imports']

    exchange_rates = pd.read_csv('assets/exchange-rates.csv', sep=';')
    exchange_rates['Date'] = pd.to_datetime(exchange_rates['Date'], format='%d-%b-%Y')
    for col in ['CNY', 'JPY', 'KRW', 'USD']:
        exchange_rates[col] = exchange_rates[col].astype(float)

    plot(trade, exchange_rates, 'fig1a.png', 'Exports', 'Eksport Japonii do Chin (mln USD)')
    plot(trade, exchange_rates, 'fig1b.png', 'Imports', 'Import Japonii z Chin (mln USD)')
    plot(trade, exchange_rates, 'fig1c.png', 'Balance', 'Eksport netto Japonii do Chin (mln USD)')

if __name__ == '__main__':
    main()