import os
import requests
import tempfile
import shutil

from zipfile import ZipFile
from bs4 import BeautifulSoup

APP = 274920


def get_link(item: int, app=APP) -> str:
    # online service for downloading steam workshop content
    url = 'http://steamworkshop.download/online/steamonline.php'
    data = {'item': item, 'app': app}

    # extracting the url of a file from server response and checking for some errors
    # todo check if request has sent (outside the function)
    r = requests.post(url=url, data=data)
    assert len(r.text) > 120,\
        f'link for downloading was not received, try again later\nPOST request has returned: {r.text}'

    return r.text.replace('\'', '@@@').split('@@@')[1]


def download_and_place(url: str, path: str, item: int) -> str:
    # downloading content of a zip archive
    content = requests.get(url).content

    # compiling the destination path
    path = path[:-4] + '/Mod/VP/PC_CustomData/Objects'

    # creating temporary directory and unzipping archive
    with tempfile.TemporaryDirectory() as tmpdir:
        print(tmpdir)

        with open(f'{tmpdir}/cont.zip', 'wb') as f:
            f.write(content)

            with ZipFile(f'{tmpdir}/cont.zip') as zip_obj:
                zip_obj.extractall(f'{tmpdir}')

        # moving character dir to FaceRig characters directory
        character_dir = os.listdir(f'{tmpdir}/{item}')[0]
        path_to_character_dir = f'{tmpdir}/{item}/{character_dir}'

        shutil.move(path_to_character_dir, path)

    return f'{character_dir} was moved to the {path}'


def parse(sort='trend', page=1, amount=30, days=7, app=APP):
    data = {}
    payload = {'appid': app, 'browsesort': sort, 'actualsort': sort, 'p': page, 'numperpage': amount}

    if sort == 'trend':
        payload['days'] = days

    html = requests.get('https://steamcommunity.com/workshop/browse', params=payload)
    soup = BeautifulSoup(html.text, 'html.parser')

    logo_tags = soup.find_all('img', 'workshopItemPreviewImage')
    logo_sources = [tag.get('src') for tag in logo_tags]
    data['img_sources'] = logo_sources

    rating_tags = soup.find_all('img', 'fileRating')
    rating_sources = [tag.get('src') for tag in rating_tags]
    data['rating_sources'] = rating_sources

    title_tags = soup.find_all('div', 'workshopItemTitle')
    title_texts = [tag.string for tag in title_tags]
    data['title_texts'] = title_texts

    author_tags = soup.find_all('div', 'workshopItemAuthorName')
    author_texts = ['by ' + tag.a.string for tag in author_tags]
    data['author_texts'] = author_texts

    return data


# debug stuff

if __name__ == '__main__':

    item_code = int(input('Enter an item code: '))
    path_to_place = input('Enter path where the FaceRig.exe is placed: ')

    try:
        link = get_link(item_code)
        info = download_and_place(link, path_to_place, item_code)
    except AssertionError as err:
        print(err)
    except requests.exceptions.ConnectionError as err:
        print(err)
    else:
        print(info)
