# aws-slack-alert

Use this to send an slack message when a new instance ec2 is created with a SSD disk.

#### What do you need before ####

* python 3.6
* boto3 (pip install boto3)
* Slack webhook (see https://api.slack.com/incoming-webhooks)
* AWS Credentials (AWS KEY and SECRET KEY)

#### How to use ####

**Step 1:** Create a lambda function using the [alertNewSSDInstance.py](/alertNewSSDInstance.py)

**Step 2:** Create a CloudWatch Events > Rule to trigger a lambda function

Event Pattern:

``` json
{
  "source": [
    "aws.ec2"
  ],
  "detail-type": [
    "EBS Volume Notification"
  ],
  "detail": {
    "event": [
      "createVolume",
      "modifyVolume"
    ]
  }
}
```
