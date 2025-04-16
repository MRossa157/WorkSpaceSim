#!/usr/bin/env python3
"""
Запуск WorkSpaceSim
Запустите этот скрипт для старта симуляции.
"""

import os
import random
import sys

# Добавляем директорию app в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Импортируем и запускаем приложение
if __name__ == "__main__":
    from app.constants import BASE_SIMULATION_SPEED, SPEED_MULTIPLIER_1
    from app.main import WorkSpaceSimApp

    # Вы можете указать конкретный сид как аргумент командной строки
    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except ValueError:
            print(f"Некорректное значение сида: {sys.argv[1]}")
            print("Используется случайный сид вместо указанного")
            seed = random.randint(1, 1000000)
    else:
        seed = random.randint(1, 1000000)

    print(f"Запуск WorkSpaceSim с сидом: {seed}")
    print(f"Базовая скорость симуляции: {BASE_SIMULATION_SPEED} минут за кадр")
    print(f"Начальный множитель скорости: ×{SPEED_MULTIPLIER_1}")
    print(f"Используйте клавиши 1, 2, 3 для изменения скорости симуляции")

    app = WorkSpaceSimApp(seed)
    app.run()
