import logging
import os
import sys
import threading
import time
import schedule
import pickle
from datetime import datetime
from typing import Optional

from tests.test_http_parser import response

from pywxdump.api.local_server import get_real_time_msg
# Assuming get_incremental_msgs is defined in the same module or imported
from pywxdump.api.remote_server import get_incremental_msgs

work_path = os.path.join(os.getcwd(), "wxdump_work")
TIMESTAMP_FILE = os.path.join(work_path, 'last_timestamp.pkl')

_scheduler_started = False  # 全局标志

msg_job_logger = logging.getLogger("msg_job")
msg_job_logger.setLevel(logging.INFO)  # 设置日志级别

#handler = logging.StreamHandler()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s:     %(message)s"))
msg_job_logger.addHandler(handler)


def start_scheduler():

    global _scheduler_started
    if not _scheduler_started:
        schedule.every(3).minutes.do(job)
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        _scheduler_started = True
        msg_job_logger.info("Scheduler started")


def save_timestamp(timestamp: int):
    with open(TIMESTAMP_FILE, 'wb') as f:
        pickle.dump(timestamp, f)

def load_timestamp() -> int:
    try:
        with open(TIMESTAMP_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        # If the file does not exist, return the current timestamp
        current_time = int(time.time())
        offset = 24 * 60 * 60  # subtract one day
        current_time = int(time.time()) - offset
        save_timestamp(current_time)
        return current_time

def job():

    last_timestamp = load_timestamp()
    response_new_msg = get_real_time_msg()
    if response_new_msg.get("code") == 0:
        msg_job_logger.info(f"获取实时消息成功：{response_new_msg.get('msg')}")
        response_msg = get_incremental_msgs(last_timestamp)
        if response_msg.get("code") == 0:

            timestamp = response_msg.get("body").get("timestamp")
            save_timestamp(timestamp)
            msg_job_logger.info(response_msg.get("body"))
            if timestamp is not None:
                ts_str = datetime.fromtimestamp(timestamp)
                msg_job_logger.info(f"Task executed successfully at {ts_str}")
        else:
            msg_job_logger.error(response_msg.get("msg"))
    else:
        msg_job_logger.error(f"Task execution failed，get_real_time_msg failed{response_new_msg.get('msg')}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    msg_job_logger.addHandler(handler)
    msg_job_logger.setLevel(logging.INFO)
    start_scheduler()
    time.sleep(300)