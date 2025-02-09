# Jira Tickets Analysis Dashboard

A Dash-based web application for visualizing and analyzing Jira ticket data. This dashboard provides insights into ticket progression, team velocity, and project health metrics.

## Pre-requisites
- [Conda](https://www.anaconda.com/download/success)
- [Node.js](https://nodejs.org/en/download)

## Setup Instructions

1. **Create a Conda Environment**:
   ```bash
   conda create -n jira-dashboard
   conda activate jira-dashboard
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Data Source**:
   - Update `config.yaml` with your JIRA credentials
   - Update the JQL query to filter the data you want to analyze

4. **Run the Reporting Application**:
   ```bash
   python run-report.py
   ```

5. **Access the Dashboard**:
   - Open a web browser
   - Navigate to `http://localhost:8081`