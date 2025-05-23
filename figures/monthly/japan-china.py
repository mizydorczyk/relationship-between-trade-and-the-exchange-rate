import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

exchange_rates = pd.read_csv('assets/exchange-rates.csv', sep=';')
exchange_rates['Date'] = pd.to_datetime(exchange_rates['Date'], format='%d-%b-%Y')
cols_to_convert = ['CNY', 'JPY', 'KRW', 'USD']
for col in cols_to_convert:
    exchange_rates[col] = exchange_rates[col].astype(float)

trade = pd.read_csv('assets/japan-china-trade-data.csv', sep=';')
trade['Date'] = pd.to_datetime(trade['Date'], format='%Y/%m')

cols_to_convert = ['Exports', 'Imports']
for col in cols_to_convert:
    trade[col] = trade[col].astype(float)
    trade[col] = trade[col] / 1000

exchange_rates_with_jpy = exchange_rates.dropna(subset=['JPY'])
exchange_rates_with_jpy['Year'] = exchange_rates_with_jpy['Date'].dt.year
exchange_rates_with_jpy['Month'] = exchange_rates_with_jpy['Date'].dt.month
monthly_avg_jpy_usd = exchange_rates_with_jpy.groupby(['Year', 'Month'])['JPY'].mean()

trade['Year'] = trade['Date'].dt.year
trade['Month'] = trade['Date'].dt.month

def to_usd(row):
    rate = monthly_avg_jpy_usd.get((row['Year'], row['Month']), None)
    exports_usd = row['Exports'] / rate
    imports_usd = row['Imports'] / rate
    return pd.Series([exports_usd, imports_usd])

trade[['Exports', 'Imports']] = trade.apply(to_usd, axis=1)
trade['Balance'] = trade['Exports'] - trade['Imports']

trade_melted = pd.melt(trade, id_vars='Date', value_vars=['Exports', 'Imports', 'Balance'],
                       var_name='Category', value_name='Value')

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(data=trade_melted, x='Date', y='Value', hue='Category', marker='')
plt.title('Japan - China Trade Over Time')
plt.xlabel('Date')
plt.ylabel('USD (in millions)')

plt.xticks(ticks=trade['Year'], labels=trade['Year'].astype(str)) 
plt.xlim([trade['Date'].min(), trade['Date'].max()])
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()