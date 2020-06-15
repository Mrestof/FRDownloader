import os
import requests
import tempfile
import shutil

from zipfile import ZipFile
from bs4 import BeautifulSoup

APP = 274920


def get_link(item: int, app=APP) -> str:
    """
    Return link of the archived character files.

    :param item: id of an item.
    :param app: id of the app (default is 274920).
    :return: link for downloading the character archive.
    """
    # online service for downloading steam workshop content
    url = 'http://steamworkshop.download/online/steamonline.php'
    data = {'item': item, 'app': app}

    # todo check if request has sent (outside the function)
    # extracting the url of a file from server response and checking for some errors
    r = requests.post(url=url, data=data)
    assert len(r.text) > 120,\
        f'link for downloading was not received, try again later\nPOST request has returned: {r.text}'

    return r.text.split('\'')[1]


def download_and_place(url: str, path: str, item: int) -> str:
    """
    Download archive and unpacking it into the characters folder.

    :param url: link of the archive.
    :param path: path where the FaceRig.exe is situated.
    :param item: id of the item to be unpacked.
    :return: text message about where the files were moved to.
    """

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


def parse(sort='trend', search='', page=1, amount=30, days=7, app=APP) -> dict:
    """
    Parse data for using in browse section of an FRDownloader.

    :param sort: the way items are sorted.
    :param search: string to find in titles of items.
    :param page: number of page you are looking to.
    :param amount: amount of items in page.
    :param days: time period of showed items (only for trend sort)
    :param app: id of the app (default is 274920)
    :return: dictionary of parsed data: links for images, titles as a text and ids of the items (characters).
    """

    items_data = {}
    additional_data = {}
    payload = {'appid': app, 'browsesort': sort, 'actualsort': sort, 'p': page, 'numperpage': amount}

    if search:
        payload['searchtext'] = search
        payload['childpublishedfileid'] = 0

    if sort == 'trend':
        payload['days'] = days

    html = requests.get('https://steamcommunity.com/workshop/browse', params=payload)
    soup = BeautifulSoup(html.text, 'html.parser')

    logo_tags = soup.find_all('img', 'workshopItemPreviewImage')
    logo_sources = [tag.get('src') for tag in logo_tags]
    items_data['img_sources'] = logo_sources

    rating_tags = soup.find_all('img', 'fileRating')
    rating_sources = [tag.get('src') for tag in rating_tags]
    items_data['rating_sources'] = rating_sources

    title_tags = soup.find_all('div', 'workshopItemTitle')
    title_texts = [tag.string for tag in title_tags]
    items_data['title_texts'] = title_texts

    author_tags = soup.find_all('div', 'workshopItemAuthorName')
    author_texts = ['by ' + str(tag.a.string) for tag in author_tags]
    items_data['author_texts'] = author_texts

    id_tags = soup.find_all('a', 'ugc')
    item_ids = [tag.get('data-publishedfileid') for tag in id_tags]
    items_data['item_ids'] = item_ids

    page_browse_div = soup.find('div', 'workshopBrowsePagingControls')
    try:
        additional_data['last_page'] = int(page_browse_div.contents[-3])
    except ValueError as error:
        print(error)
        if page_browse_div:
            page_tags = page_browse_div.find_all('a', 'pagelink')
            last_page = page_tags[-1].string
            additional_data['last_page'] = int(last_page)
    except IndexError as error:
        print(error)
        additional_data['last_page'] = 1
    except AttributeError as error:
        print(error)

    if item_ids:
        items_per_page_raw = soup.find('div', 'workshopBrowsePagingInfo').string
        items_per_page = items_per_page_raw.split(' ')[1]
        additional_data['items_range'] = items_per_page

    return {'items': items_data, 'additional': additional_data}


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
