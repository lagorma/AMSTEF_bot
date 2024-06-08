import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import datetime
import matplotlib.image as mpimg
import app.database.requests as rq


async def create_mood_graph(tg_id):
    plt.figure()
    # Путь к изображениям (замените на свои изображения)
    image_paths = ['img/image6.png', 'img/image5.png', 'img/image4.png', 'img/image3.png', 'img/image2.png',
                   'img/image1.png']
    colors = ["grey", "purple", "lightblue", "green", "yellow", "gold"]

    # Создаем данные для графика
    values, dates = await rq.get_mood_answer_and_date(tg_id)
    print(values, dates)

    # Создаем график с разноцветными линиями
    if len(values) > 1:
        for i in range(len(dates) - 1):
            plt.plot(dates[i:i + 2], values[i:i + 2], color="lightgrey", linewidth=2.5)
            plt.fill_between(dates[i:i + 2], values[i:i + 2], 0, color='red', alpha=0.03)

    for i in range(len(dates)):
        plt.scatter(dates[i], values[i], color=colors[int(values[i]) - 1], s=200, zorder=2)
        plt.fill_between(dates[i], values[i], 0, color='red', alpha=0.03)

    for value in range(0, 7):
        plt.axhline(y=value + 0.5, color="grey", linestyle='--', linewidth=0.5)

    # Убираем метки по осям и сетку
    # plt.xticks([])
    plt.yticks([1, 2, 3, 4, 5, 6])
    plt.grid(False)

    # Отображаем только даты на оси x
    # if len(values) > 1:
    #     plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d.%m'))
    #     plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=1))

    plt.tick_params(axis='x', colors='grey')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)

    # Добавляем изображения рядом с графиком
    for i, img_path in enumerate(image_paths):
        img = mpimg.imread(img_path)
        imagebox = plt.axes([-0.01, 0.19 + i * 0.125, 0.1, 0.1])
        imagebox.imshow(img)
        imagebox.axis('off')

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(f'img/mood/{tg_id}mood.png', bbox_inches='tight', transparent=False)

    plt.close('all')
    allfignums = plt.get_fignums()
    print(f'fignums: {allfignums} (should be zero)')


async def create_stress_graph(tg_id):
    plt.figure()
    # Создаем данные для графика
    values, dates = await rq.get_stress_answer_and_date(tg_id)
    print(values, dates)
    plt.plot(dates, values)

    for i in range(len(dates)):
        plt.scatter(dates[i], values[i], color="lightblue", s=100, zorder=2)

    plt.yticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    plt.grid(False)

    plt.tick_params(axis='x', colors='grey')
    plt.tick_params(axis='y', colors='grey')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'img/stress/{tg_id}stress.png', bbox_inches='tight', transparent=False)
    
    plt.close('all')
    allfignums = plt.get_fignums()
    print(f'fignums: {allfignums} (should be zero)')
