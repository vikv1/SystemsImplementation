import heapq
import concurrent.futures
import random
import threading
import time
from queue import Queue
from threading import Lock, Condition

visited = set()
visited_lock = Lock()

class Job:
    def __init__(self, id, priority):
        self.id = id
        self.priority = priority

    def process(self):
        worker_id = threading.current_thread().name
        with visited_lock:
            visited.add(self.id)
        print(f"Worker {worker_id} processing job {self.id} with priority {self.priority}")
    
    def __lt__(self, other):
        return self.priority < other.priority
        
class JobQueue:
    def __init__(self):
        self.queue = []
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.jobs_available = True

    def add_job(self, job: Job):
        with self.lock:
            heapq.heappush(self.queue, job)
            self.condition.notify()

    def process_job(self):
        with self.lock:
            # Wait until a job is available or all jobs are done
            while not self.queue and self.jobs_available:
                self.condition.wait()
            
            if not self.queue:
                self.jobs_available = False
                return None
                
            job = heapq.heappop(self.queue)
            
        # Process job outside the lock to minimize lock contention
        job.process()
        return job.id
    
    def mark_complete(self):
        with self.lock:
            self.jobs_available = False
            self.condition.notify_all()
    
j = JobQueue()
job_count = 100000
# Create jobs
for i in range(job_count):
    rand_priority = random.randint(1, 10)
    j.add_job(Job(i, rand_priority))

# Use ThreadPoolExecutor with optimal number of workers
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    futures = []
    
    start_time = time.time()
    
    # Submit exactly the number of jobs we have
    for _ in range(job_count):
        futures.append(executor.submit(j.process_job))
    
    # Mark that no more jobs will be added
    j.mark_complete()
    
    # Wait for all futures to complete
    concurrent.futures.wait(futures)
    end_time = time.time()
    
    # Filter out None results and count successful jobs
    successful_jobs = [f.result() for f in futures if f.result() is not None]
    
    print(f"Total execution time: {end_time - start_time:.4f} seconds")
    print(f"Total jobs processed: {len(successful_jobs)}")

# Verify all jobs were processed
if len(successful_jobs) != job_count:
    print(f"Duplicate jobs processed")
    
for i in range(job_count):
    if i not in visited:
        print(f"Job {i} not done")