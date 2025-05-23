import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

trade['Year'] = trade['Date'].dt.year
trade_yearly = trade.groupby('Year')[['Exports', 'Imports', 'Balance']].sum().reset_index()
trade_yearly_melted = pd.melt(trade_yearly, id_vars='Year',
                              value_vars=['Exports', 'Imports', 'Balance'],
                              var_name='Category', value_name='Value')

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(data=trade_yearly_melted, x='Year', y='Value', hue='Category', marker='')
plt.title('Japan - China Trade Over Time (Yearly Aggregated)')
plt.xlabel('Date')
plt.ylabel('USD (in millions)')

plt.xticks(ticks=trade_yearly['Year'], labels=trade_yearly['Year'].astype(str), rotation=45)
plt.xlim([trade_yearly['Year'].min(), trade_yearly['Year'].max()])

plt.tight_layout()
plt.show()