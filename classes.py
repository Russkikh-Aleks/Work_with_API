from datetime import datetime as dt
import json
import logging
import os.path
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from gui import *


def sort_photo(letter: str) -> int:
    sort_dict = {alpha: index for index, alpha in enumerate("smxopqryzw")}
    return sort_dict[letter]


class VKClient:
    """Класс для получения и загрузки информации с профиля в VK"""

    base_url = "https://api.vk.com/method"

    def __init__(self, token, id):
        self.token = token
        self.user_id = id
        self.common_params = {"access_token": self.token, "v": "5.131"}
        logger2.info("Экземпляр класса VKClient успешно создан")

    def get_albums(self) -> json:
        """Метод получает список альбомов для конкретного пользователя по атрибуту self.user_id"""

        params = self.common_params
        params.update({
            "owner_id": self.user_id,
            "need_system": 1
        })
        response = requests.get(
            f"{self.base_url}/photos.getAlbums?", params=params)
        print(response.status_code)
        try:
            response = response.json()

            return response
        except Exception as err:
            logger2.info(
                f"{type(err)} - {err}. Не удалось получить данные об альбомах.")
            return None

    def get_photo(self, albums_dict: dict) -> dict:
        """Метод получает список фото конкретного альбома, выбранного пользователем"""
        for a, b in albums_dict.items():
            album_id = a
            photo_count = b
        params = self.common_params
        params.update({
            "owner_id": self.user_id,
            "album_id": album_id,
            "extended": "1"
        })
        try:
            response = requests.get(
                f"{self.base_url}/photos.get?", params=params)
            response = response.json()
            data = response['response']['items']
            logger2.info(
                f"Успешно получена информация о {len(data)} фотографиях.")
        except:
            logger2.info(
                f"Ошибка получения информации с VK. Информация о фотографиях не получена.")
            return None

        length = min(len(data), photo_count)
        names, files_dict = set(), {}
        for el in data[:length]:
            if el['likes']['count'] in names:
                file_name = f"{el['likes']['count']} - {dt.strftime(dt.fromtimestamp(el['date']), '%Y-%m-%d %H-%M-%S')}"
            else:
                file_name = el['likes']['count']
            names.add(file_name)
            max_elem = max(
                el['sizes'], key=lambda size: sort_photo(size['type']))
            files_dict[f"{file_name}.jpg"] = {
                "f_url": max_elem['url'],
                "f_size": max_elem['type']
            }
        return files_dict


class YaUploader:
    """Класс для загрузки данных на Яндекс Диск"""

    base_url = "https://cloud-api.yandex.net/v1/disk"

    def get_dir_inform(self, folder_name: str) -> list:
        """ Метод получает информацию о файлах и папках, находящихся в переданной папке на яндекс диске"""

        params = {"path": f"disk:/{folder_name}",
                  "fields": 'items'}
        response = requests.get(f"{self.base_url}/resources",
                                headers=self.header, params=params).json()
        return [el['name'] for el in response["_embedded"]["items"]]

    def __init__(self, token: str):
        self.token = token
        self.header = {"Authorization": self.token}
        logger2.info("Экземпляр класса YaUploader успешно создан")

    def create_folder(self, folder_name: str) -> int:
        """Метод создает папку на Яндекс Диск, если ее еще там нет."""

        params = {"path": folder_name}
        response = requests.put(
            f"{self.base_url}/resources", headers=self.header, params=params)
        if response.status_code == 401:
            logger2.info(
                f"Ошибка авторизации на яндекс диске. Проверьте токен.")
            gui_interface_2.print_error(
                'Ошибка авторизации на яндекс диске. Проверьте токен.', 'Продолжить')
            return None
        elif response.status_code == 201:
            logger2.info(f"На Яндекс.диск успешно создана папка {folder_name}")
        elif response.status_code == 409:
            logger2.info(f"Папка {folder_name} уже существует на Яндекс.диск")
        else:
            logger2.info(
                f"Ошибка {response.status_code}. Папка {folder_name} не создана на яндекс диск.")
            gui_interface_2.print_error(
                'Не удалось создать папку на яндекс диске', 'Продолжить')
            return None
        return response.status_code

    def upload_ya_disk(self, folder_name: str, files_dict: dict) -> None:
        """Метод создает папку и сохраняет в нее файлы по списку file_dict на Яндекс Диск.
        Если файлы с такими именами уже находятся в папке, повторное копирование не производится, и об этом делается запись в файле 'logging.log'
        В конце в текущую директорию записывается файл 'ya_files_list.json', содержащий список успешно загруженных фото.

        """

        if not self.create_folder(folder_name):
            return None

        json_data = []
        existing_files = self.get_dir_inform(folder_name)
        for photo_name in files_dict.keys():
            if photo_name in existing_files:
                logger2.info(
                    f"Файл с названием {photo_name} уже существует в папке {folder_name} на яндекс.диск")
            else:
                params = {"path": f"{folder_name}/{photo_name}",
                          "url": files_dict[photo_name]["f_url"]}
                response = requests.post(
                    f"{self.base_url}/resources/upload", headers=self.header, params=params)

                if response.status_code == 202:
                    logger2.info(
                        f"Файл {photo_name} успешно сохранен на яндекс.диск")
                    json_data.append(
                        {"file_name": photo_name, "size": files_dict[photo_name]['f_size']})
                else:
                    logger2.info(
                        f"Ошибка {response.status_code}. Файл {photo_name} не скопирован на яндекс.диск")
        if json_data:
            try:
                with open("ya_files_list.json", "w", encoding="utf-8") as file:
                    json.dump(json_data, file)
            except Exception as err:
                logger2.info(f"{type(err)}: {err}")


class GoogleUploader:
    """Класс для загрузки данных на Google диск"""

    scopes = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, cred_file: str):
        self.creds = self.create_token(cred_file)
        if not self.creds:
            logger2.info(
                f"Ошибка авторизации на гугл диске. Проверьте файл - идентификатор клиента OAuth google drive.")
            gui_interface_2.print_error(
                'Ошибка авторизации на google drive. Проверьте файл - идентификатор клиента OAuth google drive.')
            return None
        self.service = build("drive", "v3", credentials=self.creds)

    def create_token(self, cred_file: str) -> Credentials:
        """Метод создает/актуализирует токен для работы с Google Диском.
           Необходимо, чтобы в директории с программой находился Идентификатор клиента OAuth google drive - файл с данными в формате json.
           Более подробная информация https://developers.google.com/drive/api/quickstart/python?hl=ru

           """
        try:
            creds = None
            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file(
                    "token.json", self.scopes)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        cred_file, self.scopes)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                # with open("token.json", "w") as token:
                #     token.write(creds.to_json())
            return creds
        except Exception as err:
            logger2.info(f"{type(err)}: {err}")
            return None

    def createRemoteFolder(self, folderName: str, parentID: str = None) -> str:
        """Метод создает папку на Google Диск"""

        body = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parentID:
            body['parents'] = [{'id': parentID}]
        try:
            response = self.service.files().create(body=body, fields='id').execute()
            logger2.info(f"На google drive успешно создана папка {folderName}")
            return response["id"]
        except:
            logger2.info(
                f"Ошибка создания папки {folderName} на google drive. Папка не создана")
            gui_interface_2.print_error(
                'Не удалось создать папку на google drive')
            return None

    def createRemoteFiles(self, folder_name: str, files_dict: dict) -> None:
        """Метод записывает файлы согласно полученного списка files_dict.
           Файлы сначала скачиваются в текущую директорию с программой, затем копируются на Google Диск.
           После сохранения на Google Диск файлы из текущей директории удаляются.
           В конце в текущую директорию записывается файл 'google_files_list.json', содержащий список успешно загруженных фото.

           """
        parent_id = self.createRemoteFolder(folder_name)
        if not parent_id:
            return None
        json_data = []
        for photo_name in files_dict.keys():
            try:
                response = requests.get(files_dict[photo_name]["f_url"])
                with open(photo_name, "wb") as file:
                    file.write(response.content)

                body = {
                    'name': photo_name,
                    'parents': [parent_id]
                }
                media = MediaFileUpload(photo_name, resumable=True)
                r = self.service.files().create(
                    body=body, media_body=media, fields='id').execute()
                if r["id"]:
                    json_data.append(
                        {"file_name": photo_name, "size": files_dict[photo_name]['f_size']})
                    logger2.info(
                        f"Файл {photo_name} успешно сохранен на google drive")
            except:
                logger2.info(
                    f"Ошибка записи файла {photo_name} на google drive.")

        if json_data:
            try:
                with open("google_files_list.json", "w", encoding="utf-8") as file:
                    json.dump(json_data, file)
            except Exception as err:
                logger2.info(f"{type(err)}: {err}")

    def delete_files(self, *args) -> None:
        """Метод удаляет фото из текущией директории после их загрузки на Google Диск"""

        for element in args:
            try:
                os.remove(element)
            except:
                pass


file_log_name = "logging"
logger2 = logging.getLogger(file_log_name)
logger2.setLevel(logging.INFO)
handler2 = logging.FileHandler(f"{file_log_name}.log", mode='w')
formatter2 = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
logger2.addHandler(handler2)
gui_interface_2 = Gui()
