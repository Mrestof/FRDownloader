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

    # extracting the url of a file from server response and checking for some errors
    r = requests.post(url=url, data=data)
    assert len(r.text) > 120,\
        f'link for downloading was not received, try again later\nPOST request has returned: {r.text}'

    # still trying to catch this rare bug
    print(r.text)

    return r.text.split('\'')[1]


# todo split this function on two different: check path, download and place item
def download_and_place(url: str, path: str, item: int, is_direct=False) -> dict:
    """
    Download archive and unpacking it into the characters folder.

    :param url: link of the archive.
    :param path: path where the FaceRig.exe is situated or direct path to characters folder.
    :param item: id of the item to be unpacked.
    :param is_direct: change to True if you want to enter direct path.
    :return: dictionary with message about where the files were moved to or with some error message.
    """

    # downloading content of a zip archive
    content = requests.get(url).content

    # compiling the destination path
    if os.path.isdir(path):
        if not is_direct:
            if path[-3:] == 'Bin':
                path = path[:-4] + '/Mod/VP/PC_CustomData/Objects'
            else:
                return {'Path Error': 'Given path must end on "Bin"'}
    else:
        return {'Path Error': 'Given path is not a valid directory'}

    # creating temporary directory and unzipping archive
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/cont.zip', 'wb') as f:
            f.write(content)

            with ZipFile(f'{tmpdir}/cont.zip') as zip_obj:
                zip_obj.extractall(f'{tmpdir}')

        # checking if there are any files in it, checking character dir and moving it into FaceRig characters directory
        character_dir_info = next(os.walk(f'{tmpdir}/{item}'))

        if character_dir_info[1]:
            character_dir = character_dir_info[1][0]
        else:
            return {'Item Error': 'This item is unavailable, it has no files inside'}

        path_to_character_dir = f'{tmpdir}/{item}/{character_dir}'

        if character_dir not in next(os.walk(path))[1]:
            shutil.move(path_to_character_dir, path)
        else:
            return {'Item Error': 'Already have this item in collection, can\'t move duplicate character'}

    return {'Success': f'{character_dir} was moved to the {path}'}


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

    # create the data dicts that will be filled with parsed data and payload with given params
    items_data = {}
    additional_data = {}
    payload = {'appid': app, 'browsesort': sort, 'actualsort': sort, 'p': page, 'numperpage': amount}

    # if given some search string, pass it to request
    if search:
        payload['searchtext'] = search
        payload['childpublishedfileid'] = 0

    # if we sort not by trend we can't pass the amount of days to payload
    if sort == 'trend':
        payload['days'] = days

    # get html page and make a beautiful soup from it
    html = requests.get('https://steamcommunity.com/workshop/browse', params=payload)
    soup = BeautifulSoup(html.text, 'html.parser')

    # get links for item icons
    logo_tags = soup.find_all('img', 'workshopItemPreviewImage')
    logo_sources = [tag.get('src') for tag in logo_tags]
    items_data['img_sources'] = logo_sources

    # get links for item rating images
    rating_tags = soup.find_all('img', 'fileRating')
    rating_sources = [tag.get('src') for tag in rating_tags]
    items_data['rating_sources'] = rating_sources

    # get title of each item
    title_tags = soup.find_all('div', 'workshopItemTitle')
    title_texts = [tag.string for tag in title_tags]
    items_data['title_texts'] = title_texts

    # get author of each item
    author_tags = soup.find_all('div', 'workshopItemAuthorName')
    author_texts = ['by ' + str(tag.a.string) for tag in author_tags]
    items_data['author_texts'] = author_texts

    # get id of each item
    id_tags = soup.find_all('a', 'ugc')
    item_ids = [int(tag.get('data-publishedfileid')) for tag in id_tags]
    items_data['item_ids'] = item_ids

    # get last possible page with such payload
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

    # get amount of items on the page
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
