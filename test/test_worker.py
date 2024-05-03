import pytest
from unittest.mock import patch, Mock
from worker import do_work


@patch('worker.get_job_by_id')
@patch('worker.update_job_status')
def test_do_work(mock_update_status, mock_get_job):
    jobid = '1234'

    # Mock current job data
    mock_get_job.return_value = {"start_year": 2020, "end_year": 2021}

    # Directly replacing Redis fetching logic with simple data assignments
    # Assuming this structure mimics expected results
    mock_driver_standings_data = {"drivers": [{"driverId": 1, "points": 10}]}
    mock_drivers_data = [{"driverId": 1, "name": "John Doe"}]
    mock_races_data = [{"raceId": 1, "year": 2021}]

    # Now call the function to test
    do_work(jobid)

    # Assert that job status was updated to 'in progress' and later to 'complete'
    mock_update_status.assert_any_call(jobid, 'in progress')
    mock_update_status.assert_any_call(jobid, 'complete')
