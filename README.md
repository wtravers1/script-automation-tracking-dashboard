Scheduled_Job_Status_Dashboard_README: |
  # Scheduled Job Status Dashboard Automation Tool

  ## Overview
  The Scheduled Job Status Dashboard connects to a MySQL database to retrieve and display scheduled job status logs in a live-updating Tkinter GUI.

  It provides three key views:
  - **Running Jobs** – Jobs started today without subsequent success or failure
  - **Failed Jobs (last 7 days)** – Jobs that failed recently
  - **Successful Jobs (last 7 days)** – Jobs that completed successfully

  ## Features
  - Live-updating, color-coded dashboard
  - Local timezone-aware timestamps
  - Configurable refresh interval
  - Test mode vs production mode via a simple flag

  ## Requirements
  - Python 3.12+
  - pandas
  - mysql-connector-python
  - tzlocal
  - Tkinter (standard library)
  - zoneinfo (standard in Python 3.9+)

  ## Installation
  1. Clone the repository:
     ```bash
     git clone <repo_url>
     cd <repo_folder>
     ```
  2. Install dependencies:
     ```bash
     pip install pandas mysql-connector-python tzlocal
     ```
  3. Update the database configuration in the script (`DB_CONFIG`) with your credentials.

  ## Configuration
  - `MY_ARGS.TEST` – Set to `True` to use the test database
  - `REFRESH_INTERVAL` – Dashboard refresh interval in milliseconds (default: 15000)

  ## Usage
  Run the dashboard:
  ```bash
  python scheduled_job_dashboard.py
