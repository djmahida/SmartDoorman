import json
import boto3
from botocore.vendored import requests
import logging



def lambda_handler(event, context):
    # TODO implement
            
    logging.info("API CALLED. EVENT IS:{}".format(event))

    print("this", event)
    
    VisitorName = event["currentIntent"]["slots"]["VisitorName"]
    Purpose = event["currentIntent"]["slots"]["Purpose"]


    smsClient = boto3.client('sns')
    
    
    messageToSMS = "Hey!! I know you are busy with work, but I detected that this might be urgent. Someone is at your door. The persons name is {} and the person is here for the pupose of {}. Please check with the person if its important".format(VisitorName,Purpose)
    mobile = "*********"
    
    SENDER = "****************"
    RECIPIENT = "*****************"
    AWS_REGION = "us-east-1"
    SUBJECT = " Someone is at your door "
    BODY_TEXT = messageToSMS
    BODY_HTML = "<html><head></head><body><h1><font color='red'>Someone at your door!</font></h1><p>'Hey!! I know you are busy with work, but I detected that this might be urgent. Someone is at your door. The persons name is {} and the person is here for the pupose of {}. Please check with the person if its important'<p></body></html>".format(VisitorName,Purpose)
    CHARSET = "UTF-8"
    
    client = boto3.client('ses',region_name=AWS_REGION)
    response = client.send_email(
    Destination={
        'ToAddresses': [
            RECIPIENT,
        ],
    },
    Message={
        'Body': {
            'Html': {
                'Charset': CHARSET,
                'Data': BODY_HTML,
            },
            'Text': {
                'Charset': CHARSET,
                'Data': BODY_TEXT,
            },
        },
        'Subject': {
            'Charset': CHARSET,
            'Data': SUBJECT,
        },
    },
    Source=SENDER
    )
    print("Email sent! Message ID:"),
    print('RESPONSE',response['MessageId'])


    # smsClient.publish(
    # PhoneNumber="+1"+mobile,
    # Message=messageToSMS
    #     )
        
    if (Purpose is None):
        return {
                "sessionAttributes": {
                # "key1": "value1",
                # "key2": "value2"
                
              },
                                # "sessionAttributes": {},
                "dialogAction": {
                            "type": "Close",
                            "fulfillmentState": "Fulfilled",
                            "message": {
                            "contentType": "PlainText",
                            "content": "I am sorry that I could not identify your purpose properly. But I will let the owner know your name. Thank you for letting me know."
                                        }
                                }               
                }
    
    elif (VisitorName is None):
        return {
                "sessionAttributes": {},
                "dialogAction": {
                            "type": "Close",
                            "fulfillmentState": "Fulfilled",
                            "message": {
                            "contentType": "PlainText",
                            "content": "I am sorry that I could not identify your name and purpose properly. But I will let the owner know you came. Thank you for letting me know."
                                        }
                                }               
                }
          
                
    else:
        return {"sessionAttributes": {},
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                  "contentType": "PlainText",
                  "content": "I will let the owner know your name and purpose of coming. Thank you for letting me know."
                },
               }}
              