#!/usr/bin/env python3
import boto3
import pandas as pd
from pprint import pprint
from datetime import datetime
import sys

# Get profiles from command-line arguments
profiles = sys.argv[1:]
if not profiles:
    print("Please provide at least one AWS profile.")
    sys.exit(1)

current_time = datetime.now().strftime("%Y-%m-%d-%H%M%S")
final_output = []

def get_instance_tags(tags):
    """Convert list of tags into a dictionary for easier readability."""
    return {tag['Key']: tag['Value'] for tag in tags} if tags else {}

# Loop through each profile and gather instance details
for profile in profiles:
    try:
        # Initialize the session with the current profile
        session = boto3.session.Session(profile_name=profile)
        ec2_client = session.client("ec2", region_name="us-west-1")
        response_reg = ec2_client.describe_regions()
        all_regions = [region['RegionName'] for region in response_reg['Regions']]

        for region in all_regions:
            # Create a new EC2 client for each region
            ec2_client = session.client("ec2", region_name=region)
            response_ec2 = ec2_client.describe_instances()

            for reservation in response_ec2['Reservations']:
                for instance in reservation['Instances']:
                    tags = get_instance_tags(instance.get('Tags'))
                    instance_data = {
                        'OwnerId': reservation['OwnerId'],
                        'InstanceId': instance.get('InstanceId'),
                        'Instance_State': instance['State']['Name'],
                        'Architecture': instance.get('Architecture'),
                        'InstanceType': instance.get('InstanceType'),
                        'ImageId': instance.get('ImageId'),
                        'KeyName': instance.get('KeyName'),
                        'Monitor': instance['Monitoring']['State'],
                        'PlatformDetails': instance.get('PlatformDetails'),
                        'PrivateIpAddress': instance.get('PrivateIpAddress'),
                        'SubnetId': instance.get('SubnetId'),
                        'VpcId': instance.get('VpcId'),
                        'InterfaceID': [interface['NetworkInterfaceId'] for interface in instance['NetworkInterfaces']],
                        'GroupNames': [group['GroupName'] for group in instance['SecurityGroups']],
                        'LaunchTime': instance.get('LaunchTime').strftime("%Y-%m-%d %H:%M:%S"),
                        'Profile': profile,
                        'Region': region,
                        'Name': tags.get('Name'),
                        'User_Application': tags.get('user:Application'),
                        'User_Environment': tags.get('user:Environment'),
                        'ITOwnerName': tags.get('user:ITOwnerName'),
                        'ITTeamOwner': tags.get('user:ITTeamOwner'),
                        'terraform.io/workspace': tags.get('terraform.io/workspace'),
                        'aws:cloudformation:stack-name': tags.get('uaws:cloudformation:stack-name'),
                        'Tags': tags
                    }
                    final_output.append(instance_data)

    except Exception as e:
        print(f"Error in profile {profile} or region {region}: {e}")

# Convert final output to a DataFrame and save to Excel
df = pd.DataFrame(final_output)
if not df.empty:
    # Join profiles in filename for clarity
    profiles_str = "_".join(profiles)
    excel_file_name = f"EC2-Instances-{current_time}.xlsx"
    df.to_excel(excel_file_name, index=False)

    # Print final output for verification
    pprint(final_output)
    print(f"Data saved to {excel_file_name}")
