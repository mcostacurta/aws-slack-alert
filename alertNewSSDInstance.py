'''This code list the new SSD volume in AWS and send an message alert to slack
'''
import boto3
import json
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger()
#uncomment below to see log details
#logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)


BOT_USERNAME = 'Amazon EC2 - EBS Volume Notification'
SLACK_CHANNEL = "<slack channel>"

ACCESS_KEY = '<aws access key>'
SECRET_KEY = '<aws secret key>'


def get_ssd_volumes(region, resources):
    """This function filter and return only SSD resource
    """
    logger.info('>> Resources List: ' + str(resources))
    logger.info('>> Filtering Resources...')
    
    session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name = region)

    ssd_volumes_list = []
    for resource in resources:
        try:
            ec2 = session.resource('ec2', region_name=region)
            volume = ec2.Volume(resource.split('/')[1])
            
            logger.info('--> Volume Id: ' + volume.id)
            logger.info('----> Volume size: ' + str(volume.size))
            logger.info('----> Volume type: ' + volume.volume_type)
            volume_instance_id = (volume.attachments[0]['InstanceId'] if volume.attachments else "NOT IN USE")
            logger.info('----> Volume Instance Id attached: ' + volume_instance_id)
            
            if volume.volume_type == 'gp2':
                ssd_volumes_list.append(" VolumeId: " + volume.id + " | Type: " + volume.volume_type + " | Size: " + str(volume.size) + " | State: " + volume.state + " | Instance Id: " + volume_instance_id + "\n")
                logger.info('----> SSD Added!')

        except Exception as e:
            logger.error(e)

    logger.info('>> Resources filtered.')
    return ssd_volumes_list

def send_message_to_slack(MSG):
    """This function send a formated message to Slack App

    :param MSG: Text to be included in the post message in Slack.
    """
    from urllib import request, parse
    import json

    logger.info('>> Sending slack message...')

    HOOK_URL = '<slack hook address>'
    post={"channel": "#" + SLACK_CHANNEL, "username": BOT_USERNAME, "text": "{0}".format(MSG), "icon_emoji": ":smile:"}
    params = json.dumps(post).encode('utf8')

    logger.info("##### SEND MESSAGE TO SLACK: " + str(params))

    try:
        req = request.Request(HOOK_URL, data=params, headers={'Content-Type': 'application/json'})
        resp = request.urlopen(req)
    except Exception as em:
        logger.error("EXCEPTION: " + str(em))

    logger.info('>> Slack message sent!')

#if __name__ == "__main__":
def lambda_handler(event, context):
    """This function is the one that will be runned by AWS Lambda.

    To run this code locally, after you prepare your environment, comment the
    line ``def lambda_handler(event, context):`` and uncomment the line
    ``if __name__ == "__main__":``
    """
    logger.info('>> Start script...')
    logger.info('>> Got event{}'.format(event))
    logger.info('>> Region: ' + event['region'])
    resources = event['resources']
    logger.info('>> Resources length: ' + str(len(resources)))

    if resources:
        ssd_volumes_list = get_ssd_volumes(event['region'],resources)
    
    MSG = ""
    if ssd_volumes_list:
        MSG = 'These are the new SSD volumes:\n\n'
        for volume_msg in ssd_volumes_list:
            MSG = MSG + volume_msg

    if MSG != "":
        send_message_to_slack(MSG)

    logger.info('>> End script!')
    return {
        'statusCode': 200,
        'body': json.dumps('Completed!')
    }