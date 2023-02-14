import threading
import queue
import time

import database
import typing

import logging
import sys

from docker_client import client

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


LOG = logging.getLogger(__name__)

class Worker:
    def __init__(self, num_of_workers=1):
        self.queue = queue.Queue()
        self.num_of_workers = num_of_workers

    def start_workers(self):
        LOG.debug("Starting %s workers.", self.num_of_workers)
        for i in range(self.num_of_workers):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            item = self.queue.get()
            self._process_task(item)
            self.queue.task_done()

    def wait(self):
        """Wait for all tasks to be processed."""
        self.queue.join()

    def _put_task(self, task: database.Task):
        self.queue.put(task)

    def _process_task(self, task: database.Task):
        LOG.debug("Processing task %s.", task)
        task.status = task.Status.running.value
        task.save()
        try:
            container = client.containers.run(image=task.image, command=task.command, detach=True)
            task.logs = container.logs().decode('UTF-8')
            task.status = task.Status.finished.value
            task.save()
        except Exception:
            task.status = task.Status.failed.value
            task.save()

    def _gather_tasks(self) -> typing.Sequence[database.Task]:
        """Gather all tasks.py in the database."""
        tasks = [task for task in database.Task.select().where(database.Task.status == 'pending')]
        return tasks

    def start(self):
        database.init_database()
        self.start_workers()

        while True:
            tasks = self._gather_tasks()
            if tasks:
                for task in tasks:
                    self._put_task(task)
            else:
                LOG.debug("No tasks found, sleeping for 30 seconds.")
                time.sleep(30)

            self.wait()


w = Worker()
w.start()
