# from flask import Flask, request, jsonify
# from flask_restful import Resource, Api
# import pandas as pd
# import pymongo



# app = Flask(__name__)
# api = Api(app)

from flask import Flask
# import pandas as pd


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/json")
# def get_json():
#     return {"test":"test1"}

# # CLASS OBJECT TO HANDLE METHODS OF READING DATA FROM PYMONGO
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
    
# class TestPage(Resource):
#     def get(self):
#         return "test home page."

# api.add_resource(TestPage, '/')
# api.add_resource(FinanceTags, '/<ticker>')
# api.add_resource(TagsByYear, '/<ticker>/<year>')


# if __name__ == '__main__':
#     app.run(debug=True)