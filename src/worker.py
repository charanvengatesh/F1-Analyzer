import json
import matplotlib.pyplot as plt
import numpy as np
import logging

from jobs import get_job_by_id, update_job_status, q, rd, results

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@q.worker
def do_work(jobid):
    update_job_status(jobid, 'in progress')
    logger.info(f"Job {jobid} started.")

    driver_standings_data = rd.get('driver_standings_data')
    drivers_data = rd.get('drivers_data')
    races_data = rd.get('races_data')

    try:
        driver_standings_data = json.loads(driver_standings_data)
        drivers_data = json.loads(drivers_data)
        races_data = json.loads(races_data)
        logger.info("Data retrieved and parsed.")
    except TypeError:
        update_job_status(jobid, 'complete')
        logger.warning("Database empty. Job results could not be computed.")
        return "Database empty. Job results could not be computed.\n"

    current_job = get_job_by_id(jobid)
    start_year = current_job['start_year'] or 0
    end_year = current_job['end_year'] or 3000

    driverId = next((e['driverId'] for e in drivers_data if f"{e['forename']}-{e['surname']}" == current_job['driver']), -1)
    if driverId == -1:
        update_job_status(jobid, 'complete')
        logger.warning(f"Driver {current_job['driver']} not found in data.")
        return "Inputted Driver Name not found in data. Job results could not be computed\n"

    hashmap = {}
    for entry in driver_standings_data:
        race_Id = entry['raceId']
        race_year = next((e['year'] for e in races_data if e['raceId'] == race_Id), None)

        if driverId==entry['driverId']:
            
            if race_year in hashmap:
                hashmap[race_year] += int(entry['points'])
            else:
                hashmap[race_year] = int(entry['points'])
                

    groups, numbs = zip(*hashmap.items())

    plt.bar(groups, numbs, color="red")
    plt.title(f"Points scored by year for {current_job['driver'].replace('-', ' ')}")
    plt.savefig('my_bar_graph.png')
    logger.info(f"Graph generated for job {jobid}.")

    try:
        with open('my_bar_graph.png', 'rb') as f:
            img = f.read()
            results.hset(jobid, 'image', img)
        logger.info(f"Graph saved to Redis for job {jobid}.")
    except FileNotFoundError:
        results.hset(jobid, 'image',
                     "No data found for that given chromosome.")
        logger.warning(f"No data found for graph in job {jobid}.")

    update_job_status(jobid, 'complete')
    logger.info(f"Job {jobid} completed.")


# main guard to prevent immediate execution
if __name__ == "__main__":
    do_work()
