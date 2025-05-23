import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

trade = pd.read_csv('assets/korea-china-trade-data.csv', sep=',', dtype={"Date": str})
del trade['Country']

trade['Date'] = pd.to_datetime(trade['Date'], format='%Y.%m')

cols_to_convert = ['Exports', 'Imports']
for col in cols_to_convert:
    trade[col] = trade[col].astype(float)
    trade[col] = trade[col] / 1000
trade['Balance'] = trade['Exports'] - trade['Imports']

trade['Year'] = trade['Date'].dt.year
trade_melted = pd.melt(trade, id_vars='Date', value_vars=['Exports', 'Imports', 'Balance'],
                       var_name='Category', value_name='Value')

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(data=trade_melted, x='Date', y='Value', hue='Category', marker='')
plt.title('Korean Republic - China Trade Over Time')
plt.xlabel('Date')
plt.ylabel('USD (in millions)')

plt.xticks(ticks=trade['Year'], labels=trade['Year'].astype(str)) 
plt.xlim([trade['Date'].min(), trade['Date'].max()])
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()