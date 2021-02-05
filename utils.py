import glob
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


def convert_files_to_jpg(source_path, processed_images_path, instagram_image_size):
    image_paths = glob.glob(f'{source_path}/*.*')
    image_paths = sorted(image_paths)
    for file_path in image_paths:
        if os.path.splitext(file_path)[-1] == '.REMOVE_ME':
            continue
        image = Image.open(file_path)
        image.thumbnail(instagram_image_size)
        file_name = os.path.splitext(os.path.split(file_path)[-1])[0]
        image_path = os.path.join(processed_images_path, f'{file_name}.jpg')
        rgb_image = image.convert('RGB')
        rgb_image.save(image_path, format='JPEG')
        logger.info(f'save processed image: {image_path}')
        os.rename(file_path, f'{file_path}.REMOVE_ME')


def upload_images(bot, folder_path):
    logger.info('bot start')
    image_paths = glob.glob(f'{folder_path}/*.jpg')
    image_paths = sorted(image_paths)
    for image_path in image_paths:
        logger.info(f'uploading a file {image_path}')
        upload_result = bot.upload_photo(image_path, caption='Nice pic!')
        logger.info(f'upload result: {upload_result}')
