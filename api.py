from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from functools import lru_cache
import time
import requests

# SET HEADERS FOR SEC REQUESTS
headers = {'User-Agent': 'ben@gmail.com'}

# SET PANDAS SCIENTIFIC NOTATION
pd.set_option('display.float_format', lambda x: '%.3f' % x)

app = Flask(__name__)
api = Api(app)
CORS(app)



#######################################################################################################################################
############################################################ EQUITY OBJECT FUNCTIONS ##################################################
#######################################################################################################################################

class Equity:
    def __init__(self, ticker):
        self.ticker = ticker


###########################################################################
######################### MISC AND NAME FUNCTIONS #########################

    def getCIKDataFrame(self):
        # REQUESTS THE COMAPNY TICKERS FROM SEC EDGAR API
        tickers_cik = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
        # NORMALIZES THE JSON DATA AND VALUES 
        tickers_cik = pd.json_normalize(pd.json_normalize(tickers_cik.json(), max_level=0).values[0])
        # CONVERTS CIK INT TO A STRING
        tickers_cik["cik_str"] = tickers_cik["cik_str"].astype(str).str.zfill(10)
        # SETS INDEX OF TICKERS_CIK DATAFRAME
        tickers_cik.set_index("ticker",inplace=True)
        # RETURNS DATAFRAME
        return tickers_cik
    
    def getTickerCIK(self):
        # CONVERTS THE INPUT TICKER TO ALL UPPERCASE
        ticker = self.ticker.upper()
        # TRY STATEMENT TO BETTER HANDLE ERRORS
        try:
            # GET CIK DATAFRAME, GETCIKDATAFRAME MUST BE DEFINED PRIOR TO CALL
            data = self.getCIKDataFrame()
            # CREATE DATAFRAME FROM CIK_STR ONLY
            CIKdf = pd.DataFrame(data['cik_str'])
            # RESETS INDEX
            CIKdf = CIKdf.reset_index()
            # PARSE DATAFRAME TO FIND MATCH WITH TICKER, DROPSna VALUES POST FILTER
            CIK = CIKdf.where(CIKdf['ticker'] == ticker).dropna()
            # GET THE CIK NUMBER FROM THE ONLY REMAINING ROW IN THE DATAFRAME
            CIK_number = CIK['cik_str'].values[0]
            # RETURNS CIK_NUMBER
            return CIK_number
        except:
            print('Error: Ticker Not Found')

    def getTickerFullName(self):
        # CONVERTS THE INPUT TICKER TO ALL UPPERCASE
        ticker = self.ticker.upper()
        # TRY STATEMENT TO BETTER HANDLE ERRORS
        try:
            # GET CIK DATAFRAME, GETCIKDATAFRAME MUST BE DEFINED PRIOR TO CALL
            data = self.getCIKDataFrame()
            # CREATE DATAFRAME FROM TITLE ONLY
            CIKdf = pd.DataFrame(data['title'])
            # RESETS INDEX
            CIKdf = CIKdf.reset_index()
            print(CIKdf)
            # PARSE DATAFRAME TO FIND MATCH WITH TICKER, DROPSna VALUES POST FILTER
            CIK = CIKdf.where(CIKdf['ticker'] == ticker).dropna()
            # GET THE CIK NUMBER FROM THE ONLY REMAINING ROW IN THE DATAFRAME
            CIK_number = CIK['title'].values[0]
            # RETURNS CIK_NUMBER
            return CIK_number
        except:
            print('Error: Ticker Not Found')

#######################################################################
######################## SUBMISSION FUNCTIONS #########################




#######################################################################
######################### FINANCIAL FUNCTIONS #########################

    # RETURNS THE VALUE OF A TAG IN DATAFRAME FORMAT FOR TICKER
    def getValueOfTag(self, tag):
        # GET THE CIK NUMBER OF THE TICKER PARAMETER
        CIKOfTicker = self.getTickerCIK()
        response = requests.get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{CIKOfTicker}/us-gaap/{tag}.json", headers=headers)
        lowerLvlDictKey = response.json()['units'].keys()
        jsonUnitsChildKey = list(lowerLvlDictKey)[0]
        valueOfTag = pd.json_normalize(response.json()["units"][jsonUnitsChildKey])
        valueOfTag["filed"] = pd.to_datetime(valueOfTag["filed"])
        valueOfTag = valueOfTag.sort_values("end")
        return valueOfTag


# FOR THIS FUNCTION AND API IN GENERAL WE NEED TO SPECIFY THE STANDARD API OUT PUT SHOULD LOOK LIKE
    def getAnnualValuesOfTag(self, tag):
        valuesDF = self.getValueOfTag(tag)
        
        valuesDF = valuesDF.drop(columns='filed')
        tempVar = valuesDF
        print(f'Number of records: {len(tempVar.index)}')

        try: 
            valuesDFannualFilter = valuesDF.where(~valuesDF['fp'].str.contains("Q")).dropna(how='all')
            print(f'\nSuccessfully dropped quarters from column FP, now {len(valuesDFannualFilter.index)} records remain.')
        except:
            valuesDFannualFilter = tempVar
            print('Error dropping quarters from dataset')

        try:
            valuesDFannualFilterNotQ = valuesDFannualFilter.where(~valuesDFannualFilter['frame'].str.contains("Q", na=False)).dropna(how='any')
            if len(valuesDFannualFilterNotQ.index > 0):
                valuesDFannualFilter = valuesDFannualFilterNotQ
            else:
                valuesDFannualFilter
            print(f'Successfully dropped frames containing Q, now {len(valuesDFannualFilter.index)} records remain.')

        except:
            pass
            print('Error dropping frames that contain Q from dataset')
        try:
            valuesDFannualFilter = valuesDFannualFilter.drop(columns=['accn','form','start','end']).set_index('frame')
            print(f'Successfully dropped the columns, now {len(valuesDFannualFilter.index)} records remain.')
            
        except:
            pass
            print('Error dropping columns')
            
        print(valuesDFannualFilter)
        return valuesDFannualFilter


#####################################################################
######################### PRICING FUNCTIONS #########################

    @lru_cache(maxsize=32)
    def getCurrentPrice(self):
        stock = yf.Ticker(self.ticker)
        closeData = pd.DataFrame(stock.history('ytd')['Close'])
        latestClose = round(closeData.Close.iloc[-1],2)
        time.sleep(1)
        return latestClose


    def ytdReturn(self):
        stock = yf.Ticker(self.ticker)
        closeData = pd.DataFrame(stock.history('ytd')['Close'])
        latestClose = closeData.Close.iloc[-1]
        startClose = closeData.Close.iloc[0]
        ytdReturn = (latestClose/startClose-1)
        ytdReturn = round(ytdReturn,4)
        time.sleep(1)
        return ytdReturn * 100
    
    def threeYearReturn(self):
        stock = yf.Ticker(self.ticker)
        closeData = pd.DataFrame(stock.history('3y')['Close'])
        latestClose = closeData.Close.iloc[-1]
        startClose = closeData.Close.iloc[0]
        threeYearReturn = (latestClose/startClose-1)
        return threeYearReturn
    
    def fiveYearReturn(self):
        stock = yf.Ticker(self.ticker)
        closeData = pd.DataFrame(stock.history('5y')['Close'])
        latestClose = closeData.Close.iloc[-1]
        startClose = closeData.Close.iloc[0]
        fiveYearReturn = (latestClose/startClose-1)
        return fiveYearReturn
    
    def dividendHistory(self):
        stock = yf.Ticker(self.ticker)
        # NO TIME FRAME SET ... USE .HISTORY()
        dividends = pd.DataFrame(stock.dividends)
        dividends = pd.DataFrame(dividends['Dividends'])
        return dividends
    
    def getvolumeOneYear(self):
        stock = yf.Ticker(self.ticker).history('1y')
        volumedata = pd.DataFrame(stock.Volume)
        volumedata = pd.DataFrame(volumedata['Volume'])
        return volumedata
    
    def getCloseHistory(self, timeframe):
        stock = yf.Ticker(self.ticker).history(timeframe)
        closeData = pd.DataFrame(stock.Close)
        closeData = pd.DataFrame(closeData['Close'])
        return closeData
    
    def fiveYearReturnsByMonthTable(self):
        # Gets the historical close prices by input time frame
        def getHistoricalClosePrices(ticker, time):
            stockObj = yf.Ticker(ticker).history(time)
            return stockObj
        # Gets the returns from dataframe from date: 'start' to 'end'
        def getReturnForMonth(df, start, end):
            start = start.date()
            end = end.date()
            closePricesForMonth = df.loc[start:end]
            monthStart = (closePricesForMonth.iloc[0]['Close'])
            monthEnd = (closePricesForMonth.iloc[-1]['Close'])
            returnForMonth = (monthEnd/monthStart-1)

            return returnForMonth*100
        

        
        sample_data = getHistoricalClosePrices(self.ticker, '5y')
        sample_data.index = sample_data.index.date
        sample_data['Returns'] = sample_data['Close'].pct_change(1)
        close_returns_df = sample_data
        # listOfDates = close_returns_df.index
        # currentYear = dt.datetime.today().year
        # print(currentYear)
        start = pd.Timestamp(year=2019, month=1, day=1)
        df = pd.DataFrame({"Start": pd.date_range(start, periods=60, freq="MS"),
                            "End": pd.date_range(start, periods=60, freq="M")})


        df['Returns'] = 1
        for k in df.index:
            # print(df['Start'][k].date(), df['End'][k].date())
            try:
                
                df['Returns'][k] = getReturnForMonth(sample_data, df['Start'][k], df['End'][k])
            except:
                df['Returns'][k] = 0

        df['Start'] = (df['Start']).apply(lambda s: s.strftime('%m-%d-%Y') if pd.notnull(s) else s)
        df['End'] = (df['End']).apply(lambda s: s.strftime('%m-%d-%Y') if pd.notnull(s) else s)
        
        return df
    
    def fiveYearReturnsByYearTable(self):
        # Gets the historical close prices by input time frame
        def getHistoricalClosePrices(ticker, time):
            stockObj = yf.Ticker(ticker).history(time)
            return stockObj
        # Gets the returns from dataframe from date: 'start' to 'end'
        def getReturnForYear(df, start, end):
            start = start.date()
            end = end.date()
            closePricesForYear = df.loc[start:end]
            monthStart = (closePricesForYear.iloc[0]['Close'])
            monthEnd = (closePricesForYear.iloc[-1]['Close'])
            returnForYear = (monthEnd/monthStart-1)
            return returnForYear
        
        sample_data = getHistoricalClosePrices(self.ticker, '5y')
        sample_data.index = sample_data.index.date
        sample_data['Returns'] = sample_data['Close'].pct_change(1)
        close_returns_df = sample_data
        # listOfDates = close_returns_df.index
        # currentYear = dt.datetime.today().year
        # print(currentYear)
        start = pd.Timestamp(year=2019, month=1, day=1)
        df = pd.DataFrame({"Start": pd.date_range(start, periods=5, freq="YS"),
                            "End": pd.date_range(start, periods=5, freq="Y")})

        df['Returns'] = 1
        for k in df.index:
            # print(df['Start'][k].date(), df['End'][k].date())
            try:
                
                df['Returns'][k] = getReturnForYear(sample_data, df['Start'][k], df['End'][k])
            except:
                df['Returns'][k] = 0

        df['Start'] = (df['Start']).apply(lambda s: s.strftime('%m-%d-%Y') if pd.notnull(s) else s)
        df['End'] = (df['End']).apply(lambda s: s.strftime('%m-%d-%Y') if pd.notnull(s) else s)
        
        return df


###################################################################################################################
################################################## API CLASSES ####################################################
###################################################################################################################

# ONLY API CLASSES SHOULD BE MAKING THE CONVERSION TO DICT TO THEN BE DISPLAYED IN JSON ON THE API ENDPOINT
# THIS IS BECAUSE WE MIGHT NEED TO USE THE FUNCTIONS ELSE WHERE ESPECIALLY WHEN MAKING COMPARISIONS/CALCULATIONS

########## PRICING DATA CLASSES ##########

class oneYearCloseData(Resource):
    def get(self, ticker):
        oneYcloseData = Equity(ticker).getCloseHistory('1y')
        oneYcloseData.index = oneYcloseData.index.strftime("%m/%d/%Y")
        oneYearCloseDataJson = oneYcloseData.to_dict(orient='index')
        return oneYearCloseDataJson

class YTDreturn(Resource):
    def get(self, ticker):
        ytdreturn = Equity(ticker).ytdReturn()
        return ytdreturn

class threeYearReturn(Resource):
    def get(self, ticker):
        threeYReturn = Equity(ticker).threeYearReturn()
        return threeYReturn 

class fiveYearReturn(Resource):
    def get(self, ticker):
        fiveYReturn = Equity(ticker).fiveYearReturn()
        return fiveYReturn 
    
class dividends(Resource):
    def get(self, ticker):
        dividends = Equity(ticker).dividendHistory()
        dividends.index = dividends.index.strftime("%m/%d/%Y")
        dividendsJson = dividends.to_dict(orient='index')
        return dividendsJson
    
class latestPrice(Resource):
    def get(self, ticker):
        latestClosePrice = Equity(ticker).getCurrentPrice()
        return latestClosePrice
    
class volumeOneYear(Resource):
    def get(self, ticker):
        volumeData = Equity(ticker).getvolumeOneYear()
        volumeData.index = volumeData.index.strftime("%m/%d/%Y")
        volumeDataJson = volumeData.to_dict(orient='index')
        return volumeDataJson
    
class fiveYearReturnsByMonth(Resource):
    def get(self, ticker):
        fiveYearReturnsTable = Equity(ticker).fiveYearReturnsByMonthTable()
        print(fiveYearReturnsTable)
        fiveYearReturnsTableJSON = fiveYearReturnsTable.to_dict(orient='index')
        return fiveYearReturnsTableJSON

class fiveYearReturnsByYear(Resource):
    def get(self, ticker):
        fiveYearReturnsTable = Equity(ticker).fiveYearReturnsByYearTable()
        print(fiveYearReturnsTable)
        fiveYearReturnsTableJSON = fiveYearReturnsTable.to_dict(orient='index')
        return fiveYearReturnsTableJSON

########## MISC CLASSES ##########
    
class tickerCIK(Resource):
    def get(self, ticker):
        tickerCIK = Equity(ticker).getTickerCIK()
        return tickerCIK
    
class tickerName(Resource):
    def get(self, ticker):
        tickerName = Equity(ticker).getTickerFullName()
        return tickerName
    
        


########## FINANCIAL STATEMENT CLASSES ##########

class DilutedSharesOutstandingAnnual(Resource):
    def get(self, ticker):
        tag = 'WeightedAverageNumberOfDilutedSharesOutstanding'
        sharesAnnual = Equity(ticker).getAnnualValuesOfTag(tag).to_dict(orient='index')
        return sharesAnnual

class RevenueAnnual(Resource):
    def get(self, ticker):
        tag = 'RevenueFromContractWithCustomerExcludingAssessedTax'
        revAnnual = Equity(ticker).getAnnualValuesOfTag(tag).to_dict(orient='index')
        return revAnnual


class netIncomeLossAnnual(Resource):
    def get(self, ticker):
        tag = "NetIncomeLoss"
        netIandL = Equity(ticker).getAnnualValuesOfTag(tag).to_dict(orient='index')
        return netIandL

class OpertatingCashflowsAnnual(Resource):
    def get(self, ticker):
        tag = "NetCashProvidedByUsedInOperatingActivities"
        CFOannual = Equity(ticker).getAnnualValuesOfTag(tag).to_dict(orient='index')
        return CFOannual
    
class CapitalExpenditureAnnual(Resource):
    def get(self, ticker):
        tag = "PaymentsToAcquirePropertyPlantAndEquipment"
        CapexAnnual = Equity(ticker).getAnnualValuesOfTag(tag).to_dict(orient='index')
        return CapexAnnual
    
class LongTermDebtAnnual(Resource):
    def get(self, ticker):
        tag = "DebtInstrumentCarryingAmount"
        LTdebt = Equity(ticker).getAnnualValuesOfTag(tag).dropna().to_dict(orient='index')
        return LTdebt
    
class OperatingIncomeAnnual(Resource):
    def get(self, ticker):
        tag = "OperatingIncomeLoss"
        OperatingIncome = Equity(ticker).getAnnualValuesOfTag(tag).to_dict(orient='index')
        return OperatingIncome
    


class FreeCashFlowAnnual(Resource):
    def get(self, ticker):
        cfotag = "NetCashProvidedByUsedInOperatingActivities"
        CfoAnnual = Equity(ticker).getAnnualValuesOfTag(cfotag)
        capextag = "PaymentsToAcquirePropertyPlantAndEquipment"
        CapexAnnual = Equity(ticker).getAnnualValuesOfTag(capextag)

        FreeCashFlows = CfoAnnual.set_index('frame').join(CapexAnnual.set_index('frame'), lsuffix='_OpCashFlowAnnual')
        FreeCashFlows['FreeCashFlow'] = FreeCashFlows['val_OpCashFlowAnnual'] - FreeCashFlows['val']

        FreeCashFlows = FreeCashFlows.drop(columns=['start_OpCashFlowAnnual','end_OpCashFlowAnnual', 'accn_OpCashFlowAnnual', 'fy_OpCashFlowAnnual','fp_OpCashFlowAnnual','form_OpCashFlowAnnual','accn','val_OpCashFlowAnnual','val'])
        FreeCashFlows = FreeCashFlows.dropna()
        
        FreeCashFlowsJson = FreeCashFlows.to_dict(orient='index')
        print(FreeCashFlows)
        return FreeCashFlowsJson



########## EXPIRIMENTAL CLASSES ##########

class Stock(Resource):
    def get(self, ticker):
        stock = yf.Ticker(ticker)
        history = pd.DataFrame(stock.history("1y")['Close'])
        json_data = history.to_dict(orient='records')
        return jsonify(json_data)
    
class status(Resource):    
    def get(self):
        return {"hello": "world"}

class TreasuryData(Resource):
    def get(self):
        link = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2023/all?field_tdr_date_value=2023&type=daily_treasury_yield_curve&page&_format=csv'
        yeilds = pd.read_csv(link)
        treasuryDF = yeilds.T
        treasuryDF = treasuryDF.rename(columns=yeilds['Date'])
        treasuryDF = treasuryDF.drop(['Date'])
        treasuryDF = treasuryDF.T
        json_data = treasuryDF.to_dict(orient='index')
        return jsonify(json_data)



#######################################################################################################################################
############################################################ API ENDPOINTS ############################################################
#######################################################################################################################################

api.add_resource(status, '/')

# EQUITY RETURNS ENDPOINTS
api.add_resource(YTDreturn, '/Stock/<ticker>/returns/ytd')
api.add_resource(threeYearReturn, '/Stock/<ticker>/returns/3y')
api.add_resource(fiveYearReturn, '/Stock/<ticker>/returns/5y')
api.add_resource(fiveYearReturnsByMonth, '/Stock/<ticker>/returns/monthly/5y')
api.add_resource(fiveYearReturnsByYear, '/Stock/<ticker>/returns/yearly/5y')

# EQUITY DIVIDEND ENDPOINTS
api.add_resource(dividends, '/Stock/<ticker>/dividends')

# EQUITY PRICE ENDPOINTS
api.add_resource(latestPrice, '/Stock/<ticker>/currentPrice')
api.add_resource(oneYearCloseData, '/Stock/<ticker>/price/1y')

# EQUTIY VOLUME ENDPOINTS
api.add_resource(volumeOneYear, '/Stock/<ticker>/volume/1y')

# EQUITY MISC ENDPOINTS
api.add_resource(Stock, '/Stock/<ticker>')
api.add_resource(tickerCIK, '/Stock/<ticker>/ciknumber')
api.add_resource(tickerName, '/Stock/<ticker>/cikname')

# EQUITY FINANCIALS ENDPOINTS
# ANNUAL DATA
api.add_resource(netIncomeLossAnnual, '/Stock/<ticker>/annual/netincomeloss')
api.add_resource(OpertatingCashflowsAnnual, '/Stock/<ticker>/annual/operatingcashflows')
api.add_resource(CapitalExpenditureAnnual, '/Stock/<ticker>/annual/capex')
api.add_resource(FreeCashFlowAnnual, '/Stock/<ticker>/annual/freecashflow')
api.add_resource(RevenueAnnual, '/Stock/<ticker>/annual/revenue')
api.add_resource(DilutedSharesOutstandingAnnual, '/Stock/<ticker>/annual/shares')
api.add_resource(LongTermDebtAnnual, '/Stock/<ticker>/annual/ltdebt')
api.add_resource(OperatingIncomeAnnual, '/Stock/<ticker>/annual/operatingIncome')



# TREASURY ENDPOINTS
api.add_resource(TreasuryData, '/treasuries')



#####################################
########## SERVER SETTINGS ##########
#####################################

if __name__ == '__main__':
    app.run()