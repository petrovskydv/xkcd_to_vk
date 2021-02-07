import logging
import os
import random

import requests
import urllib3
from dotenv import load_dotenv

import utils

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    load_dotenv()
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    group_owner_id = -int(vk_group_id)
    vk_api_version = 5.126
    start_number = 0
    file_name = 'image'
    source_path = 'images'
    os.makedirs(source_path, exist_ok=True)

    urllib3.disable_warnings()

    image_url, image_title = fetch_comic_book_url_and_description(get_random_comic_book_number(start_number))
    file_path = utils.download_image(file_name, image_url, source_path)

    params = {
        'access_token': vk_access_token,
        'v': vk_api_version,
    }

    try:
        upload_result = upload_image_to_vk_server(
            file_path, fetch_server_address_to_upload_image(params, vk_group_id))

        post_image_on_wall(
            group_owner_id,
            save_image_to_album(upload_result, vk_group_id, params),
            params,
            image_title)
    except utils.VkException as e:
        print(f'Публикация завершилась ошибкой: {e}')
    finally:
        logger.info('удаляем файл')
        os.remove(file_path)

    logger.info('удаляем файл')
    os.remove(file_path)


def fetch_comic_book_url_and_description(image_number):
    logger.info('получаем ссылку на файл')
    response = requests.get(f'https://xkcd.com/{image_number}/info.0.json')
    response.raise_for_status()
    review_result = response.json()
    logger.debug(review_result)
    return review_result['img'], review_result['alt']


def post_image_on_wall(owner_id_group, save_wall_photo_result, params, image_title):
    logger.info('размещаем фото на стене')

    params['owner_id'] = owner_id_group
    params['attachments'] = f'photo{save_wall_photo_result["owner_id"]}_{save_wall_photo_result["id"]}]'
    params['message'] = image_title

    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()
    logger.debug(response.json())
    raise_for_vk_error(response.json())


def save_image_to_album(upload_result, vk_group_id, params):
    logger.info('сохраняем файл в альбоме')

    params['server'] = upload_result['server']
    params['photo'] = upload_result['photo']
    params['hash'] = upload_result['hash']
    params['group_id']: vk_group_id

    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    review_result = response.json()
    logger.debug(review_result)
    raise_for_vk_error(review_result)
    return review_result['response'][0]


def upload_image_to_vk_server(file_path, upload_url):
    logger.info('выгружаем файл на upload_url')
    with open(file_path, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        review_result = response.json()
        logger.debug(review_result)
        raise_for_vk_error(review_result)
    return review_result


def fetch_server_address_to_upload_image(params, vk_group_id):
    logger.info('запрашиваем upload_url')
    params['group_id'] = vk_group_id
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    review_result = response.json()
    logger.debug(review_result)
    raise_for_vk_error(review_result)
    return review_result['response']['upload_url']


def get_random_comic_book_number(start_number):
    logger.info('получаем случайный комикс')
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    review_result = response.json()
    logger.debug(review_result)
    return random.randint(start_number, review_result['num'])


def raise_for_vk_error(review_result):
    if 'error' in review_result:
        logger.info(f'Error {review_result["error"]["error_msg"]}')
        raise utils.VkException(review_result)


if __name__ == '__main__':
    main()
