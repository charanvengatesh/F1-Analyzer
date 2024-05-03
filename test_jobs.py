import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from jobs import _generate_jid, _instantiate_job, _save_job, _queue_job


def test_generate_jid():
    jid = _generate_jid()
    assert isinstance(jid, str)
    assert len(jid) == 36  # UUIDs are 36 characters long


def test_instantiate_job():
    jid = str(uuid.uuid4())
    job = _instantiate_job(jid, 'pending', 'John Doe', 2000, 2020)
    assert job == {'id': jid, 'status': 'pending',
                   'driver': 'John Doe', 'start_year': 2000, 'end_year': 2020}


@patch('jobs.jdb')
def test_save_job(mock_jdb):
    jid = str(uuid.uuid4())
    job = {'id': jid, 'status': 'pending', 'driver': 'John Doe',
           'start_year': 2000, 'end_year': 2020}
    _save_job(jid, job)
    mock_jdb.set.assert_called_with(jid, json.dumps(job))


@patch('jobs.q')
def test_queue_job(mock_q):
    jid = str(uuid.uuid4())
    _queue_job(jid)
    mock_q.put.assert_called_with(jid)
