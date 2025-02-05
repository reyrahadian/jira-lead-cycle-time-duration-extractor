# Stage Thresholds
STAGE_THRESHOLDS = {
    'default': {'warning': 2, 'critical': 5},
    'In Development': {'warning': 3, 'critical': 6},
    'In Code Review': {'warning': 1, 'critical': 2},
    'In PR Test': {'warning': 2, 'critical': 3},
    'In SIT Test': {'warning': 2, 'critical': 3},
    'In UAT Test': {'warning': 2, 'critical': 3},
    'Awaiting Prod Deployment': {'warning': 10, 'critical': 20},
    'Done': {'warning': 1000, 'critical': 1000}
}

# Colors
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'background': '#f8f9fa',
    'card': '#ffffff',
    'border': '#dee2e6'
}

# Valid Components
VALID_COMPONENTS = {
    'BFF': 'BFF',
    'FED': 'FED',
    'SFCC': 'SFCC',
    'XM': 'XM',
    'SITECORE': 'Sitecore',
    'CONTENTHUB': 'Content Hub'
}

# Priority Order
PRIORITY_ORDER = {
    'Highest': 0,
    'P1': 1,
    'High': 2,
    'P2': 3,
    'Medium': 4,
    'P3': 5,
    'Low': 6,
    'P4': 7,
    'N/A': 8
}

# Stage Columns
ALL_STAGE_COLUMNS_DURATIONS_IN_DAYS = [
    "Stage Backlog days",
    "Stage Rejected days",
    "Stage Open days",
    "Stage Blocked days",
    "Stage Waiting for support days",
    "Stage Failed Test days",
    "Stage In Analysis days",
    "Stage Ready for Development days",
    "Stage In Development days",
    "Stage In Progress days",
    "Stage In Code Review days",
    "Stage In PR days",
    "Stage Ready for PR Test days",
    "Stage In PR Test days",
    "Stage Awaiting SIT Deployment days",
    "Stage In Sit days",
    "Stage In QA days",
    "Stage Ready for SIT Test days",
    "Stage In SIT Test days",
    "Stage In Test days",
    "Stage Ready for Staging days",
    "Stage Awaiting UAT Deployment days",
    "Stage Deployed to UAT days",
    "Stage In Staging days",
    "Stage Ready for UAT Test days",
    "Stage In UAT Test days",
    "Stage In UAT days",
    "Stage Design Review days",
    "Stage PO Review days",
    "Stage Ready for Release days",
    "Stage Pre-Production days",
    "Stage Awaiting Prod Deployment days",
    "Stage In Production days",
    "Stage In Prod Test days",
    "Stage Done days",
    "Stage Closed days"
]

THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS = [
    "Stage Waiting for support days",
    "Stage In Development days",
    "Stage In Progress days",
    "Stage Blocked days",
    "Stage In Code Review days",
    "Stage Ready for PR Test days",
    "Stage In PR Test days",
    #"Stage Awaiting Deployment days",
    "Stage Awaiting SIT Deployment days",
    "Stage In Sit days",
    "Stage Ready for SIT Test days",
    "Stage In SIT Test days",
    "Stage In Test days",
    "Stage In QA days",
    "Stage Awaiting UAT Deployment days",
    "Stage In Staging days",
    "Stage Deployed to UAT days",
    "Stage Ready for UAT Test days",
    "Stage In UAT Test days",
    "Stage In UAT days",
    "Stage Pre-Production days",
    "Stage PO Review days",
    "Stage Awaiting Prod Deployment days",
    "Stage Ready for Release days",
    "Stage In Prod Test days"
]

THRESHOLD_STAGE_COLUMNS_IN_SPRINT_DURATION_IN_DAYS = [
    f"{stage.replace(' days', ' days in sprint')}" for stage in THRESHOLD_STAGE_COLUMNS_DURATION_IN_DAYS
]