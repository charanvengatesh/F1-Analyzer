import json
from unittest.mock import patch, Mock
import pytest

# Assuming the following is the new implementation of process_data and generate_and_save_graph
from worker import process_data, generate_and_save_graph

# Sample Data
driver_data = [{"driverId": 1, "forename": "John", "surname": "Doe"}]
race_data = [{"raceId": 101, "year": 2021, "points": "50"}]
current_job = {'driver': "John-Doe"}


def test_process_data_found():
    result = process_data('123', driver_data, race_data, current_job)
    expected_hashmap = {2021: 50}
    assert result == expected_hashmap, "Should process data and return correct hashmap"


def test_process_data_not_found():
    job = {'driver': "Jane-Doe"}
    result = process_data('123', driver_data, race_data, job)
    assert result is None, "Should return None if driver not found"


def test_generate_and_save_graph(mocker):
    hashmap = {2021: 100}
    # Mock savefig to prevent actual file creation
    mocker.patch('matplotlib.pyplot.savefig')
    generate_and_save_graph(hashmap, {'driver': 'John-Doe'}, '123')
    plt_mock = mocker.patch('matplotlib.pyplot.title')
    plt_mock.assert_called_once_with('Points scored by year for John Doe')

# The command to run pytest remains the same:
# pytest test_data_processing.py
