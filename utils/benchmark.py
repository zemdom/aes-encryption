import time

from utils.logger_handler import logger


class Benchmark:
    def __init__(self):
        self.total_time = 0
        self.t1 = 0

    def start_benchmarking(self):
        logger.debug(f'[BENCHMARK] Beginning')
        self.total_time = 0

    def start_measuring(self):
        self.t1 = time.time()

    def stop_measuring(self):
        t2 = time.time()
        self.total_time += (t2 - self.t1)

    def stop_benchmarking(self):
        logger.debug(f'[BENCHMARK] Time = {self.total_time}s')
        logger.debug(f'[BENCHMARK] Finished')
        return self.total_time
