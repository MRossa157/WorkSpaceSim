"""
Константы для проекта WorkSpaceSim.
"""

import pygame
from models import RoomType

# Инициализация pygame
pygame.init()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 200)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (240, 240, 240)
LIGHT_BLUE = (200, 220, 255)

# Цвета комнат
ROOM_COLORS = {
    RoomType.OFFICE: (220, 240, 220),      # Светло-зеленый
    RoomType.MEETING_ROOM: (220, 220, 255),  # Светло-синий
    RoomType.KITCHEN: (255, 255, 220),      # Светло-желтый
    RoomType.RESTROOM: (240, 220, 240),     # Светло-фиолетовый
    RoomType.CORRIDOR: (230, 230, 230),     # Светло-серый
    RoomType.RECEPTION: (255, 220, 220),    # Светло-красный
}

# Размеры экрана
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Скорость симуляции
BASE_SIMULATION_SPEED = 1  # Базовая скорость симуляции (минут за кадр)
SPEED_MULTIPLIER_1 = 1  # Множитель для клавиши 1
SPEED_MULTIPLIER_2 = 10  # Множитель для клавиши 2
SPEED_MULTIPLIER_3 = 100  # Множитель для клавиши 3

# Константы для меток скорости
SPEED_SLOW_LABEL = "Медленно"
SPEED_NORMAL_LABEL = "Нормально"
SPEED_FAST_LABEL = "Быстро"

# Параметры зума и позиции
DEFAULT_ZOOM = 1.0
MIN_ZOOM = 0.5
MAX_ZOOM = 2.0
ZOOM_STEP = 1.1
DEFAULT_OFFSET_X = 0
DEFAULT_OFFSET_Y = 0
SCROLL_SPEED = 10

# Интерфейс
INFO_PANEL_WIDTH = 300
WORKER_CIRCLE_RADIUS = 6
SELECTED_WORKER_CIRCLE_RADIUS = 8
PROGRESS_BAR_WIDTH = 20
TASK_PANEL_WIDTH = 300
TASK_PANEL_HEIGHT = 400
MAX_TASKS_DISPLAYED = 15

# Параметры симуляции
DEFAULT_WORKER_COUNT = 8
FPS = 30

# Рабочее расписание (в минутах от начала дня)
WORKDAY_START_HOUR = 8
WORKDAY_START_MINUTE = 0
WORKDAY_START_TIME = WORKDAY_START_HOUR * 60 + WORKDAY_START_MINUTE  # 8:00 в минутах

WORKDAY_END_HOUR = 18
WORKDAY_END_MINUTE = 0
WORKDAY_END_TIME = WORKDAY_END_HOUR * 60 + WORKDAY_END_MINUTE  # 18:00 в минутах

MAX_OVERTIME_MINUTES = 120  # Максимальное время переработки (2 часа)
OVERTIME_PROBABILITY = 0.3  # Вероятность того, что работник останется на переработку

# Перемещение работников
MIN_TASK_MOVEMENT_DISTANCE = 50  # Минимальное расстояние для перемещения при выполнении задачи
WORKER_ARRIVAL_VARIATION = 15  # Разброс времени прихода работников (в минутах)