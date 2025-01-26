# How to Run the Dashboard

1. Run the following command to generate csv file from jira
```
npm run extract
```

2. Run the following command to run the dashboard
```
# update reports/jira-ticket-analysis.py with the path of the csv file
wsl
/home/rey/anaconda3/envs/mecca-engineering-health/bin/python /mnt/c/workspace/jira-lead-cycle-time-duration-extractor/reports/jira-ticket-analysis.py
```


