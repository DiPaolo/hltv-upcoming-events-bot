import threading
import time

import schedule


class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)
