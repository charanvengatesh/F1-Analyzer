import json
import uuid
import redis
from hotqueue import HotQueue
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_redis_ip = 'redis-db'
_redis_port = '6379'

rd = redis.Redis(host=_redis_ip, port=_redis_port, db=0)
q = HotQueue("queue", host=_redis_ip, port=_redis_port, db=1)
jdb = redis.Redis(host=_redis_ip, port=_redis_port, db=2)
results = redis.Redis(host=_redis_ip, port=_redis_port, db=3)


def _generate_jid():
    return str(uuid.uuid4())


def _instantiate_job(jid, status, driver_name, start_year, end_year):
    job_dict = {'id': jid, 'status': status, 'driver': driver_name,
                'start_year': start_year, 'end_year': end_year}
    return job_dict


def _save_job(jid, job_dict):
    jdb.set(jid, json.dumps(job_dict))
    logger.info(f"Job {jid} saved to database.")


def _queue_job(jid):
    q.put(jid)
    logger.info(f"Job {jid} added to the queue.")


def add_job(driver_name, start_year, end_year, status="submitted"):
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, driver_name, start_year, end_year)
    _save_job(jid, job_dict)
    _queue_job(jid)
    logger.info(f"Job {jid} created: {job_dict}")
    return job_dict


def get_job_by_id(jid):
    job_data = jdb.get(jid)
    if job_data:
        logger.info(f"Job {jid} retrieved.")
        return json.loads(job_data)
    logger.warning(f"Job {jid} not found.")
    return None


def update_job_status(jid, status):
    job_dict = get_job_by_id(jid)
    if job_dict:
        job_dict['status'] = status
        _save_job(jid, job_dict)
        logger.info(f"Job {jid} status updated to {status}.")
    else:
        logger.error(f"Job {jid} not found.")
        raise Exception(f"Job {jid} not found.")


def get_jids():
    jids = jdb.keys()
    logger.info(f"Job IDs retrieved: {jids}")
    return str(jids)


def delete_jdb():
    jdb.flushdb()
    logger.info("All jobs deleted.")
