# Scheduled Job Status Dashboard Automation Tool

## Overview
This tool connects to a MySQL database to retrieve and display scheduled job status logs in a live-updating Tkinter GUI dashboard.

It provides:
- Running jobs started today without subsequent success/failure
- Failed jobs within the last 7 days
- Successful jobs within the last 7 days

## Features
- Live-updating dashboard with color-coded tables
- Local timezone-aware timestamps
- Simple configuration for test vs production databases

## Requirements
- Python 3.12+
- pandas
- mysql-connector-python
- tzlocal
- Tkinter (standard)
- zoneinfo (Python 3.9+ standard)

## Setup
1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd <repo_folder>
