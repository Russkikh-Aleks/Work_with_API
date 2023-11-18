from tkinter import *
from tkinter import ttk


class Gui:
    """Класс для реализации графического интерфейса взаимодействия с пользователем"""

    def close_window(self, root) -> None:
        root.destroy()

    def data_entry_window(self, input_data: list) -> None:
        """ Окно ввода данных для авторизации на VK, Яндекс Диск, Google Диск. Предусмотрено два способа ввода:
            1) Внесение данных в соответствующих полях в окне. 
               Если используете сочетание клавиш 'Ctrl+V' должна быть включена английская раскладка.
            2) Необходимые данные можно внести в файл 'congig.txt'. Данные вводятся без кавычек. 
               После сохранения файла 'congig.txt' с данными необходимо нажать на кнопку "Данные в файл 'config.txt' заполнены".
               Данные, необходимые для работы программы:
               - токен от VK
               - ID пользователя VK
               - токен от Яндекс Диска
               - название файла идентификатора клиента OAuth google drive в формате json
                 (подробнее https://developers.google.com/drive/api/quickstart/python?hl=ru)


               """

        def end_window() -> None:
            """Внесение данных через соответствующие поля ввода в окне."""

            for i in range(4):
                input_data[i] = entry_data[i].get()
            self.close_window(root)

        def get_data_config() -> None:
            """Внесение данных через файл 'config.txt'."""

            with open("config.txt", encoding="utf-8") as file:
                lines = (line.split('=')[1].strip() for line in file.readlines()
                         if line.strip != '' and line.index('=') != -1)
                i = 0
                for line in lines:
                    input_data[i] = line
                    i += 1
                    if i == 4:
                        break
            self.close_window(root)

        root = Tk()
        root.title("Введите данные")
        root.geometry("1250x400")

        fields = ["Введите токен от VK",
                  "Введите ID пользователя VK",
                  "Введите токен от Яндекс.диска",
                  "Введите название файла - идентификатора клиента OAuth google drive",
                  ]
        entry_data = [None, None, None, None]

        for i, field in enumerate(fields):
            label = ttk.Label(text=field, justify=LEFT)
            label.pack()
            entry_data[i] = ttk.Entry()
            entry_data[i].pack(anchor=NW, padx=6, pady=6)
            entry_data[i].config(width=200)

        btn = ttk.Button(text="Подтвердить", command=end_window)
        btn.pack(anchor=NW, padx=6, pady=6)

        label = ttk.Label(
            text="Альтернативный способ ввода: заполните данные в файле 'config.txt'.\nФайл должен находиться в одной директории с программой", justify=LEFT)
        label.pack()
        btn = ttk.Button(
            text="Данные в файл 'config.txt' заполнены.", command=get_data_config)
        btn.pack(anchor=NW, padx=6, pady=6)

        root.mainloop()

    def print_error(self, text_error: str, buttom_text: str = "Закончить"):
        """Метод для вывода инфомационных сообщений.
         Выводится текст из параметра text_error.

         """

        def end_window():
            self.close_window(root)

        root = Tk()
        root.title("Информационное окно")
        root.geometry("1000x200")

        label = ttk.Label(text=text_error, justify=LEFT)
        label.pack()

        btn = ttk.Button(text=buttom_text, command=end_window)
        btn.pack(anchor=NW, padx=6, pady=6)
        root.mainloop()

    def choice_albums(self, albums_list: dict, albums_dict: dict) -> None:
        """Метод для выбора альбома и количества фото для сохранения. У пользователя есть возможность выбрать конкретный альбом.
           Для этого надо ввести ID альбома в соответствующее поле из списка всех альбомов. После этого ввести количество фото.
           Если введены некорректные данные программа выдаст соответствующее сообщение.
           Если введенное количество фото больше, чем количество фото в альбоме, будут скопированы все фото в альбоме.
           Можно выбрать данные по умолчанию путем нажатия кнопки 'Использовать параметры по умолчанию. Альбом - фото профиля, количество фото - 5 шт.'
           Сохранение данных происходит путем добавления информации в объект albums_dict класса dict.
        """

        def set_default() -> None:
            """Устанавливаются значения по уполчаниюю. Альбом - фото профиля, количество фото - 5 шт."""

            albums_dict[-6] = 5
            self.close_window(root)

        def set_album() -> None:
            """Устанавливаются значения согласно введенным данным от пользователя"""

            try:
                count = int(entry_count.get().strip())
                value = int(entry_id.get())
                if value not in (el["id"] for el in albums_list['response']['items']):
                    print(2)
                    self.close_window(root)
                    self.print_error(
                        "Введен некорректный номер альбома")
                else:
                    albums_dict[entry_id.get()] = count
                    self.close_window(root)
            except:
                self.close_window(root)
                self.print_error(
                    "Введенные количество фото не является числом")

        try:
            albums_count = albums_list['response']['count']
        except:
            self.print_error(
                'Не получены данные о фото. Проверьте ID пользователя.')
            return None

        root = Tk()
        root.title(
            f"Найдено {albums_count} альбома(ов). Введите ID албома количество фото, или нажмите 'Использовать параметры по умолчанию'")
        root.geometry("500x1500")

        btn = ttk.Button(
            text="Использовать параметры по умолчанию. Альбом - фото профиля, количество фото - 5 шт.", command=set_default)
        btn.pack(anchor=NW, padx=6, pady=6)

        label = ttk.Label(
            text=f"Введите ID албома", justify=LEFT)
        label.pack(anchor=NW)
        entry_id = ttk.Entry()
        entry_id.pack(anchor=NW, padx=6, pady=6)

        label = ttk.Label(
            text=f"Введите количество фото для сохранения (не больше, чем количество фото в албоме)", justify=LEFT)
        label.pack(anchor=NW)
        entry_count = ttk.Entry()
        entry_count.pack(anchor=NW, padx=6, pady=6)

        btn = ttk.Button(
            text="Подтвердить", command=set_album)
        btn.pack(anchor=NW, padx=6, pady=6)

        scrollbar = Scrollbar(root)
        scrollbar.pack(side=RIGHT, fill=Y)

        listbox = Listbox(root, yscrollcommand=scrollbar.set)
        listbox.config(width=100)
        for i in range(albums_count):
            album = albums_list['response']['items'][i]
            listbox.insert(
                END, f"ID: {album['id']} - {album['title']} - {album['size']} фото")
        listbox.pack(side=LEFT, fill=BOTH)

        scrollbar.config(command=listbox.yview)

        root.mainloop()
