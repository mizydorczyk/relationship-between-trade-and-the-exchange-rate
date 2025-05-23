import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

trade = pd.read_csv('assets/usa-china-trade-data.csv', sep=';')
trade.rename(columns={'Month':'Date'}, inplace=True)

trade['Date'] = pd.to_datetime(trade['Date'], format='%B %Y')

cols_to_convert = ['Exports', 'Imports', 'Balance']
for col in cols_to_convert:
    trade[col] = trade[col].replace(',', '', regex=True).astype(float)

trade['Year'] = trade['Date'].dt.year
trade_yearly = trade.groupby('Year')[['Exports', 'Imports', 'Balance']].sum().reset_index()
trade_yearly_melted = pd.melt(trade_yearly, id_vars='Year',
                              value_vars=['Exports', 'Imports', 'Balance'],
                              var_name='Category', value_name='Value')

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(data=trade_yearly_melted, x='Year', y='Value', hue='Category', marker='')
plt.title('United States - China Trade Over Time (Yearly Aggregated)')
plt.xlabel('Date')
plt.ylabel('USD (in millions)')

plt.xticks(ticks=trade_yearly['Year'], labels=trade_yearly['Year'].astype(str), rotation=45)
plt.xlim([trade_yearly['Year'].min(), trade_yearly['Year'].max()])

plt.tight_layout()
plt.show()