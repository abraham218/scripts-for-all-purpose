import requests
import pandas as pd
from datetime import datetime, timedelta
from pprint import pprint
 
current_time = datetime.now().strftime("%Y-%m-%d-%H%M%S")
 
# Jenkins API credentials and list of servers
JENKINS_SERVERS = [
    {
        'url': 'https://jenkins1.billa.com',
        'username': 'abraham',
        'token': '1148993cfc8929ea251dbec339971'
    },
    {
        'url': 'https://jenkins2.billa.com',
        'username': 'abraham',
        'token': '11c70841741cdx4cb7a7342a93d4410'
    },
    {
        'url': 'https://jenkins3.billa.com',
        'username': 'abraham',
        'token': '115815abaab0c0qw34cx24dd66d200'
    },
    # Add more Jenkins servers as needed
]
 
 
# Define headers for the request
headers = {
    'Content-Type': 'application/json',
}
 
# Function to get jobs (including folder jobs) from a specific Jenkins server
def get_jenkins_jobs(jenkins_server, folder_url=''):
    folder_url = folder_url.strip('/')  # Ensure no extra slashes
    url = f'{jenkins_server["url"]}/{folder_url}/api/json?tree=jobs[name,url,builds[number,timestamp,result],jobs[name,url]]'
    try:
        response = requests.get(url, auth=(jenkins_server['username'], jenkins_server['token']), headers=headers)
        response.raise_for_status()  # Check if the request was successful (status code 200)
        # Parse JSON response
        jobs = response.json().get('jobs', [])
        all_jobs = []
 
        for job in jobs:
            # If the job has nested jobs, it's a folder
            if 'jobs' in job:
                folder_name = job['name']
                folder_jobs = get_jenkins_jobs(jenkins_server, f'{folder_url}/job/{folder_name}')
                all_jobs.extend(folder_jobs)  # Recursively fetch folder jobs
            else:
                all_jobs.append(job)  # Regular job
        return all_jobs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs from Jenkins: {e}")
        return []
 
# Function to flatten builds and filter jobs from the last 30 days
def flatten_job_data(jobs, server_name):
    job_data = []
    last_30_days = datetime.now() - timedelta(days=5)
    for job in jobs:
        job_name = job['name']
        job_url = job['url']
        # Process each build for the job
        builds = job.get('builds', [])
        if builds:
            for build in builds:
                # Convert timestamp to datetime and filter by last 30 days
                build_timestamp = pd.to_datetime(build['timestamp'], unit='ms')
                if build_timestamp >= last_30_days:
                    job_data.append({
                        'Server Name': server_name,
                        'Job Name': job_name,
                        'Job URL': job_url,
                        'Build Number': build['number'],
                        'Timestamp': build_timestamp,
                        'Result': build['result']
                    })
    return job_data
 
# Collect all job data from all servers
all_job_data = []
 
for server in JENKINS_SERVERS:
    print(f"Fetching jobs from {server['url']}...")
    jobs = get_jenkins_jobs(server)
    server_job_data = flatten_job_data(jobs, server['url'])  # Add server name for differentiation
    all_job_data.extend(server_job_data)
 
# Convert to pandas DataFrame
df = pd.DataFrame(all_job_data)
 
# Save to Excel
excel_filename = f"jenkins_jobs_last_30_days-{current_time}.xlsx"
df.to_excel(excel_filename, index=False)
print(f"Jenkins jobs data from the last 30 days saved to {excel_filename}")
 
pprint(all_job_data)
