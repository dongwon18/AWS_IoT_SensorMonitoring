# Title  
- Sensor Monitoring using AWS IoT  

# Purpose  
1. read sensor(DHT22, thermo-hygrometer) value
2. store data in DynamoDB
3. Monitor the value with Android App
4. Send email to administrator if the value exits the limit

# Total Architecture

<p align = 'center'>
  <img src = "/images/AWS IoT Architecture modified3.png" alt = "total architecture of project"> <br/>
  total architecture of project
</p>

1. Measure temperature, humidity using DHT22.  
2. Send sensor values to RPI using Serial communication.  
3. RPI formats the data in json form.  
4. Send messages to AWS IoT Core using MQTT protocol.  
5. Save data to DynamoDB using AWS IoT Rule.  
6. Check the value if it exceed the limit by AWS IoT Rule.  
7. Send email to administrators using AWS IoT Rule, AWS Lambda, AWS SNS.  
8. Get values from DynamoDB using AWS Lambda.  
9. Using AWS Amplify and API Gateway, monitor sensor values at the web page.  

# Developing Environment
- RaspberryPi
    - RaspberryPi 4B 4GB RAM
    - Raspberrypi OS 32bit
    - 16GB SD card
- Developing Language
    - Python

# For detail
- Refer my blog
    - [Tutorial of AWS IoT](https://dongwon18.github.io/categories/#aws-iot) 
    - [Project detail](https://dongwon18.github.io/categories/#sensormonitoring)

# Reference
- AWS IoT Development Guide and sample code
