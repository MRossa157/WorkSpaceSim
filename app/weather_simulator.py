import random
from datetime import datetime
from enum import Enum
from typing import Optional


class WeatherType(Enum):
    """Типы погоды в симуляции"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAIN = "rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"


class WeatherSimulator:
    """
    Класс для симуляции погоды в офисном приложении.

    Генерирует реалистичные погодные условия на основе времени года,
    текущего дня и предыдущих погодных условий.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Инициализация симулятора погоды

        Args:
            seed: Seed для генератора случайных чисел (опционально)
        """
        if seed is not None:
            random.seed(seed)

        self.current_weather = WeatherType.SUNNY
        self.update_interval = 60  # интервал обновления погоды в минутах
        self.last_update_time = 0

        # Вероятности для каждого типа погоды по сезонам
        self.season_probabilities: dict[str, dict[WeatherType, float]] = {
            'winter': {
                WeatherType.SUNNY: 0.2,
                WeatherType.CLOUDY: 0.4,
                WeatherType.RAIN: 0.1,
                WeatherType.THUNDERSTORM: 0.0,
                WeatherType.SNOW: 0.3
            },
            'spring': {
                WeatherType.SUNNY: 0.4,
                WeatherType.CLOUDY: 0.3,
                WeatherType.RAIN: 0.2,
                WeatherType.THUNDERSTORM: 0.1,
                WeatherType.SNOW: 0.0
            },
            'summer': {
                WeatherType.SUNNY: 0.6,
                WeatherType.CLOUDY: 0.2,
                WeatherType.RAIN: 0.1,
                WeatherType.THUNDERSTORM: 0.1,
                WeatherType.SNOW: 0.0
            },
            'autumn': {
                WeatherType.SUNNY: 0.3,
                WeatherType.CLOUDY: 0.4,
                WeatherType.RAIN: 0.2,
                WeatherType.THUNDERSTORM: 0.1,
                WeatherType.SNOW: 0.0
            }
        }

        # Инициализация первичной погоды
        self._update_weather()

    def update(self, current_time: int) -> None:
        """
        Обновляет погоду на основе прошедшего времени

        Args:
            current_time: Текущее время симуляции (в минутах)
        """
        if current_time - self.last_update_time >= self.update_interval:
            self._update_weather()
            self.last_update_time = current_time

    def _update_weather(self) -> None:
        """Обновляет текущую погоду на основе вероятностей"""
        current_season = self._get_current_season()
        probabilities = self.season_probabilities[current_season]

        # Генерация случайного числа
        r = random.random()

        # Определение новой погоды на основе вероятностей
        cumulative_prob = 0
        for weather_type, probability in probabilities.items():
            cumulative_prob += probability
            if r <= cumulative_prob:
                self.current_weather = weather_type
                break

    def _get_current_season(self) -> str:
        """Определяет текущий сезон на основе даты"""
        now = datetime.now()
        month = now.month

        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'autumn'
        else:
            return 'winter'

    def get_current_weather(self) -> str:
        """
        Возвращает текущее состояние погоды

        Returns:
            Строковое представление текущей погоды
        """
        return self.current_weather.value