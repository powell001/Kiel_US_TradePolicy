import pandas as pd
import os
import sys 
import numpy as np
from functools import reduce
import itertools
from ast import literal_eval #converts object list to list of strings
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import statsmodels.api as sm
from statsmodels.formula.api import ols
import openpyxl

# this points to a Python file with the function country_mappings (not used)
#from combine_country_regions import country_mappings

# not great practice, but this removes warnings from the output
import warnings
warnings.filterwarnings("ignore")

# display settings so I can see more on the screen
desired_width=1000
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',10)
pd.options.display.max_rows = 50

#############################################################
# set this to point to your folder or create a new folder,
# (in my case my computer is called jpark and I called the folder tariffs_timeline) 
#############################################################
os.chdir(r'C:\Users\jpark\VSCode\tariffs_timeline\\')

# points to country codes as defined by BACI
COUNTRY_CODES = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\country_codes_V202501.csv"
# point to product codes
PRODUCT_DESCRIPTION = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\product_codes_HS22_V202501.csv"
# add region data, might be better sources
ADD_REGIONS = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\iso_countries_regions_gtap_nato.csv" ################################ added _gtap
# add short HS2 description (could be better descriptions)
SHORT_CODES = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\hs6twodigits.csv"
# add long product description
LONG_DESCRIPTION = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\product_codes_HS22_V202501.csv"
# add gdp data  
GDP_DATA = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\global_gdp_current.csv"
# strategic goods
STRATEGIC_GOODS = r"src\pdf_extractor\strategicProducts.csv"
# wgi values 
WGI_VALUES = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\WGI_iso3.csv"
# location of BACI unpacked data, note(!) last part of string, I keep the year 
# as a variable, so I can write, for instance:
j = 2022
BACI_DATA = r"C:\Users\jpark\VSCode\tariffs_timeline\data\baci\BACI_HS22_Y"
BACI_DATA + str(j) + "V202501.csv"

###############################
### LOOP years
beginYear = 1995
endYear = 2023
###############################

class baci:
    '''baci class contains the methods to load baci data and add characteristics such as geographic and strategic'''
    def readindata(self, bacidata, verbose = False, tmp_save = True, productasInt = True) -> pd.DataFrame:
        '''main method to read in baci data'''
        df1 = pd.read_csv(bacidata, usecols=['t','i','j','k','v','q'], 
                          dtype= {'t': 'int64',
                                  'i': 'int64', 
                                  'j': 'int64', 
                                  'k': 'object',
                                  'v': 'float64',
                                  'q': 'float64'}
                          )

        # This is too complicated, but '   NA' should be converted to float
        #df1['q'] = df1['q'].apply(lambda x: x.strip()) # remove spaces in data
        df1['q'].replace('NA', np.nan, inplace=True)   # np.nan is different than string NaN
        df1['q'] = df1['q'].astype(float)

        # rename columns to make them meaningful to humans
        df1.rename(columns={'t': 'Year', 'i': 'Exporter', 'j': 'Importer', 'k': 'Product', 'v': 'Value', 'q': 'Quantity'}, inplace=True)

        # replace number with name of country *exporter* 
        iso1 = pd.read_csv(COUNTRY_CODES, usecols=['country_code', 'country_iso3'])
        df1 = df1.merge(iso1, left_on="Exporter", right_on="country_code", how="left")
        df1.drop(columns=['country_code', 'Exporter'], inplace = True)
        df1.rename(columns={"country_iso3": "Exporter"}, inplace=True)
    
        # replace number with name of country *importer*
        df1 = df1.merge(iso1, left_on="Importer", right_on="country_code", how="left")
        df1.drop(columns=['country_code', 'Importer'], inplace = True)
        df1.rename(columns={"country_iso3": "Importer"}, inplace=True)

        # 2015 has some strange data, take only Values greater than 10.00, otherwise number of exporting countries in 2015 is an outlier
        #df1 = df1[df1['Value'] > 10.00]

        # if verbose is True, this will print out
        if verbose:
            hcodes = [str(x)[0:2] for x in df1["Product"]]
            print(set(hcodes))
            print(len(set(hcodes)))

        # make product code and int, otherwise its an object which can be confusing
        if productasInt:
            df1['Product'] = df1['Product'].astype(int)    

        return df1
    
    def addprodcode(self, data):
        '''add the product description if needed'''
        # add product_codes
        prodcodes = pd.read_csv(PRODUCT_DESCRIPTION, usecols=['code', 'description'])
        # product '9999AA' appears to be a filler--empty
        mask = prodcodes['code'] == '9999AA'
        prodcodes = prodcodes[~mask]

        # convert prodcodes to int (make sure all products captured (e.g. 090000))
        prodcodes['code'] = prodcodes['code'].astype(str)   

        # I love merges, note its a left merge, I want all baci data to have a code, but dont care for product codes without products.
        data = data.merge(prodcodes, left_on = "Product", right_on = "code", how = "left")
        
        return data
       
    def subsetData(self, data_param: pd.DataFrame, iso3_param: list[str], imp_exp_param: str, products_param: list[str], minvalue_param=0.0) -> pd.DataFrame():
        '''Select the importing (so not exporting at this point) country and the product, can be extended to select exporters'''
        
        df1 = data_param.copy()

        # select the importing (so, again, not exporting at this point) country and the product
        if products_param:
            out1 = df1[(df1[imp_exp_param].isin(iso3_param)) & (df1["Product"].isin(products_param))]
            out1.sort_values(by=['Value', 'Importer'], inplace=True, ascending=False)
            out1 = out1[out1['Value'] >= minvalue_param]
            out1['Value'] = out1['Value'].astype(int)
        else: # return all products in no product selected
            out1 = df1[df1[imp_exp_param].isin(iso3_param)]
            out1.sort_values(by=['Value', 'Importer'], inplace=True, ascending=False)
            out1 = out1[out1['Value'] >= minvalue_param]
            out1['Value'] = out1['Value'].astype(int)

        return out1
    
    def subsetStrategicGoods(self, data, STRATEGICGOODS: list):
        '''Selects products based on a list of strings'''
        df1 = data.copy()
        df2 = df1[df1['Product'].isin(STRATEGICGOODS)]
        return df2
    
    def addregions(self, data):
        '''Add regions to data, there are two of these almost identical functions, I need to combine them or get rid of one of them'''
        regions = pd.read_csv(ADD_REGIONS)
    
        # Exporter
        exp = data.merge(regions, left_on="Exporter", right_on="alpha-3", how="left")
        exp.drop(columns=['alpha-2', 'alpha-3', 'country-code', 'name', 'iso_3166-2', 'intermediate-region', 'region-code', 'sub-region-code', 'intermediate-region-code'], inplace = True)
        exp.rename(columns={"region": "Exporter_region", "region_eu": "Exporter_region_eu", "sub-region": "Exporter_sub_region", "GTAP_Agg": "Exporter_GTAP_Agg", "NATO": "Exporter_region_nato"}, inplace = True)
        # Importer
        imp = exp.merge(regions, left_on="Importer", right_on="alpha-3", how="left")
        imp.drop(columns=['alpha-2', 'alpha-3', 'country-code', 'name', 'iso_3166-2', 'intermediate-region', 'region-code', 'sub-region-code', 'intermediate-region-code'], inplace = True)
        imp.rename(columns={"region": "Importer_region", "region_eu": "Importer_region_eu", "sub-region": "Importer_sub_region", "GTAP_Agg": "Importer_GTAP_Agg", "NATO": "Importer_region_nato"}, inplace = True)
        data = imp.copy()

        return data

    def addregion(self, data, exim):
        '''Add regions to data, there are two of these almost identical functions, I need to combine them or get rid of one of them'''
        if exim == "Exporter":
            iso_regions = pd.read_csv(ADD_REGIONS)
            iso_regions = iso_regions[['alpha-3', 'region']]
            data = data.merge(iso_regions, left_on="Exporter", right_on="alpha-3", how="left")
            data.rename(columns = {'region': 'Exporter_Region'}, inplace = True)
            data.drop(columns=["alpha-3"], inplace=True)
        elif exim == "Importer":
            iso_regions = pd.read_csv(ADD_REGIONS)
            iso_regions = iso_regions[['alpha-3', 'region']]
            data = data.merge(iso_regions, left_on="Importer", right_on="alpha-3", how="left")
            data.rename(columns = {'region': 'Importer_Region'}, inplace = True)
            data.drop(columns=["alpha-3"], inplace=True)
        else: 
            print("Error")

        return data

    def addshortdescriptoProdname(self, data):
        '''Add short product description based on codes'''

        localdata = data.copy()
        prod_h6 = pd.read_csv(SHORT_CODES, dtype = str)

        # this is necessary because codes 1:9 should be 01:09
        localdata.loc[:, 'code'] = ["0" + x if len(x) == 5 else x for x in localdata['Product'].astype(str)]

        localdata['shrtDescription'] = localdata['code'].astype(str).str[0:2]
        proddesc = localdata.merge(prod_h6, left_on="shrtDescription", right_on="code")
        proddesc['product'] = proddesc['product'] + "_" + proddesc['shrtDescription']
        proddesc.drop(columns = {'code_x', 'shrtDescription', 'code_y'}, inplace = True)

        proddesc.rename(columns = {"product": "code"}, inplace = True)

        return proddesc
    
    def addlongdescription(self, data):
        '''Add product product description based on codes'''
        localdata = data.copy()
        longdesc = pd.read_csv(LONG_DESCRIPTION, dtype = str)

        # this is necessary because codes 1:9 should be 01:09
        localdata.loc[:, 'Product'] = ["0" + x if len(x) == 5 else x for x in localdata['Product'].astype(str)]

        longdesc.rename(columns = {"code": "isocode"}, inplace=True)
        longproddesc = localdata.merge(longdesc, left_on="Product", right_on="isocode", how = 'left', suffixes = ['x', 'y'])
       
        r1 = localdata.shape[0]
        r2 = longproddesc.shape[0]
        assert r1 == r2

        return longproddesc
    
    def add_gdp(self, data, GDP, year):
        '''Join GDP to data'''

        ### join GDP to data
        
        # Exporters
        gdp = GDP[GDP.index == year]
        gdp = gdp.T
        gdp['Exporter_gdp'] = gdp.index
        
        gdp.rename(columns={year: year + "_gdp_Exporter"}, inplace=True)

        dataj = data.merge(gdp, left_on = "Exporter", right_on = "Exporter_gdp")
        dataj[year + '_gdp_Exporter'] = dataj[year + '_gdp_Exporter']/1e+6
        
        # Importers
        gdp = GDP[GDP.index == year]
        gdp = gdp.T
        gdp['Importer_gdp'] = gdp.index
        gdp.rename(columns={year: year + '_gdp_Importer'}, inplace=True)

        data = dataj.merge(gdp, left_on = "Importer", right_on = "Importer_gdp")
       
        data.drop(columns = ["Exporter_gdp", "Importer_gdp"], inplace=True)

        return data
         
    def valueacrossallcountries(self, data_param: pd.DataFrame()):
        '''sums value across all product categories'''

        ### Relative size of Step1 inputs per product
        g = data_param[['Product', 'Value']].groupby(['Product']).sum()
        valueofStep1products = g.apply(lambda x: x.sort_values(ascending=False))
        valueofStep1products['Percentage'] = 100 * (valueofStep1products / valueofStep1products['Value'].sum())

        return valueofStep1products

    def valuepercountryacrossprods(self, data_param, imp_exp_param):
        '''not used, finds percentage of a product category compared to total'''
        ### Relative size of Step1 inputs per exporter
        g = data_param[[imp_exp_param, 'Value']].groupby([imp_exp_param]).sum()
        valueofStep1perExporter = g.apply(lambda x: x.sort_values(ascending=False))
        valueofStep1perExporter['Percentage'] = 100 * (valueofStep1perExporter / valueofStep1perExporter['Value'].sum())

        print(valueofStep1perExporter)
        return valueofStep1perExporter

    def valueperprod(self, data_param, imp_exp_param):
        '''not used, another means to get summed value of exported or imported product categories'''
        exp1 = data_param[['Value', imp_exp_param, 'Product']]
        g = exp1.groupby([imp_exp_param, 'Product']).sum().reset_index()  #this is now a data frame

        allprods = []
        for p in g['Product'].unique():
            prod = g[g['Product'] == p]
            prod.sort_values(by = ['Value'], ascending=False, inplace=True)
            allprods.append(prod)

        print(pd.concat(allprods))

        return pd.concat(allprods)

    def OECD_agg(self, data_param, baci_countries_param, imp_exp_param):
        '''not used, if the country a member of the OECD, get percentage of value of OECD exports/imports'''
        
        assert (imp_exp_param == 'Exporter_ISO3') or (imp_exp_param == 'Importer_ISO3'), "needs to be Exporter_ISO3 or Importer_ISO3"

        grp_perCountry = data_param[['Value', imp_exp_param]].groupby([imp_exp_param]).sum().reset_index()
        merged1 = grp_perCountry.merge(baci_countries_param[['ISO3', 'OECD']], left_on=imp_exp_param, right_on="ISO3", how="left")

        out = merged1[[imp_exp_param, 'Value', 'OECD']].groupby(['OECD']).sum().reset_index()
        out['Percentage'] = 100 * (out['Value'] / out['Value'].sum())
        out.sort_values(['Percentage'], ascending=False,inplace=True)
        print(out)

        return out

    def strategicgoodExportingImportingregions(self, data, impexp: str):
        '''sum of value of strategic imports/exports grouped by region'''

        if impexp == 'Importer':
            data = bc1.addregion(data, exim='Importer')
            regionValue = data[['Value', 'Importer_Region']].groupby('Importer_Region').sum()
            print("Major strategic importing regions: ", regionValue.sort_values(['Value'], ascending = False))

            stateValue = data[['Value', 'Importer']].groupby('Importer').sum()
            print("Major stratefic importing states: ", stateValue.sort_values(['Value'], ascending = False))
        
        if impexp == 'Exporter':
            data = bc1.addregion(data, exim='Exporter')
            regionValue = data[['Value', 'Exporter_Region']].groupby('Exporter_Region').sum()
            print("Major strategic exporting regions: ", regionValue.sort_values(['Value'], ascending = False))

            stateValue = data[['Value', 'Exporter']].groupby('Exporter').sum()
            print("Major strategic exporting states: ", stateValue.sort_values(['Value'], ascending = False))

        return data


    def typesofstrategicgoods(self, data):
        '''not used, just sums value by product code and sorts, done in other code'''
        valuestrategicgood = data[['Value', 'code']].groupby("code").sum()
        strategicproducts = valuestrategicgood.sort_values(['Value'], ascending = False)

            
        return strategicproducts

def GDPData():
    '''should alway be run, need to move to BACI class'''
    # https://data.worldbank.org/indicator/NY.GDP.MKTP.CD?end=2022&start=1960&view=chart
    # Taiwan comes from IMF data, added by hand. https://www.imf.org/external/datamapper/NGDPD@WEO/OEMDC/ADVEC/WEOWORLD
    
    data = pd.read_csv(GDP_DATA, index_col=[1], skiprows=4)
    data = data.drop(columns=['Country Name', 'Indicator Code', 'Indicator Name'])
    data = data.T
    return data
GDP = GDPData()

def getStrategicGoods():
    '''should alway be run, need to move to BACI class'''
    data = pd.read_csv(STRATEGIC_GOODS, index_col=[0],dtype= {'0': 'object'})
    # objects to ints
    data.iloc[:,0] = data.iloc[:,0].astype(int)
    data = data.iloc[:,0].tolist()

    return data
#STRATEGICGOODS = getStrategicGoods()

def getWGI():
    '''should alway be run, need to move to BACI class'''
    wgi = pd.read_csv(WGI_VALUES, index_col=[0])
    wgi.columns = ['ISO3', 'WGI_2022xxx']
    return wgi
WGI = getWGI()


#bc1 = baci()

