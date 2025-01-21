import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta
import seaborn as sns
print(os.listdir())
 
file_path = 'jenkins_jobs_last_30_days-2024083345.xlsx'
df = pd.read_excel(file_path)
 
# Cleaning the dataset
df["Server Name"] = df['Server Name'].str.split('//').str[1].str.split('.').str[0]
 
#Stats for each Jenkins Servers
plt.figure(figsize=(4, 2))
sns.countplot(x='Server Name', data=df)
plt.title('Jenkins Stats for each Server')
plt.xticks(rotation=45)
plt.show()
 
df.groupby('Server Name')['Result'].value_counts()
 
#Find the Total Jobs by each Server
server_counts = df['Server Name'].value_counts()
plt.figure(figsize=(5, 5))
server_counts.plot.pie(autopct='%1.1f%%', startangle=90, colors=['lightblue', 'lightgreen', 'coral'], 
                      wedgeprops={'edgecolor': 'black'})
plt.ylabel('')  # Remove y-label
plt.title('Server Name Distribution')
 
# Show chart
plt.show()
server_counts
 
#Find the list of total jobs for each jenkins server
jenkins1 = df[df['Server Name'] == "jenkins1"]
proto = df[df['Server Name'] == "proto-jenkins"]
jenkins = df[df['Server Name'] == "jenkins"]
#################################################
#Bar Plot for Job Results for Each Server
plt.figure(figsize=(12, 6))
sns.countplot(x='Result', data=jenkins1, palette='Blues', label='jenkins1')
sns.countplot(x='Result', data=proto, palette='Reds', label='proto-jenkins', alpha=0.7)
sns.countplot(x='Result', data=jenkins, palette='Greens', label='jenkins', alpha=0.5)
plt.title('Job Results Count for Different Jenkins Servers')
plt.xticks(rotation=45)
plt.legend()
plt.show()
 
# Total jobs run from each Server Name each day with graph
 
df['Date'] = df['Timestamp'].dt.date
jobs_per_day_per_server = df.groupby(['Server Name', 'Date']).size().unstack(fill_value=0)
 
# Plotting total jobs run each day from each server
jobs_per_day_per_server.T.plot(kind='line', figsize=(6,3), marker='o')
plt.title("Total Jobs per Day from Each Server")
plt.xlabel("Date")
plt.ylabel("Number of Jobs")
plt.xticks(rotation=45)
plt.legend(title="Server Name")
plt.show()
 
# Further analysis: Summary statistics for the jobs
job_summary = df.groupby(['Server Name', 'Result']).agg(
    total_jobs=('Job Name', 'count'),
    first_job=('Timestamp', 'min'),
    last_job=('Timestamp', 'max'),
    avg_builds_per_day=('Date', lambda x: x.nunique())
).reset_index()
 
# Display summary
job_summary
