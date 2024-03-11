import requests

# The URL where we will send the POST request
url = "http://ec2-3-142-149-227.us-east-2.compute.amazonaws.com/store-regen-signal"

# The number you want to send as plain text
data = '125'

# Send POST request
response = requests.post(url, data=data)

# Print the response
print("Status Code:", response.status_code)
print("Response Text:", response.text)
