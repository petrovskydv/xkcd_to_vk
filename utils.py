import logging
import os

import requests

logger = logging.getLogger(__name__)


def download_image(file_name, url, source_path):
    response = requests.get(url, verify=False)
    response.raise_for_status()

    result_file_name = f'{file_name}{os.path.splitext(url)[1]}'
    file_path = os.path.join(source_path, result_file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.info(f'download file: {file_path}')