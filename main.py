import logging
import os
from pprint import pprint

import requests
import urllib3
from dotenv import load_dotenv

import utils

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    processed_images_path = 'upload'
    source_path = 'images'

    # os.makedirs(processed_images_path, exist_ok=True)
    os.makedirs(source_path, exist_ok=True)
    urllib3.disable_warnings()
    response = requests.get('https://xkcd.com/353/info.0.json')
    response.raise_for_status()
    review_result = response.json()
    pprint(review_result['img'])

    utils.download_image('python', review_result['img'], source_path)
    print(review_result['alt'])

    vk_upload()


def vk_upload():
    load_dotenv()
    vk_app_id = os.getenv('VK_APP_ID')
    access_token = os.getenv('ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    owner_id_group = -int(vk_group_id)

    # запрашиваем upload_url
    print('запрашиваем upload_url')
    params = {
        'group_id': vk_group_id,
        'access_token': access_token,
        'v': 5.126,
    }
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    review_result = response.json()['response']
    pprint(review_result)

    # выгружаем файл на upload_url
    print('выгружаем файл на upload_url')
    with open('images\python.png', 'rb') as file:
        url = review_result['upload_url']
        files = {
            'photo': file,  # media — это имя поля данных, как указано в доке к API
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        review_result = response.json()
        pprint(review_result)

    print('сохраняем файл в альбоме')
    params = {
        'server': review_result['server'],
        'photo': review_result['photo'],
        'hash': review_result['hash'],
        'group_id': vk_group_id,
        'access_token': access_token,
        'v': 5.126,
    }
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    pprint(response.json())
    save_wall_photo_result = response.json()['response'][0]
    pprint(save_wall_photo_result)

    print('размещаем фото на стене')
    params = {
        'owner_id': owner_id_group,
        'attachments': f'photo{save_wall_photo_result["owner_id"]}_{save_wall_photo_result["id"]}]',
        'from_group': 1,
        'message': 'Магия!',
        'signed': 1,
        'access_token': access_token,
        'v': 5.126,
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()
    review_result = response.json()
    pprint(review_result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # main()

    vk_upload()
