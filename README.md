# Formula 1 Race Data Analysis

# Overview

This repository contains code for analyzing Formula 1 race data obtained from Kaggle. The dataset comprises comprehensive information on Formula 1 races from 1950 to 2023, including details on racers, constructors, pit stop times, race results, and more. The project aims to extract insights from this data, such as understanding historical trends, evaluating performance metrics, and identifying patterns in race outcomes.

# Group Members

- Daiara Garcia
- Charan Vengatesh
- Dylan McIntyre

# Dataset Information

- **Dataset Source:** [Formula 1 World Championship 1950-2020](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020)
- **Description:** This dataset provides a comprehensive overview of Formula 1 races, including race dates, circuit names, weather conditions, race distances, lap-by-lap data, driver and constructor performances, pit stop times, qualifying times, race results, and championship standings.
- **Objective:** The objective of this project is to analyze the Formula 1 race data, perform various operations such as CRUD (Create, Read, Update, Delete), conduct trend analysis, evaluate performance metrics, and visualize insights.

# Description

The `main.py` script fetches the dataset from Kaggle, processes the data, and converts it into JSON format. This data conversion script simplifies the process of accessing and working with the Formula 1 race data.

# Dockerfile

To run this project using Docker, follow these steps:

1. Clone this repository to your local machine.
2. Navigate to the root directory of the cloned repository.
3. Create a Dockerfile in the root directory

# Routes

## Below are examples of different API routes and their output:
```
/data

      curl localhost:5000/data -X POST

  Posts F1 data to the redis database
  
  
      curl localhost:5000/data -X GET

  Returns the current database data
  
  
      curl localhost:5000/data -X DELETE

  Clears the current database data


```

```
/drivers

    curl localhost:5000/drivers

Returns a list of all driver names within the database

    curl localhost:5000/drivers/<firstname-lastname>

Returns a dictionary of information about a given driver including their nationality, number of races, and date of birth
  #Note: Please input driver names with a dash between first and last name ex: Lewis-Hamilton

```

```
/jobs
      curl localhost:5000/jobs  -X POST -d '{"driver":"Lewis-Hamilton", "start_year":"2000", "end_year":"2020"}' -H 'Content-Type: application/json'
This is an example request for a job post. The above request will generate a job to create a bar graph of championship points scored by Lewis Hamilton within the start and end year range. To request a job with no designated start and end date, put 0 as the start and end years as so:
      curl localhost:5000/jobs  -X POST -d '{"driver":"Lewis-Hamilton", "start_year":"2000", "end_year":"2020"}' -H 'Content-Type: application/json'


      curl localhost:5000/jobs -X DELETE
Deletes all current jobs on the database


    curl localhost:5000/jobs -X GET
Gets the job ID for all current jobs


    curl localhost:5000/jobs/<jobId>
This will return the status of the job for the requested job ID along with the inputed parameters of the job

```

```
/download
    curl localhost:5000/download/<jobId> --output output.png
Downloads the outputed image for a completed job given the job ID

