# Site Reliability Monitoring Tool

A production-ready endpoint monitoring tool that tracks and reports the availability of services across multiple domains.

## Overview

This tool continuously monitors HTTP/HTTPS endpoints defined in a YAML configuration file and reports their availability by domain. It's designed to be simple and suitable for monitoring needs.

## Features

- Monitors endpoint health based on HTTP status code and response time.
- Aggregates availability metrics by domain.
- Ignores port numbers when calculating domain-based statistics.
- Produces regular availability reports at 15-second intervals.
- Handles various error conditions.
- Includes comprehensive logging.
- Supports customizable HTTP methods, headers, and request bodies.

## Requirements

- Python 3.11+
- Required packages: `pyyaml` and `requests` that may not be installed by default.

## Installation

1. Clone this repository:

```shell
git clone https://github.com/aramyd001/dev-sre-take-home-exercise.git
cd dev-sre-take-home-exercise
```

1. Install dependencies:

```shell
pip install -r requirements.txt
```

## Usage

Run the monitor with a YAML configuration file:

```shell
python monitor.py config.yaml
```

### Configuration Format

The tool accepts a YAML file containing a list of endpoints to monitor. Each endpoint should have the following structure:

```yaml
- body: '{"foo":"bar"}' # Request body (optional)
  headers: # HTTP headers (optional)
    content-type: application/json
  method: POST # HTTP method (optional, defaults to GET)
  name: sample body up # A descriptive name for the endpoint (required)
  url: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/body # The URL to monitor (required)
- name: sample index up
  url: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/
- body: "{}"
  headers:
    content-type: application/json
  method: POST
  name: sample body down
  url: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/
- name: sample error down
  url: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/error
```

## Availability Criteria

An endpoint is considered "UP" (available) only if:

1. It returns a status code between 200 and 299, AND
2. It responds within 500ms

## Issues Identified and Fixed

The following issues were identified in the original code and addressed in this implementation:

1. **YAML Validation**: Check if the YAML being parsed has all the required fields and handle request body based on content type.

2. **Response Time Check**: Added validation to ensure that endpoints respond within 500ms to be considered available.

3. **Availability Calculation**: Reset domain statistics for each monitoring cycle to provide accurate interval-based reporting.

4. **Configurable HTTP Methods**: Properly handles the HTTP method from configuration with a default of GET when not specified.

5. **Logging Improvements**: Added structured logging with timestamps and log levels.

6. **Production Readiness**: Added features for production environments:
   - Dual logging to console and file
   - Proper exception handling
   - Meaningful error messages
   - Timeout for HTTP requests

## Output Example

The tool produces output in the following format:

```log
[04/08/2025 04:22:57 PM] - [INFO] - Monitor triggered for 4 endpoints.
[04/08/2025 04:22:58 PM] - [WARNING] - STATUS: DOWN - URL: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/body - Slow response: 1278.87ms
[04/08/2025 04:22:59 PM] - [WARNING] - STATUS: DOWN - URL: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/ - Slow response: 1325.93ms
[04/08/2025 04:23:01 PM] - [WARNING] - STATUS: DOWN - URL: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/ - Slow response: 1428.55ms
[04/08/2025 04:23:03 PM] - [WARNING] - STATUS: DOWN - URL: https://dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com/error - Slow response: 2213.39ms
[04/08/2025 04:23:03 PM] - [INFO] - --- Domain Availability Summary ---
[04/08/2025 04:23:03 PM] - [INFO] - dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com has 0.00% availability percentage (0/4 endpoints up)

Trying again in 15s...
```
