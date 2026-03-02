# IS211 Assignment 5 – Network Request Simulator

This project simulates how network requests are processed by a web server (or multiple servers behind a load balancer) using a queue data structure. It reads a CSV file of requests, each with an arrival time (the request ID) and a processing time, and calculates the average wait time (latency) for requests.

## Files
- `simulation.py` – the main simulation script.

## How to Run
```bash
# Single server
python simulation.py --file /path/to/requests.csv

# Multiple servers (e.g., 3)
python simulation.py --file /path/to/requests.csv --servers 3
