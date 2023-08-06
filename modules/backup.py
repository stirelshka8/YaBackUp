import os
import zipfile
import requests
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.cfg")


# Функция для создания резервной копии директорий
def create_backup(directories_loc):
    # Папка для сохранения резервных копий
    backup_dir = '/tmp'

    # Создание имени архива
    backup_files = f'backup_{((str(datetime.timestamp(datetime.now()))).split("."))[0]}.zip'

    # Создание архива
    with zipfile.ZipFile(backup_dir + '/' + backup_files, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for directory in directories_loc:
            # Рекурсивное добавление файлов и папок в архив
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(directory))
                    zipf.write(file_path, arcname)

    return backup_dir + '/' + backup_files


# Функция для загрузки файла на Яндекс.Диск
def upload_to_yandex_disk(file_path):
    try:
        url = (f'https://cloud-api.yandex.net/v1/disk/resources/upload?path=/{config["RUNS"]["YA_DIR"]}/'
               f'{os.path.basename(file_path)}')
        headers = {
            'Authorization': f'OAuth {config["TOKEN"]["YA"]}'
        }
        with open(file_path, 'rb') as file:
            response = requests.get(url, headers=headers)
            upload_url = response.json()['href']
            requests.put(upload_url, data=file)

        print('Backup uploaded to Yandex.Disk')
    except Exception as ex:
        print(f'ERROR uploaded to Yandex.Disk {ex}')
    finally:
        os.remove(file_path)


def start():
    directories = ("".join((config["RUNS"]["BACK_DIR"]).split(","))).split()
    backup_file = create_backup(directories)
    upload_to_yandex_disk(backup_file)
