from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from functools import lru_cache
import time

app = Flask(__name__)
api = Api(app)
CORS(app)

###################################
########## CLASS OBJECTS ##########
###################################

class Equity:
    def __init__(self, ticker):
        self.ticker = ticker

    @lru_cache(maxsize=32)
    def getCurrentPrice(self):
        stock = yf.Ticker(self.ticker)
        closeData = pd.DataFrame(stock.history('ytd')['Close'])
        latestClose = closeData.Close.iloc[-1]
        time.sleep(1)
        return latestClose


    def ytdReturn(self):
        stock = yf.Ticker(self.ticker)
        closeData = pd.DataFrame(stock.history('ytd')['Close'])
        latestClose = closeData.Close.iloc[-1]
        startClose = closeData.Close.iloc[0]
        ytdReturn = (latestClose/startClose-1)
        time.sleep(1)
        return ytdReturn
    
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


###################################
########## API CLASSES ############
###################################

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



#############

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



###################################
########## API ENDPOINTS ##########
###################################

api.add_resource(status, '/')

api.add_resource(YTDreturn, '/Stock/<ticker>/ytdreturn')
api.add_resource(threeYearReturn, '/Stock/<ticker>/3Yreturn')
api.add_resource(fiveYearReturn, '/Stock/<ticker>/5Yreturn')
api.add_resource(dividends, '/Stock/<ticker>/dividends')
api.add_resource(latestPrice, '/Stock/<ticker>/currentPrice')
api.add_resource(volumeOneYear, '/Stock/<ticker>/volume/1y')

api.add_resource(Stock, '/Stock/<ticker>')
api.add_resource(TreasuryData, '/treasuries')



#####################################
########## SERVER SETTINGS ##########
#####################################

if __name__ == '__main__':
    app.run()

# import pandas as pd
# import pymongo

## PUSH 
# git push heroku main
# api.add_resource(FinanceTags, '/<ticker>')
# api.add_resource(TagsByYear, '/<ticker>/<year>')







# CLASS OBJECT TO HANDLE METHODS OF READING DATA FROM PYMONGO
# class DataBase():
#     # READING CONTENTS OF THE DATA BASE FOR SELECTED TICKER
#     def getMasterFrame(self, input_ticker):

#         ticker = input_ticker.upper()

#         print(f'Searching database for {ticker}...')

#         client = pymongo.MongoClient("mongodb+srv://ryanhhogan:1314red1314red@cluster0.t0ayqhj.mongodb.net/")

#         client.list_database_names()

#         stock = client[ticker]

#         ann_tag_string = f'{ticker}_Annual_Tags'

#         collection = stock[ann_tag_string]

#         df_accounts = pd.DataFrame(list(collection.find()))

#         print('Success')

#         return df_accounts
    
#     # CONVERTS THE DATAFRAME RETRIEVED IN getMasterFrame FUNCTION AND CONVERTS IT TO JSON FOR API USE
#     def ConvertMasterFrameToJSON(self, input_ticker):
        
#         annual_tags_df = self.getMasterFrame(input_ticker)

#         annual_tags_df = annual_tags_df.drop(['_id'], axis=1)

#         json_data = annual_tags_df.to_dict(orient='records')

#         return jsonify(json_data)
    
#     def getTagsByYear(self, input_ticker, year):
        
#         annual_tags_df = self.getMasterFrame(input_ticker)

#         annual_tags_df = annual_tags_df.drop(['_id'], axis=1)

#         parse_by_year = annual_tags_df.where(annual_tags_df['frame'].str.contains(str(year)) & (~annual_tags_df['frame'].str.contains("Q"))).dropna(how='all')

#         json_data = parse_by_year.to_dict(orient='records')

#         return jsonify(json_data)


# class FinanceTags(Resource):
#     def get(self, ticker):
#         db_get_request = DataBase()
#         request_in_json = db_get_request.ConvertMasterFrameToJSON(ticker)
#         return request_in_json
    
# class TagsByYear(Resource):
#     def get(self, ticker, year):
#         db_connection = DataBase()
#         request_in_json = db_connection.getTagsByYear(ticker, year)
#         return request_in_json