import os
import json
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
import webbrowser  # Для открытия файла с помощью системы

DATA_FILE = "bookshelf_data.json"  # Имя файла для сохранения списка книг

class Book:
    def __init__(self, title, file_path):
        self.title = title
        self.file_path = file_path
        self.current_page = 0  # Текущая страница для отслеживания прогресса

    def to_dict(self):
        """Преобразуем объект книги в словарь для сохранения"""
        return {
            'title': self.title,
            'file_path': self.file_path,
            'current_page': self.current_page
        }

    @staticmethod
    def from_dict(data):
        """Создаем объект книги из словаря"""
        book = Book(data['title'], data['file_path'])
        book.current_page = data.get('current_page', 0)
        return book

class Bookshelf:
    def __init__(self):
        self.books = []  # Список книг
    
    def add_book(self, title, file_path):
        new_book = Book(title, file_path)
        self.books.append(new_book)
    
    def remove_book(self, title):
        self.books = [book for book in self.books if book.title != title]

    def get_books(self):
        return self.books

    def save_books(self):
        """Сохраняем список книг в JSON файл"""
        books_data = [book.to_dict() for book in self.books]
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, ensure_ascii=False, indent=4)
    
    def load_books(self):
        """Загружаем книги из JSON файла, если он существует"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                books_data = json.load(f)
                self.books = [Book.from_dict(book_data) for book_data in books_data]

class BookshelfApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shelf = Bookshelf()
    
    def build(self):
        # Загружаем книги из файла при запуске
        self.shelf.load_books()

        layout = BoxLayout(orientation='vertical', spacing=10)

        # Кнопки добавления и удаления книги
        buttons_layout = BoxLayout(size_hint_y=None, height=50)
        add_btn = Button(text="Добавить книгу", size_hint_x=None, width=150)
        add_btn.bind(on_press=self.show_file_chooser)
        remove_btn = Button(text="Удалить книгу", size_hint_x=None, width=150)
        remove_btn.bind(on_press=self.show_remove_dropdown)

        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(remove_btn)

        layout.add_widget(buttons_layout)

        # Полки для книг с возможностью скролла
        self.bookshelf_view = ScrollView(size_hint=(1, 1))
        self.update_bookshelf_view()

        layout.add_widget(self.bookshelf_view)

        return layout

    def on_stop(self):
        """Сохраняем книги при завершении работы приложения"""
        self.shelf.save_books()

    def update_bookshelf_view(self):
        # Визуальное обновление стеллажа
        grid_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        for book in self.shelf.get_books():
            book_button = Button(text=book.title, size_hint_y=None, height=150)
            book_button.bind(on_press=lambda instance, b=book: self.open_book(b))
            grid_layout.add_widget(book_button)
        
        self.bookshelf_view.clear_widgets()
        self.bookshelf_view.add_widget(grid_layout)
    
    def show_file_chooser(self, instance):
        # Открытие FileChooser для выбора книги из указанной папки
        filechooser = FileChooserListView(path=r'C:\Users\k119\Desktop', filters=['*.txt', '*.pdf'])  # Фильтруем текстовые и PDF файлы
        popup = Popup(title="Выберите файл", content=filechooser, size_hint=(0.9, 0.9))

        # Кнопка для подтверждения выбора файла
        select_btn = Button(text="Выбрать", size_hint_y=None, height=40)
        select_btn.bind(on_press=lambda x: self.add_selected_book(filechooser.selection, popup))

        # Добавляем кнопку в диалог
        filechooser.add_widget(select_btn)
        popup.open()

    def add_selected_book(self, selection, popup):
        if selection:
            file_path = selection[0]  # Получаем путь к выбранному файлу
            book_title = os.path.basename(file_path)  # Название книги — это имя файла
            self.shelf.add_book(book_title, file_path)
            self.update_bookshelf_view()
        popup.dismiss()

    def show_remove_dropdown(self, instance):
        # Создаем выпадающий список для удаления книги
        dropdown = DropDown()
        for book in self.shelf.get_books():
            btn = Button(text=book.title, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.remove_book_from_dropdown(btn.text, dropdown))
            dropdown.add_widget(btn)

        dropdown.open(instance)

    def remove_book_from_dropdown(self, book_title, dropdown):
        # Удаление выбранной книги
        self.shelf.remove_book(book_title)
        self.update_bookshelf_view()
        dropdown.dismiss()

    def open_book(self, book):
        # Открытие PDF или текстового файла с помощью системы
        if os.path.exists(book.file_path):
            webbrowser.open(f'file://{book.file_path}')
        else:
            print(f"Файл {book.file_path} не найден.")

if __name__ == "__main__":
    BookshelfApp().run()
