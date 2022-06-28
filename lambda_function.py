import json
import boto3
from botocore.exceptions import ClientError


def mail_send(email, password):
    print("mail send")
    SENDER = "Ayash Hossain <ayash.hossain.fiem.cse19@teamfuture.in>"
    RECIPIENT = email

    AWS_REGION = "us-east-2"
    SUBJECT = "Amazon SES Test"
    BODY_TEXT = ("Amazon SES Test\r\n"
                 "This email was sent from our website "
                 )

    BODY_HTML = """
                <html>
                <head></head>
                <body>
                    <p>Successfully Registered
                    <br>
                    Email: """ + str(email) + """ <br>
                    Password: """ + str(password) + """
                    </p>
                </body>
                </html>
                """

    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)
    try:
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
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def lambda_handler(event, context):
	try:
		for record in event['Records']:

			if record['eventName'] == 'INSERT':
				handle_insert(record)

		return "Success!"
	except Exception as e:
		print(e)
		return "Error"


def handle_insert(record):
	print("Handling INSERT Event")
	newImage = record['dynamodb']['NewImage']
	email = newImage['email']['S']
	password = newImage['password']['S']
    print("before mail send")
	mail_send(email, password)
