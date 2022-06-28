
from flask import Flask, render_template, request
import key_config as keys
import boto3
import random
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
OTP = 0
email_glo = ""
application = app = Flask(__name__)


dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=keys.ACCESS_KEY_ID,
                          aws_secret_access_key=keys.ACCESS_SECRET_KEY)

# for update_item in dynamodb table
dynamodb_client = boto3.client('dynamodb')


@app.route('/')
def index():
    return render_template('index1.html')


@app.route('/signup', methods=['post'])
def signup():
    if request.method == 'POST':
        email = request.form['mail']
        password = request.form['pass']
        try:
            if("@" in email and password):

                table = dynamodb.Table('users')

                table.put_item(
                    Item={
                        'email': email,
                        'password': password
                    },
                    ConditionExpression='attribute_not_exists(email)'
                )
                return render_template('login1.html')
        except:
            return render_template('index1.html')
    return render_template('index1.html')


@app.route('/login', methods=['post'])
def login():
    return render_template('login1.html')


@app.route('/check', methods=['post'])
def check():
    if request.method == 'POST':
        table = dynamodb.Table('users')
        email = request.form['mail']
        password = request.form['pass']
        try:
            response = table.query(
                KeyConditionExpression=Key('email').eq(email)
            )
            items = response['Items']
            if password == items[0]['password']:
                return "success!"
            return render_template("login1.html")
        except:
            return render_template("login1.html")


@app.route('/forgot', methods=['post'])
def forgot():
    return render_template("forgot.html")


@app.route('/checkforgot', methods=['post'])
def checkforgot():
    if request.method == 'POST':
        table = dynamodb.Table('users')
        email = request.form['mail']
        global email_glo
        email_glo = email
        try:
            response = table.query(
                KeyConditionExpression=Key('email').eq(email)
            )
            global OTP
            OTP = random.randint(1000, 9999)
            mail_send(email, OTP)
            return render_template("enterotp.html")
        except:
            return render_template("forgot.html")


@app.route('/otpcheck', methods=['post'])
def otpcheck():
    if request.method == 'POST':
        try:
            user_otp = request.form['otp']
            print(user_otp)
            print(type(user_otp))
            print(OTP)
            if(OTP == int(user_otp)):
                print("yes")
                return render_template('resetpass.html')
        except:
            return render_template('enterotp.html')

    return render_template('enterotp.html')


@app.route('/resetpassword', methods=['post'])
def resetpassword():
    if request.method == 'POST':
        email = email_glo
        password = request.form['pass']
        if(password):
            key = {
                'email': {'S': email}
            }

            response = dynamodb_client.update_item(
                TableName='users',
                Key=key,
                ExpressionAttributeNames={
                    '#ps': 'password'
                },
                UpdateExpression="set #ps = :pass",
                ExpressionAttributeValues={
                    ':pass': {
                        'S': password
                    }
                }
            )
            return render_template('login1.html')
    return render_template('resetpass.html')


def mail_send(email, OTP):

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
                    <p>                   
                    OTP: """ + str(OTP) + """
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
        # print(response['MessageId'])


if __name__ == "__main__":

    app.run(debug=True)
