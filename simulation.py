"""IS211 Assignment 5: Network Request Simulator"""

import argparse
import csv
from collections import deque
import sys


class Request:
    """Represents a network request to a web server."""

    def __init__(self, request_id, file_name, arrival_time, process_time):
        self.request_id = request_id
        self.file_name = file_name
        self.arrival_time = arrival_time
        self.process_time = process_time
        self.start_time = None

    def wait_time(self):
        if self.start_time is not None:
            return self.start_time - self.arrival_time
        return 0


class Server:
    """Represents a web server that processes requests."""

    def __init__(self):
        self.queue = deque()
        self.current_request = None
        self.time_remaining = 0
        self.total_wait_time = 0
        self.requests_processed = 0
        self.current_time = 0

    def tick(self):
        if self.current_request is not None:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.requests_processed += 1
                self.total_wait_time += self.current_request.wait_time()
                self.current_request = None
                return True
        return False

    def add_request(self, request):
        self.queue.append(request)

    def start_next_request(self):
        if self.current_request is None and len(self.queue) > 0:
            self.current_request = self.queue.popleft()
            self.current_request.start_time = self.current_time
            self.time_remaining = self.current_request.process_time
            return True
        return False

    def is_busy(self):
        return self.current_request is not None

    def queue_size(self):
        return len(self.queue)

    def set_current_time(self, time):
        self.current_time = time

    def get_average_latency(self):
        if self.requests_processed == 0:
            return 0
        return self.total_wait_time / self.requests_processed


def load_requests(filename):
    requests = []
    try:
        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) < 3:
                    continue
                request_id = int(row[0].strip())
                file_name = row[1].strip()
                process_time = int(row[2].strip())
                arrival_time = request_id  # In this file, arrival time = request ID
                request = Request(request_id, file_name, arrival_time, process_time)
                requests.append((arrival_time, request))
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    requests.sort(key=lambda x: x[0])
    return requests


def simulate_one_server(filename):
    requests_data = load_requests(filename)
    if not requests_data:
        return 0
    server = Server()
    all_requests = [req for _, req in requests_data]
    max_time = max(req.arrival_time for req in all_requests)
    max_time += max(req.process_time for req in all_requests) + 100

    requests_by_time = {}
    for arrival_time, request in requests_data:
        requests_by_time.setdefault(arrival_time, []).append(request)

    for current_time in range(1, max_time + 1):
        server.set_current_time(current_time)
        if current_time in requests_by_time:
            for request in requests_by_time[current_time]:
                server.add_request(request)
        server.tick()
        if not server.is_busy():
            server.start_next_request()
    return server.get_average_latency()


def simulate_many_servers(filename, num_servers):
    requests_data = load_requests(filename)
    if not requests_data:
        return 0
    servers = [Server() for _ in range(num_servers)]
    all_requests = [req for _, req in requests_data]
    max_time = max(req.arrival_time for req in all_requests)
    max_time += max(req.process_time for req in all_requests) + 100

    requests_by_time = {}
    for arrival_time, request in requests_data:
        requests_by_time.setdefault(arrival_time, []).append(request)

    server_index = 0
    for current_time in range(1, max_time + 1):
        for server in servers:
            server.set_current_time(current_time)
        if current_time in requests_by_time:
            for request in requests_by_time[current_time]:
                servers[server_index].add_request(request)
                server_index = (server_index + 1) % num_servers
        for server in servers:
            server.tick()
            if not server.is_busy():
                server.start_next_request()

    total_wait_time = sum(s.total_wait_time for s in servers)
    total_requests = sum(s.requests_processed for s in servers)
    return total_wait_time / total_requests if total_requests else 0


def main():
    parser = argparse.ArgumentParser(description='Network Request Simulator')
    parser.add_argument('--file', required=True, help='CSV file containing request data')
    parser.add_argument('--servers', type=int, help='Number of servers to simulate')
    args = parser.parse_args()

    if args.servers:
        avg = simulate_many_servers(args.file, args.servers)
        print(f"Average latency with {args.servers} servers: {avg:.2f} seconds")
    else:
        avg = simulate_one_server(args.file)
        print(f"Average latency with 1 server: {avg:.2f} seconds")


if __name__ == '__main__':
    main()
