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
        driver_standings_data = df.to_json(orient="records")


        # 5: Reading the CSV from the zip file and converting it to a dataframe.
        file_name = "drivers.csv"
        df = pd.read_csv(zf.open(file_name))


        # 6: convert the dataframe to a JSON object.
        drivers_data = df.to_json(orient="records")
        


        # 5: Reading the CSV from the zip file and converting it to a dataframe.
        file_name = "results.csv"
        df = pd.read_csv(zf.open(file_name))

        # 6: convert the dataframe to a JSON object.
        results_data = df.to_json(orient="records")





        
        driver_standings_data=json.dumps(driver_standings_data)
        drivers_data=json.dumps(drivers_data)
        results_data=json.dumps(results_data)

        drivers_data=drivers_data.replace('\\', '')


        rdb.set('driver_standings_data', driver_standings_data)
        rdb.set('drivers_data', drivers_data)
        rdb.set('results_data', results_data)

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
    return str(type(drivers_data))
    try:

        if(drivers_data[0]==" "):
            drivers_data=drivers_data[1:]       #This is because I was getting an error where there was a space at the start of the data string that caused an error with json.loads
        drivers_data=json.loads(drivers_data)
    except TypeError:
        return("Database empty. Submit a post request before trying to access data.\n")
   

    drivers_list=[]
    for entry in drivers_data:
        name_str=entry['forename']+' '+entry['surname']
        drivers_list.append(name_str)
    return(drivers_list)

@app.route('/driverinfo/<driver>', methods=['GET'])
def calc_driver_summary(driver):
    wins=0
    races=0
    nationality=''

    rdb=get_redis_client()


    drivers_data=rdb.get('drivers_data')
    driver_standings_data=rdb.get('driver_standings_data')

    try:
        drivers_data=json.loads(drivers_data)
        driver_standings_data=json.loads(driver_standings_data)
    except TypeError:
        return("Database empty. Submit a post request before trying to access data.\n")

    for entry in drivers_data['drivers']:
        if entry['driverRef']==driver:
            driverId=entry['driverId']
            nationality=entry['nationality']
    for entry in driver_standings_data['driver_standings']:
        if entry['driverId']==driverId:
            races+=1
            wins=wins+entry['wins']
    return(races, wins, nationality)




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

