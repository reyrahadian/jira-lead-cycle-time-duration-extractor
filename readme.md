# Jira Metrics Reporting System

A system for extracting Jira metrics and visualizing them through an interactive dashboard. Combines a Jira data extractor (Node.js) with a reporting dashboard (Python).

## Features

- Automated Jira data extraction:
  - Stage durations and flow status
  - Cycle time and lead time calculations
  - Custom field support
- Interactive dashboard with:
  - Sprint analysis
  - Team metrics
  - Project/squad filtering
- Docker containerization
- AWS deployment support

## Quick Start

### Running the apps
1. Update the `.env` file with the correct values
2. Run the following commands to build and start the apps
`docker compose build`
`docker compose up`