import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    
    print('Event',event)
    password = event['otp']
    
    sqsClient = boto3.resource('sqs')
    queue = sqsClient.get_queue_by_name(QueueName = "AuthenticateKnownUsers")

    smsClient = boto3.client('sns')
    
    for message in queue.receive_messages(MaxNumberOfMessages=10):
        data = message.body.split(":")
        message.delete()
        
        name = data[0]
        queuePassword = data[1]
        
        if queuePassword == password:
            json_data = {
                'name': name,
                'status' : 'familiar'
            }
            message.delete()
        else:
            json_data = {
            'name': name,
            'status' : 'incorrect'
        }
        return {
        "headers": {
        "Acess-Control-Allow-Origin": "*"
        },
        "statusCode": 200,
        "body": json_data
        }
    return {
    "headers": {
    "Acess-Control-Allow-Origin": "*"
    },
    "statusCode": 200,
    "body": {'status':'incorrect'}
    }
