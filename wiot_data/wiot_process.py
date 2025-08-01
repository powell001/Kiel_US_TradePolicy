import pandas as pd
import matplotlib.pyplot as plt
import pyxlsb
import numpy as np


oneyear = pd.read_excel(r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\wiot_data\WIOT2014_Nov16_ROW.xlsb", engine='pyxlsb', skiprows=0)

############
# ROWS
############
sectnames = oneyear.iloc[5:, 3].values
countrynames = oneyear.iloc[5:, 2].values
rows1 = sectnames + '_' + countrynames
print(rows1)

############
# COLUMNS
############
sectnames = oneyear.iloc[4, 4:].values
countrynames = oneyear.iloc[3, 4:].values
columns1 = sectnames + '_' + countrynames
print(columns1)

############
# data
############
data1 = oneyear.iloc[5:, 4:].values

COUNTRIES = list(set(countrynames))
COUNTRIES.remove('TOT')
COUNTRIES = sorted(COUNTRIES)
print(COUNTRIES)

SECTNAMES = ['c' + str(i) for i in range(1, 57)]
print(SECTNAMES)


############
############

############
# Trade Balance
############

def imports(country):
    oneyr = pd.DataFrame(data1, columns=columns1, index=rows1)

    #######################
    # rows
    #######################
    dontwantThese = [f'_{country}', '_TOT'] 
    theseRows = [rw for rw in oneyr.index if not any(rx in rw for rx in dontwantThese)]

    #######
    # columns
    #######
    wantThese = [f'_{country}'] 
    theseCols = [cl for cl in oneyr.columns if any(cx in cl for cx in wantThese)]

    oneyr = oneyr.loc[theseRows, theseCols]

    return oneyr.sum(axis=0).sum()

#################################

def exports(country):

    oneyr = pd.DataFrame(data1, columns=columns1, index=rows1)

    #######################
    # rows
    #######################
    wantThese = [f'_{country}'] 
    theseRows = [rw for rw in oneyr.index if any(rx in rw for rx in wantThese)]

    #######
    # columns
    #######
    dontwantThese = [f'_{country}'] 
    theseCols = [cl for cl in oneyr.columns if not any(cx in cl for cx in dontwantThese)]

    oneyr = oneyr.loc[theseRows, theseCols]

    dontwantThese = [f'_{country}', 'TOT'] 
    theseCols = [cl for cl in oneyr.columns if not any(cx in cl for cx in dontwantThese)]
    oneyr = oneyr.loc[:, theseCols]

    oneyr.to_csv("tmp_exports.csv")

    return oneyr.sum(axis=0).sum()

def tradeBalance(country='AUT'):
    print("Trade Balance:", exports(country) - imports(country))

#tradeBalance('ROW')

#############
# Own production vs inputs
#############

def own_production(country='AUS'):

    oneyr = pd.DataFrame(data1, columns=columns1, index=rows1)

    #######################
    # rows
    #######################
    wantThese = [f'_{country}'] 
    theseRows = [rw for rw in oneyr.index if any(rx in rw for rx in wantThese)]

    #######
    # columns
    #######
    wantThese = [f'_{country}'] 
    theseCols = [cl for cl in oneyr.columns if any(cx in cl for cx in wantThese)]

    # make initial selection
    oneyr = oneyr.loc[theseRows, theseCols]

    dontwantThese = ['c57', 'c58','c59','c60','c61'] 
    theseCols = [cl for cl in oneyr.columns if not any(cx in cl for cx in dontwantThese)]
    oneyr = oneyr.loc[:, theseCols]
    
    # sum columns
    sum_columns = oneyr.sum(axis=0)

    # numpy matrix
    oneyr_np = oneyr.to_numpy()
    diag = np.diagonal(oneyr_np)

    # dataframe
    df1 = pd.DataFrame({"diag": diag, "sum_columns": sum_columns})

    def percent_own_production(row):
        if row['sum_columns'] != 0:
            return (row['diag'] / row['sum_columns']) * 100
        else:
            return 0

    own1 = df1.apply(percent_own_production, axis=1)
    return own1

def own_production_all_countries():
    all_Own_Production = []
    for state in COUNTRIES:
        print(f"Own production for {state}:")
        df1 = own_production(country=state)
        all_Own_Production.append(df1.values)

    df1 = pd.DataFrame(all_Own_Production)
    df1 = df1.T 
    df1.columns = COUNTRIES
    df1.index = SECTNAMES

    print(df1)
    return df1

# own_production_all_countries()

# #############
# # Value added
# #############

def valueadded_data(country='AUS'):

    oneyr = pd.DataFrame(data1, columns=columns1, index=rows1)

    #######
    # columns
    #######

    wantThese = [f'_{country}'] 
    theseCols = [cl for cl in oneyr.columns if any(cx in cl for cx in wantThese)]

    #######
    # rows
    #######
    theseRows = ["r70_TOT"]

    # select rows and columns
    oneyr = oneyr.loc[theseRows, theseCols]

    sum = oneyr.sum(axis=1)

    return sum

def valueadded_all_countries():
    all_ValueAdded = []
    for state in COUNTRIES:
        print(f"Value Added for {state}:")
        df1 = valueadded_data(country=state)
        all_ValueAdded.append(df1.values)

    df1 = pd.DataFrame(all_ValueAdded)

    df1['Countries'] = COUNTRIES

    df1.rename(columns={0: 'value'}, inplace=True)

    df1 = df1[['Countries', 'value']]
    
    print(df1)
    return df1

#valueadded_all_countries()



#############
# Expenditures
#############

# # consumption_share
# row_sums = oneyr_selected.sum(axis=1)
# print(row_sums)

# total_consumption = row_sums.sum()

# row_sums_percent = row_sums / total_consumption 

# print(row_sums_percent)

