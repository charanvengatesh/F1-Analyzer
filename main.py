import requests
import base64
import zipfile
import io
import pandas as pd

import json
import csv
from flask import Flask, request, send_file
import redis


app = Flask(__name__)


def prepare_url(base_url, owner_slug, dataset_slug, dataset_version):
    return f"{base_url}/datasets/download/{owner_slug}/{dataset_slug}?datasetVersionNumber={dataset_version}"


def encode_credentials(username, key):
    creds = base64.b64encode(
        bytes(f"{username}:{key}", "ISO-8859-1")).decode("ascii")
    return {
        "Authorization": f"Basic {creds}"
    }


def send_request(url, headers):
    return requests.get(url, headers=headers)


#Routes using Data

@app.route('/data', methods=['GET', 'POST', 'DELETE'])
def get_data()->list:

    rdb=get_redis_client()
    if request.method=='POST':

        # 1: Preparing the URL.
        base_url = "https://www.kaggle.com/api/v1"
        owner_slug = "rohanrao"
        dataset_slug = "formula-1-world-championship-1950-2020"
        dataset_version = "22"

        url = prepare_url(base_url, owner_slug, dataset_slug, dataset_version)

        # 2: Encoding the credentials and preparing the request header.


        username = "charanvengatesh"
        key = "0af2f27b7c80e104843ed766e4606dc4"
        headers = encode_credentials(username, key)

        # 3: Sending a GET request to the URL with the encoded credentials.
        response = send_request(url, headers)

        # 4: Loading the response as a file via io and opening it via zipfile.
        zf = zipfile.ZipFile(io.BytesIO(response.content))

        # 5: Reading the CSV from the zip file and converting it to a dataframe.
        file_name = "driver_standings.csv"
        df = pd.read_csv(zf.open(file_name))

        # 6: convert the dataframe to a JSON object.
        driver_standings_data=json.loads(json.dumps(list(df.T.to_dict().values())))


        # 5: Reading the CSV from the zip file and converting it to a dataframe.
        file_name = "drivers.csv"
        df = pd.read_csv(zf.open(file_name))


        # 6: convert the dataframe to a JSON object.
        drivers_data=json.loads(json.dumps(list(df.T.to_dict().values())))

        
    


        # 5: Reading the CSV from the zip file and converting it to a dataframe.
        file_name = "results.csv"
        df = pd.read_csv(zf.open(file_name))

        # 6: convert the dataframe to a JSON object.
        results_data=json.loads(json.dumps(list(df.T.to_dict().values())))



        # 5: Reading the CSV from the zip file and converting it to a dataframe.
        file_name = "races.csv"
        df = pd.read_csv(zf.open(file_name))

        # 6: convert the dataframe to a JSON object.
        races_data=json.loads(json.dumps(list(df.T.to_dict().values())))

        
        driver_standings_data=json.dumps(driver_standings_data)
        drivers_data=json.dumps(drivers_data)
        results_data=json.dumps(results_data)
        races_data=json.dumps(races_data)


        drivers_data=drivers_data.replace('\\', '')


        rdb.set('driver_standings_data', driver_standings_data)
        rdb.set('drivers_data', drivers_data)
        rdb.set('results_data', results_data)
        rdb.set('races_data', races_data)
        return("Data has been posted to redis.\n")
    
    if request.method=='GET':
        ret_list=[]
        data=rdb.get('results_data')
        try:
            data=json.loads(data)
            return(data)
        except TypeError:
            return("Database empty. Submit a post request before trying to access data.\n")
    if request.method=='DELETE':
        rdb.flushdb()
        return("Redis data has been deleted.\n")

def get_redis_client():

    """
    Initializes and returns a Redis client connected to a specified Redis database.
    """
    return redis.Redis(host='redis-db', port=6379, db=0)



@app.route('/drivers', methods=['GET'])
def driver_list():

    rdb=get_redis_client()
    drivers_data=rdb.get('drivers_data')

    try:
        drivers_data=json.loads(drivers_data)
    except TypeError:
        return("Database empty. Submit a post request before trying to access data.\n")
   

    drivers_list=[]
    for entry in drivers_data:
        name_str=entry['forename']+' '+entry['surname']
        drivers_list.append(name_str)
    return(drivers_list)

@app.route('/drivers/<driver>', methods=['GET'])
def calc_driver_summary(driver):
    wins=0
    races=0
    rdb=get_redis_client()


    drivers_data=rdb.get('drivers_data')
    driver_standings_data=rdb.get('driver_standings_data')

    ret_dict={}

    try:
        drivers_data=json.loads(drivers_data)
        driver_standings_data=json.loads(driver_standings_data)
    except TypeError:
        return("Database empty. Submit a post request before trying to access data.\n")

    for entry in drivers_data:
        name=entry['forename']+'-'+entry['surname']
        if name==driver:
            ret_dict['forename']=entry['forename']
            ret_dict['surname']=entry['surname']
            ret_dict['dob']=entry['dob']
            ret_dict['nationality']=entry['nationality']
            driverId=entry['driverId']
    
            for entry2 in driver_standings_data:
                if entry2['driverId']==driverId:
                    races+=1
            ret_dict['races']=races
            return(ret_dict)
    return "inputted driver name not found in databse."




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

