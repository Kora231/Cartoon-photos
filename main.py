import cv2
import numpy as np
import tempfile
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window

# Проверяем платформу для Android
if platform == "android":
    try:
        from jnius import autoclass
        from android.permissions import request_permissions, Permission
    except ImportError:
        autoclass = None
        request_permissions = None
        Permission = None


class FairyTaleApp(App):

    def build(self):
        # Создаем интерфейс приложения
        self.layout = BoxLayout(orientation='vertical')

        # Создаем изображение для отображения потока с камеры
        self.img1 = Image()
        self.layout.add_widget(self.img1)

        # Устанавливаем размеры окна
        # Window.size = (300, 600)

        # Создаем кнопку для захвата и обработки фото
        self.process_button = Button(text="Make Fairy Tale", size_hint=(0.4, 0.1), pos_hint={'x': 0.3, 'y': 0})
        self.process_button.bind(on_press=self.capture_and_process_photo)
        self.layout.add_widget(self.process_button)

        # Инициализируем переменные
        self.image_texture = None
        self.capture = cv2.VideoCapture(0)

        # Запрашиваем разрешение на запись во внешнее хранилище, если на Android
        if platform == "android" and request_permissions:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

        # Запускаем метод обновления изображения с камеры
        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

        return self.layout

    def update_camera(self, dt):
        # Обновляем изображение с камеры
        ret, frame = self.capture.read()
        if ret:
            # Конвертируем кадр в текстуру и отображаем на экране
            self.image_texture = self.frame_to_texture(frame)
            self.img1.texture = self.image_texture

    def capture_and_process_photo(self, instance):
        # Захватываем и обрабатываем фото
        ret, frame = self.capture.read()
        if ret:
            # Создаем временные метки для имен файлов
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_filename = f"processed_photo_{timestamp}.jpg"

            # Обрабатываем фото
            frame = self.make_fairy_tale(frame)
            self.image_texture = self.frame_to_texture(frame)
            self.img1.texture = self.image_texture
            self.img1.canvas.ask_update()
            cv2.imwrite(processed_filename, frame)
            print("Photo processed and updated as", processed_filename)

            # Сохраняем фото в галерее
            self.save_to_gallery(processed_filename)

    def frame_to_texture(self, frame):
        # Конвертируем кадр в текстуру
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def make_fairy_tale(self, frame):
        # Применяем эффект сказки к фото
        print("Applying fairy tale effect...")

        # Применяем размытие Гаусса
        blurred_frame = cv2.GaussianBlur(frame, (7, 7), 0)

        # Конвертируем изображение в оттенки серого
        gray_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2GRAY)

        # Применяем стилизацию к фото
        cartoonized_frame = cv2.stylization(frame, sigma_s=150, sigma_r=0.25)

        print("Fairy tale effect applied")
        return cartoonized_frame

    def save_to_gallery(self, filename):
        # Сохраняем фото в галерее
        temp_directory = tempfile.gettempdir()
        file_path = f"{temp_directory}/{filename}"

        # Код ниже работает только для Android
        if platform == "android" and autoclass:
            MediaStore = autoclass('android.provider.MediaStore')
            Images = autoclass('android.provider.MediaStore$Images')
            ContentValues = autoclass('android.content.ContentValues')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            content_values = ContentValues()
            content_values.put(Images.Media.DISPLAY_NAME, filename)
            content_values.put(Images.Media.MIME_TYPE, "image/jpeg")
            content_values.put(Images.Media.RELATIVE_PATH, "Pictures/")

            resolver = PythonActivity.mActivity.getContentResolver()
            uri = resolver.insert(Images.Media.EXTERNAL_CONTENT_URI, content_values)

            with open(file_path, 'rb') as file:
                output_stream = resolver.openOutputStream(uri)
                output_stream.write(file.read())
                output_stream.close()

            print("Photo saved to gallery")


if __name__ == '__main__':
    FairyTaleApp().run()
