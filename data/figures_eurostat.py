import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# "US Trade Policy After 2024: What is at Stake for the EU" in Google Books

###############
# Use same data above to get total trade balance for the EU
###############

def eu_trade_balance_total():
    """
    This function reads trade balance data from a CSV file, filters it for specific geopolitical entities,
    processes the data to create a pivot table, and plots the trade balance over time.
    """
    # Read the CSV file containing trade balance data

    df1 = pd.read_csv("C:\\Users\\jpark\\vscode\\Kiel_US_TradePolicy\\data\\figure1b_tradebalance.csv")

    df1 = df1[df1['External trade indicator'] == 'Trade balance in million ECU/EURO']
    df1['TIME_PERIOD'] = pd.to_datetime(df1['TIME_PERIOD'], format='%Y')

    df1a = df1[df1['partner'].apply(lambda x: len(str(x)) == 2)]
    df1b = df1[df1['partner']=='CN_X_HK']

    df1 = pd.concat([df1a, df1b], ignore_index=True)

    df2 = df1[['TIME_PERIOD', 'Geopolitical entity (partner)', 'OBS_VALUE']]
    df3 = df2.pivot(index='TIME_PERIOD', columns='Geopolitical entity (partner)', values='OBS_VALUE')  

    df3.to_csv("tmp1.csv") 
    df3['EU Total'] = df3.sum(axis=1)

    df3 = df3[['EU Total']]

    df3 = df3.iloc[:,0:]
    df3.plot()
    plt.axhline(y=0.5, color='black', linestyle='--')
    plt.title('EU Trade Balance')
    plt.xlabel('Time Period')
    plt.ylabel('Trade Balance (Million Euro)')
    plt.grid()
    plt.show()

    return df3['EU Total']

#eu_trade_balance_total()

def eu_trade_balance():
    """
    This function reads trade balance data from a CSV file, filters it for specific geopolitical entities,
    processes the data to create a pivot table, and plots the trade balance over time.
    """
    # Read the CSV file containing trade balance data

    df1 = pd.read_csv("C:\\Users\\jpark\\vscode\\Kiel_US_TradePolicy\\data\\figure1b_tradebalance.csv")

    # wantThese = ['United States', 'China except Hong Kong','European non-EU27 countries (from 2020)', 'Brazil', 'Russia', 'India', 'South Africa',
    #              'Iran', 'Indonesia','Ethiopia','Egypt','United Arab Emirates']

    # df1 = df1[df1['Geopolitical entity (partner)'].isin(wantThese)]
    df1 = df1[df1['External trade indicator'] == 'Trade balance in million ECU/EURO']
    df1['TIME_PERIOD'] = pd.to_datetime(df1['TIME_PERIOD'], format='%Y')

    df2 = df1[['TIME_PERIOD', 'Geopolitical entity (partner)', 'OBS_VALUE']]
    df3 = df2.pivot(index='TIME_PERIOD', columns='Geopolitical entity (partner)', values='OBS_VALUE')  

    ######################
    # Add Total Value
    ######################
    total_eu = eu_trade_balance_total() 
    df3['Total'] = total_eu
    #######################


    wantThese = ['United States', 'China except Hong Kong','European non-EU27 countries (from 2020)', 'Brazil', 'Russia', 'India', 'South Africa',
                 'Iran', 'Indonesia','Ethiopia','Egypt','United Arab Emirates', 'Total']

    df3 = df3[wantThese]

    df3.to_csv("tmp1.csv") 

    df3['BRIC (excluding China except Hong Kong)'] = df3[['Brazil', 'Russia', 'India', 'South Africa', 'Iran', 'Indonesia','Ethiopia','Egypt','United Arab Emirates']].sum(axis=1)
    df3.drop(columns=['Brazil', 'Russia', 'India', 'South Africa', 'Iran', 'Indonesia','Ethiopia','Egypt','United Arab Emirates'], inplace=True)

    df3 = df3.iloc[:,0:]/1000
    df3.plot()
    plt.axhline(y=0.5, color='black', linestyle='--')
    plt.title('Trade Balance')
    plt.xlabel('Time Period')
    plt.ylabel('Trade Balance (Million Euro)')
    plt.grid()
    plt.show()

# eu_trade_balance()

################
# US Bureau of Economic Analysis (BEA) Data
################

def us_bea_trade_balance():
    data = pd.read_excel(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\data\trad-geo-time-series-0425.xlsx", skiprows=5, sheet_name="Table 6")
    #print(data.head())    

    data = data.drop(index=0)
    data = data.iloc[0:26,:]
    data.index = np.arange(1999,2025)
    data['Total'] = data.iloc[:,1:25].sum(axis=1)

    print(data.head())
    #data = pd.to_datetime(data['Period'], format='%Y')
    subset = data[['Germany','Mexico','Canada','China', 'European Union', 'Brazil', 'Japan', 'Total']]
    subset = subset/1000  # Convert to million USD
  
    print(subset.head())

    subset.plot()
    plt.axhline(y=0, color='black', linestyle='--')
    plt.title('US Trade Balance with Selected Trading Partners')
    plt.xlabel('Time Period')
    plt.ylabel('Trade Balance (Million USD)')
    plt.grid()
    plt.show()

# us_bea_trade_balance()     

################
# Trade for Goods and Services
################

# value of international trade in goods and services

#def eu_trade_goods_services():
# bop_eu6_q

###############
# EU balance of payments 2023/24
################


# BPM6 Services https://ec.europa.eu/eurostat/databrowser/view/bop_its6_det__custom_17603496/default/tablehttps://ec.europa.eu/eurostat/databrowser/view/bop_its6_det__custom_17603496/default/table

def eu_bop_2023_24():

    data = pd.read_csv(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\data\estat_bop_eu6_q_filtered_en.csv", encoding='utf-8')

    #data = data[data['partner']=='US']
    data1 = data[['partner', 'Stock or flow', 'Balance of payments item', 'OBS_VALUE']]

    data1['Stock or flow'][data1['Stock or flow'] == 'Credit'] = 'Exports'
    data1['Stock or flow'][data1['Stock or flow'] == 'Debit'] = 'Imports'

    print(data1)

    data1['partner'][data1['partner'] == 'US'] = 'USA'
    data1['partner'][data1['partner'] == 'BR'] = 'Brazil'
    data1['partner'][data1['partner'] == 'CA'] = 'Canada'
    data1['partner'][data1['partner'] == 'CH'] = 'Switzerland'
    data1['partner'][data1['partner'] == 'IN'] = 'India'
    data1['partner'][data1['partner'] == 'JP'] = 'Japan'
    data1['partner'][data1['partner'] == 'OFFSHO'] = 'Offshore'
    data1['partner'][data1['partner'] == 'RU'] = 'Russia'
    data1['partner'][data1['partner'] == 'UK'] = 'Britain'
    data1['partner'][data1['partner'] == 'CN_X_HK'] = 'China'

    credits1 = data1[data1['Stock or flow'] == 'Exports']
    credits1['partner2'] = credits1['partner'] + '_exports'

    debits1 = data1[data1['Stock or flow'] == 'Imports']
    debits1['partner2'] = debits1['partner'] + '_imports'

    data3 = pd.concat([credits1, debits1], ignore_index=True)
    data3.rename(columns={'OBS_VALUE': 'Value'}, inplace=True)
    data3 = data3[['partner2', 'Balance of payments item', 'Value']]
    data3['Value'] = data3['Value']/1000

    data3 = data3[data3['partner2'].isin(['USA_exports', 'Britain_exports', 'Switzerland_exports', 'China_exports', 'Japan_exports', 'India_exports', 'Brazil_exports', 'Canada_exports', 'Offshore_exports', 'Russia_exports', 
                                        'USA_imports', 'Britain_imports', 'Switzerland_imports', 'China_imports', 'Japan_imports', 'India_imports', 'Brazil_imports', 'Canada_imports', 'Offshore_imports', 'Russia_imports'])]
    data3.sort_values(by=['partner2'], inplace=True)  

    data3 = data3.set_index(['partner2','Balance of payments item'])

    xxxx = data3.unstack()

    print(xxxx)

    xxxx['sorter'] = [7,7,6,6,3,3,1,1,8,8,5,5,4,4,9,9,2,2,0,0]

    xxxx.sort_values(by=['sorter'], inplace=True) 
    xxxx.drop(columns=['sorter'], inplace=True)
    xxxx.plot(kind='bar', stacked=True, alpha=1.0, rot=90, figsize=(12, 6))
    plt.title('EU Balance of Payments by Partner')
    plt.xlabel('')
    plt.ylabel('Value')
    plt.axvline(x = 1.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 3.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 5.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 7.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 9.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 11.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 13.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 15.5, color = 'grey', label = 'axvline - full height')
    plt.axvline(x = 17.5, color = 'grey', label = 'axvline - full height')
    plt.tight_layout()
    plt.show()

# eu_bop_2023_24()

def totalExports_Percent():
    allexports = pd.read_csv(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\output\totalExports_Percent.csv",)
    print(allexports.head())
    allexports = allexports.iloc[:,1:]
    allexports.rename(columns={'0': 'EU27'}, inplace=True)
    allexports.index = np.arange(1995, 2024, 1)

    allexports = allexports[['EU27', 'USA', 'CHN', 'DEU', 'IND', 'JPN', 'CAN']]

    allexports.plot()
    plt.grid()


    plt.title('Exports as Percentage of Global Exports')
    plt.xlabel('Year')
    plt.ylabel('Share in global exports (%)')

    plt.savefig(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\output\totalExports_Percent.png")
    plt.show()

totalExports_Percent()

def totalExportsManufacturing_Percent():
    allexports = pd.read_csv(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\output\totalManufacturingExports_Percent.csv")
    print(allexports.head())
    allexports = allexports.iloc[:,1:]
    allexports.rename(columns={'0': 'EU27'}, inplace=True)
    allexports.index = np.arange(1995, 2024, 1)

    allexports = allexports[['EU27', 'USA', 'CHN', 'DEU', 'IND', 'JPN', 'CAN']]

    allexports.plot()
    plt.grid()


    plt.title('MANUFACTURING Exports as Percentage of Global Exports')
    plt.xlabel('Year')
    plt.ylabel('MANUFACTURINGShare in global exports (%)')

    plt.savefig(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\output\totalManufacturingExports_Percent.png")
    plt.show()

totalExportsManufacturing_Percent()