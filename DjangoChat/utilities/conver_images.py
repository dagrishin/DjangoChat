import time

from PIL import Image, ImageDraw


def img_convert(image1):
    # print(image1)
    image = Image.open(image1)  # Открываем изображение
    draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
    width = image.size[0]  # Определяем ширину
    height = image.size[1]  # Определяем высоту
    pix = image.load()
    # print(draw, width, height, pix)
    for x in range(width):
        for y in range(height):
            r = pix[x, y][0]  # узнаём значение красного цвета пикселя
            g = pix[x, y][1]  # зелёного
            b = pix[x, y][2]  # синего
            sr = (r + g + b) // 3  # среднее значение
            draw.point((x, y), (sr, sr, sr))  # рисуем пиксель
    image = image.resize((150, 150), Image.ANTIALIAS)
    file_name = 'avatar' + str(time.time()).replace('.', '') + '.jpeg'
    image.save('media/images/'+ file_name, "JPEG")
    return '/images/' + file_name
