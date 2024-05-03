import requests
import base64
import zipfile
import io
import pandas as pd
import json
import redis
import logging
from flask import Flask, request, send_file
from flask_cors import CORS
from jobs import add_job, get_job_by_id, update_job_status, get_jids, delete_jdb, results

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


def prepare_url(base_url, owner_slug, dataset_slug, dataset_version):
    return f"{base_url}/datasets/download/{owner_slug}/{dataset_slug}?datasetVersionNumber={dataset_version}"


def encode_credentials(username, key):
    creds = base64.b64encode(
        bytes(f"{username}:{key}", "ISO-8859-1")).decode("ascii")
    return {"Authorization": f"Basic {creds}"}


def send_request(url, headers):
    logger.info(f"Sending request to URL: {url}")
    response = requests.get(url, headers=headers)
    logger.info(f"Received response with status code: {response.status_code}")
    return response


def get_redis_client():
    return redis.Redis(host='redis-db', port=6379, db=0)


@app.route('/data', methods=['GET', 'POST', 'DELETE'])
def get_data() -> list:
    rdb = get_redis_client()

    if request.method == 'POST':
        logger.info("Handling POST request to /data")

        base_url = "https://www.kaggle.com/api/v1"
        owner_slug = "rohanrao"
        dataset_slug = "formula-1-world-championship-1950-2020"
        dataset_version = "22"

        url = prepare_url(base_url, owner_slug, dataset_slug, dataset_version)

        username = "charanvengatesh"
        key = "0af2f27b7c80e104843ed766e4606dc4"
        headers = encode_credentials(username, key)

        response = send_request(url, headers)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve dataset. Status code: {response.status_code}")
            return f"Error: Unable to retrieve dataset. Status code: {response.status_code}\n"

        zf = zipfile.ZipFile(io.BytesIO(response.content))

        def read_csv(file_name):
            return pd.read_csv(zf.open(file_name))

        def to_json(df):
            return json.loads(json.dumps(list(df.T.to_dict().values())))

        driver_standings_data = to_json(read_csv("driver_standings.csv"))
        drivers_data = to_json(read_csv("drivers.csv"))
        results_data = to_json(read_csv("results.csv"))
        races_data = to_json(read_csv("races.csv"))

        # Convert to JSON strings
        driver_standings_data = json.dumps(driver_standings_data)
        drivers_data = json.dumps(drivers_data).replace('\\', '')
        results_data = json.dumps(results_data)
        races_data = json.dumps(races_data)

        # Store data in Redis
        rdb.set('driver_standings_data', driver_standings_data)
        rdb.set('drivers_data', drivers_data)
        rdb.set('results_data', results_data)
        rdb.set('races_data', races_data)
        logger.info("Data has been stored in Redis")
        return "Data has been posted to Redis.\n"

    elif request.method == 'GET':
        try:
            data = json.loads(rdb.get('results_data'))
            logger.info("Retrieved results data from Redis")
            return data
        except TypeError:
            logger.warning("Database empty. No results data found.")
            return "Database empty. Submit a post request before trying to access data.\n"

    elif request.method == 'DELETE':
        rdb.flushdb()
        logger.info("Redis data has been deleted")
        return "Redis data has been deleted.\n"


@app.route('/drivers', methods=['GET'])
def driver_list():
    rdb = get_redis_client()
    drivers_data = json.loads(rdb.get('drivers_data'))

    if drivers_data:
        drivers_list = [f"{entry['forename']} {entry['surname']}" for entry in drivers_data]
        logger.info(f"Retrieved driver list: {len(drivers_list)} drivers")
        return drivers_list

    logger.warning("Database empty. No drivers data found.")
    return "Database empty. Submit a post request before trying to access data.\n"


@app.route('/drivers/<driver>', methods=['GET'])
def calc_driver_summary(driver):
    rdb = get_redis_client()
    drivers_data = json.loads(rdb.get('drivers_data'))
    driver_standings_data = json.loads(rdb.get('driver_standings_data'))

    if not drivers_data or not driver_standings_data:
        logger.warning("No drivers or standings data found.")
        return "Database empty. Submit a post request before trying to access data.\n"

    for entry in drivers_data:
        name = f"{entry['forename']}-{entry['surname']}".replace(' ', '-')
        if name == driver:
            ret_dict = {
                'forename': entry['forename'],
                'surname': entry['surname'],
                'dob': entry['dob'],
                'nationality': entry['nationality'],
                'races': sum(1 for e in driver_standings_data if e['driverId'] == entry['driverId'])
            }
            logger.info(f"Driver summary for {driver}: {ret_dict}")
            return ret_dict

    logger.warning(f"Driver name {driver} not found.")
    return "Driver name not found in database."


@app.route('/jobs', methods=['POST', 'GET', 'DELETE'])
def jobs_id() -> list:
    if request.method == 'POST':
        inputs = request.get_json()

        try:
            start_year = int(inputs["start_year"])
            end_year = int(inputs["end_year"])
            driver_name = inputs["driver"]
        except TypeError:
            logger.warning("Invalid job submission data.")
            return "Input an integer for start and end years."

        add_job(driver_name, start_year, end_year, status="submitted")
        logger.info(f"Job for {driver_name} from {start_year}-{end_year} submitted.")
        return "Job submitted. GET to view active jobs."

    elif request.method == 'GET':
        job_ids = get_jids()
        if len(job_ids) < 5:
            logger.warning("No current jobs.")
            return "No jobs. Use POST to create."
        else:
            jid_string = job_ids[3:-2]
            jid_list = jid_string.split("', b'")
            logger.info(f"Job IDs retrieved: {jid_list}")
            return jid_list

    elif request.method == 'DELETE':
        delete_jdb()
        logger.info("Jobs deleted.")
        return "Jobs deleted."


@app.route('/jobs/<jobid>', methods=['GET'])
def get_job_from_id(jobid) -> dict:
    try:
        job_dict = get_job_by_id(jobid)
        logger.info(f"Job {jobid} retrieved: {job_dict}")
        return job_dict
    except:
        logger.warning(f"ID {jobid} not found.")
        return "ID not found."


@app.route('/download/<jobid>', methods=['GET'])
def download(jobid):
    path = f'/app/{jobid}.png'
    with open(path, 'wb') as f:
        f.write(results.hget(jobid, 'image'))
        logger.info(f"Downloaded job image {jobid}")
        return send_file(path, mimetype='image/png', as_attachment=True)


app.run(debug=True, host='0.0.0.0', port=3000)
