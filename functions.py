import os
import requests
import tempfile
import shutil
from zipfile import ZipFile


def get_link(item: int, app=274920) -> str:
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
