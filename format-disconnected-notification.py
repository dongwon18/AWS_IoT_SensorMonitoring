"""
* Lambda function of sending disconnection data to admin.
*
* get parameters from AWS IoT Rule
* expects event parameter to contain:
*   {
*       "timestamps":
*       "clientId":
*       "eventType":  
*       "disconnectReason":
*       "notify_topic_arn": 
*   }
*
* Reference: AWS IoT Development Guide
"""
import boto3
from datetime import datetime, timezone, timedelta
import time

def lambda_handler(event, context):

    # Create an SNS client to send notification
    sns = boto3.client('sns')
    
    # Change timestamp to time
    # Set timezone to KST
    timestamp = int(event['timestamp'])
    KST = timezone(timedelta(hours=9))
    date = datetime.fromtimestamp(timestamp/1000, KST).strftime('%Y-%m-%d %H:%M:%S')

    # Format text message from data
    message_text = "Device {0} is disconnected\n at : {1} KST \n event : {2} \n reason : {3}".format(
            str(event['clientId']),
            date,
            str(event['eventType']),
            str(event['disconnectReason'])
        )

    # Publish the formatted message
    response = sns.publish(
            TopicArn = event['notify_topic_arn'],
            Message = message_text
        )

    return response
