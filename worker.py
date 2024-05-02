from jobs import get_job_by_id, update_job_status, q, rd, results
import matplotlib.pyplot as plt
import numpy as np
import json



@q.worker
def do_work(jobid):
    update_job_status(jobid, 'in progress')
    driver_standings_data=rd.get('driver_standings_data')
    races_data=rd.get('races_data')
    drivers_data=rd.get('drivers_data')

    try:
        driver_standings_data=json.loads(driver_standings_data)
        drivers_data=json.loads(drivers_data)
        races_data=json.loads(races_data)

    except TypeError:
        update_job_status(jobid, 'complete')
        return("Database empty. Job results could not be computed.\n")


    hashmap={}

    

    current_job= get_job_by_id(jobid)
    if current_job['start_year']==0:
        start_year=0
    if current_job['end_year']==0:
        end_year=3000
    #This is if the user inputs 0 as start and end years, so I am setting the start and end years so that they don't cut off any data for the case to show all years

    driverId=-1
    for entry in drivers_data:
        name=entry['forename']+'-'+entry['surname']
        if name==current_job['driver']:
            driver_id=entry['driverId']
    if driverId==-1:
        update_job_status(jobid, 'complete')
        return("Inputted Driver Name not found in data. Job results could not be computed\n")


    for entry in drivers_standings_data:
        race_Id=entry['raceId']
        for entry2 in races_data:
            if race_Id==entry2['raceId']:
                race_year=entry2['year']

        if race_year in hashmap.keys():
            hashmap[race_year]+=int(entry['points'])
        else:
            hashmap[race_year]=int(entry['points'])

    groups, numbs=zip(*hashmap.items())

    plt.bar(groups,numbs, color = "red")
    plt.savefig('my_bar_graph.png')
    title_plot="Points scored by year for " + current_job['driver'].replace('-', ' ')
    plt.title(title_plot)


    try:

        with open('my_bar_graph.png', 'rb') as f:
            img = f.read()
            results.hset(jobid, 'image', img)
    except(FileNotFoundError):
        results.hset(jobid, 'image', "No data was found for that given chromosome, so an image was not created.")

    update_job_status(jobid, 'complete')

do_work()
