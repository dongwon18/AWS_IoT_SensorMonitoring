# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
from boto3.dynamodb.conditions import Key
# import two packages to help us with dates and date formatting
from datetime import datetime, timedelta, timezone
import time

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('Sensor_data')
# store the current time in a human readable format in a variable




# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    
    now =  datetime.now() # '2021-08-24 05:26:20' 
    now_timestamp = int(time.mktime(now.timetuple())*1000) #int(time.mktime(datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()) * 1000)
    print(now_timestamp)
    start = now - timedelta(seconds = 10) #'2021-08-24 05:25:58' 
    start_timestamp = int(time.mktime(start.timetuple())*1000) #int(time.mktime(datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timetuple()) * 1000) 
    print(start_timestamp)
    client_Id = event['client_Id']

# write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    response = table.query(
        Limit = 3,
        KeyConditionExpression = Key('client_Id').eq(client_Id) & Key('store_time').between(start_timestamp, now_timestamp)
            
            )
# return a properly formatted JSON object

    data = response['Items']
    if(len(data) == 0):
        print("no such data")
        
        return{
            'statusCode': 204
            
        }
    else:
        temp = round(data[0]['sensor_data']['temperature'], 3)
        humidity = round(data[0]['sensor_data']['humidity'], 3)
        stime = data[0]['store_time']
        KST = timezone(timedelta(hours=9))
        date = datetime.fromtimestamp(stime/1000, KST).strftime('%Y-%m-%d %H:%M:%S')
    
        
        json_form = {"time": date, "temp": str(temp), "humidity": str(humidity)}
        
        return {
            'statusCode': 200,
            'body': json.dumps(json_form)
        }
