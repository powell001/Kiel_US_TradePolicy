import baci_class as bc
import numpy as np
import pandas as pd
import os

BACI_DATA = r"C:\Users\jpark\vscode\Tariffs_Timeline\data\baci\BACI_HS92_Y"
COUNTRY_CODES = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\country_codes_V202501.csv"

# INITIALIZE object, needs to be run to create a BACI object instance
print("Initializing BACI object")
bc1 = bc.baci()

output1 = r"C:\Users\jpark\vscode\Kiel_US_TradePolicy\output\\"


############################
# Exports
############################

def totalExportsWorld():

    years = np.arange(1995, 2024, 1)
    allyears = []
    for yr in years:
        print("Processing year:", yr)   

        data = bc1.readindata(bacidata = BACI_DATA + str(yr) + "_V202501.csv", productasInt = False)
        data = bc1.addregions(data)

        # total exports
        global_exports = data['Value'].sum()

        # select EU exporters
        eu_exports_toWorld = data[data['Exporter_region_eu'] == "EU"]
        #eu_exports_toWorld = eu_exports_toWorld[eu_exports_toWorld['Importer_region_eu'] == 'Not_EU']

        # select columns of interest
        eu_exports_toWorld = eu_exports_toWorld[['Value', 'Exporter', 'Importer']]

        allyears.append((eu_exports_toWorld['Value'].sum()/global_exports)*100)

    return allyears

# out1 = totalExportsWorld()
# out1 = pd.DataFrame(out1)


def totalExportsWorld_perCountry(exporterName = "USA"):

    years = np.arange(1995, 2024, 1)
    allyears = []
    for yr in years:
        print("Processing year:", yr)   

        data = bc1.readindata(bacidata = BACI_DATA + str(yr) + "_V202501.csv", productasInt = False)
        data = bc1.addregions(data)

        # total exports
        global_exports = data['Value'].sum()

        # select exporter
        exports_toWorld = data[data['Exporter'] == exporterName]
        
        # select columns of interest
        exports_toWorld = exports_toWorld[['Value', 'Exporter', 'Importer']]

        allyears.append((exports_toWorld['Value'].sum()/global_exports)*100)

    return allyears


# countries = ["USA", "CHN", "DEU", "FRA", "GBR", "JPN", "KOR", "ITA", "ESP", "IND", "BRA", "RUS", "CAN"]

# for country in countries:
#     print(f"Processing exports for {country}")
#     out1[country] = totalExportsWorld_perCountry(country)

# print(out1)
# out1.to_csv(output1 + "totalExports_Percent.csv")


############################
# Manufacturing Exports
############################

def totalManufacturingExportsWorld():

    years = np.arange(1995, 2024, 1)
    allyears = []
    for yr in years:
        print("Processing year:", yr)   

        data = bc1.readindata(bacidata = BACI_DATA + str(yr) + "_V202501.csv", productasInt = False)
        data = bc1.addregions(data)

        # select manufacturing products
        prds1_2 = data['Product']
        data.loc[:, "Product_2"] = [x[0:2] for x in prds1_2]  #####

        #manufacturing sectors    
        manuf = ['84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95']
        data = data[data['Product_2'].isin(manuf)]

        # total exports
        global_exports = data['Value'].sum()

        # select EU exporters
        eu_exports_toWorld = data[data['Exporter_region_eu'] == "EU"]
        #eu_exports_toWorld = eu_exports_toWorld[eu_exports_toWorld['Importer_region_eu'] == 'Not_EU']

        # select columns of interest
        eu_exports_toWorld = eu_exports_toWorld[['Value', 'Exporter', 'Importer']]

        allyears.append((eu_exports_toWorld['Value'].sum()/global_exports)*100)

    return allyears

# out1 = totalManufacturingExportsWorld()
# out1 = pd.DataFrame(out1)


def totalManufacturingExportsWorld_perCountry(exporterName = "USA"):

    years = np.arange(1995, 2024, 1)
    allyears = []
    for yr in years:
        print("Processing year:", yr)   

        data = bc1.readindata(bacidata = BACI_DATA + str(yr) + "_V202501.csv", productasInt = False)
        data = bc1.addregions(data)

         # select manufacturing products
        prds1_2 = data['Product']
        data.loc[:, "Product_2"] = [x[0:2] for x in prds1_2]  #####

        #manufacturing sectors    
        manuf = ['84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95']
        data = data[data['Product_2'].isin(manuf)]

        # total exports
        global_exports = data['Value'].sum()

        # select exporter
        exports_toWorld = data[data['Exporter'] == exporterName]
        
        # select columns of interest
        exports_toWorld = exports_toWorld[['Value', 'Exporter', 'Importer']]

        allyears.append((exports_toWorld['Value'].sum()/global_exports)*100)

    return allyears


countries = ["USA", "CHN", "DEU", "FRA", "GBR", "JPN", "KOR", "ITA", "ESP", "IND", "BRA", "RUS", "CAN"]

# for country in countries:
#     print(f"Processing exports for {country}")
#     out1[country] = totalManufacturingExportsWorld_perCountry(country)

# print(out1)
# out1.to_csv(output1 + "totalManufacturingExports_Percent.csv")