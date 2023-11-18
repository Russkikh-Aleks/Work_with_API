from classes import *
from gui import Gui


def get_data_from_vk(vk_client: VKClient) -> dict:
    """Выбор альбома и количества фотографий для сохранения. Формирование данных для загрузки на облачные хранилища."""

    response = vk_client.get_albums()
    if response:
        albums_dict = {}
        gui_interface.choice_albums(response, albums_dict)
        if not albums_dict:
            logger2.info(
                "Введены некорректные данные по номеру альбома или количеству фото в VK")
        else:
            data_photos = vk_client.get_photo(albums_dict)
            if not data_photos:
                gui_interface.print_error(
                    'Не удалось получить информацио о фото.')
                return None
            else:
                return data_photos


def ya_uploud_photos(token: str, folder_name: str, data_photos: dict) -> None:
    """Загрузка фото на Яндекс Диск"""

    ya_uploader = YaUploader(token)
    ya_uploader.upload_ya_disk(folder_name, data_photos)


def gogle_upload_photos(cred_file: str, folder_name: str, data_photos: dict) -> None:
    """Загрузка фото на Google Диск"""

    gu_uploader = GoogleUploader(cred_file)
    if gu_uploader:
        gu_uploader.createRemoteFiles(folder_name, data_photos)
        gu_uploader.delete_files(*data_photos.keys())


if __name__ == '__main__':

    # Ввод данных для авторизации на Яндекс, Гугл, ВК
    gui_interface = Gui()
    data_input = [None, None, None, None]
    gui_interface.data_entry_window(data_input)
    folder_name = 'vk_photos'

    # Выбор альбома и количества фотографий для сохранения. Формирование данных для загрузки на облачные хранилища.
    vk_client = VKClient(data_input[0], data_input[1])
    data_photos = get_data_from_vk(vk_client)
    if data_photos:
        # Загрузка данных на Яндекс диск, Google Диск
        ya_uploud_photos(data_input[2], folder_name, data_photos)
        gogle_upload_photos(data_input[3], folder_name, data_photos)

gui_interface.print_error(
    "Для окончания работы программы нажмите 'Закончить'.\nИнформацию о ходе выполнения программы можно найти в файле 'logging.log'")
