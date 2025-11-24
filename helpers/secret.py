import boto3
from botocore.exceptions import ClientError
from helpers.config import AppConfig, AWSConfig
from helpers.loog import logger

class AWSSecretManager(object):

    def __init__(self):
        self.app_conf = AppConfig()
        self.aws_conf = AWSConfig()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            session = boto3.session.Session()
            self._client = session.client(
                service_name='secretsmanager',
                region_name=self.aws_conf.aws_region
            )
        return self._client
    
    def get_secret(self, secret_key: str) -> str:
        try:
            
            get_secret_value_response = self.client.get_secret_value(
                SecretId=self.aws_conf.aws_secret_name
            )
            secret_value = get_secret_value_response['SecretString']
            secret = eval(secret_value).get(secret_key, "")

            return secret
        except ClientError as e:
            logger.error(f"[FE-AWS] Error retrieving secret {secret_key}: {e}")
            return None
