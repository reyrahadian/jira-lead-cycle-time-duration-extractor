# Jira Tickets Analysis Dashboard

A Dash-based web application for visualizing and analyzing Jira ticket data. This dashboard provides insights into ticket progression, team velocity, and project health metrics.

## Features

- **Real-time Filtering**: Filter data by project, component, sprint, and date range
- **Interactive Visualizations**:
  - Status Distribution Chart
  - Time in Stage Analysis
  - Sprint Burndown Chart
  - Team Velocity Tracking
- **Detailed Tables**:
  - All Tickets Overview
  - Blocked Tickets
  - At-Risk Tickets
- **Sprint Metrics**:
  - Total Tickets
  - Completion Rate
  - Blocked Items
  - Risk Assessment

## Project Structure

```
src/reporting_app/
├── __init__.py
├── app.py                 # Main application file
├── config/               # Configuration files
│   ├── __init__.py
│   ├── constants.py      # Constants and configurations
│   └── styles.py        # UI styles
├── components/          # UI components
│   ├── __init__.py
│   ├── header.py
│   ├── filters.py
│   ├── sprint_metrics.py
│   ├── charts.py
│   └── tables.py
├── callbacks/          # Interactive callbacks
│   ├── __init__.py
│   ├── filter_callbacks.py
│   ├── chart_callbacks.py
│   └── table_callbacks.py
└── utils/             # Utility functions
    ├── __init__.py
    ├── data_processing.py
    └── helpers.py
```

## Setup Instructions

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Data Source**:
   - Place your Jira data CSV file in the project root
   - Update the file path in `config/constants.py` if needed

4. **Run the Application**:
   ```bash
   python run-report.py
   ```

5. **Access the Dashboard**:
   - Open a web browser
   - Navigate to `http://localhost:8050`