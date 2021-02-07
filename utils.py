import logging
import os
from urllib.parse import urlparse, unquote

import requests

logger = logging.getLogger(__name__)


class VkException(Exception):
    def __init__(self, review_result):
        self.error_code = review_result['error']['error_code']
        self.error_msg = review_result['error']['error_msg']

    def __str__(self):
        return repr(f'error_code: {self.error_code}, error_msg:{self.error_msg}')


def download_image(file_name, url, source_path):
    response = requests.get(url, verify=False)
    response.raise_for_status()

    result_file_name = f'{file_name}{os.path.splitext(unquote(urlparse(url).path))[1]}'
    file_path = os.path.join(source_path, result_file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'download file: {file_path}')
    return file_path
