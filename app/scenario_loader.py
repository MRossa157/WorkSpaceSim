import json
import logging
import os
from typing import Any, Dict, List, Optional


class ScenarioLoader:
    """
    Класс для загрузки сценариев из отдельных JSON-файлов.

    Позволяет загружать все сценарии из указанной директории,
    получать сценарии по ID или типу, а также сохранять новые сценарии.
    """

    def __init__(self, scenarios_dir: str = "data/scenarios"):
        """
        Инициализация загрузчика сценариев

        Args:
            scenarios_dir: Путь к директории со сценариями
        """
        self.scenarios_dir = scenarios_dir
        self.scenarios: dict[str, dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def load_all_scenarios(self) -> dict[str, dict[str, Any]]:
        """
        Загружает все сценарии из директории.

        Returns:
            Словарь сценариев, где ключ - ID сценария
        """
        self.scenarios = {}

        if not os.path.exists(self.scenarios_dir):
            self.logger.warning(f"Директория со сценариями не найдена: {self.scenarios_dir}")
            return {}

        # Проходим по всем поддиректориям и ищем JSON-файлы
        for dirpath, _, filenames in os.walk(self.scenarios_dir):
            for filename in filenames:
                if not filename.endswith('.json'):
                    continue

                file_path = os.path.join(dirpath, filename)
                scenario_id = os.path.splitext(filename)[0]

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        scenario_data = json.load(f)

                    # Проверяем, совпадает ли ID в файле с именем файла
                    if 'id' in scenario_data and scenario_data['id'] != scenario_id:
                        self.logger.warning(
                            f"Несоответствие ID в файле {file_path}: "
                            f"ID в файле {scenario_data['id']}, имя файла {scenario_id}"
                        )

                    # Если ID нет в данных, добавляем его
                    if 'id' not in scenario_data:
                        scenario_data['id'] = scenario_id

                    # Определяем тип сценария по директории, если он не указан
                    if 'type' not in scenario_data:
                        # Получаем имя поддиректории
                        subdir = os.path.relpath(dirpath, self.scenarios_dir).split(os.path.sep)[0]
                        if subdir and subdir != '.':
                            scenario_data['type'] = subdir
                        else:
                            scenario_data['type'] = 'general'

                    self.scenarios[scenario_data['id']] = scenario_data
                    self.logger.debug(f"Загружен сценарий: {scenario_data['id']}")

                except Exception as e:
                    self.logger.error(f"Ошибка при загрузке сценария {file_path}: {str(e)}")

        self.logger.info(f"Всего загружено сценариев: {len(self.scenarios)}")
        return self.scenarios

    def get_scenario(self, scenario_id: str) -> Optional[dict[str, Any]]:
        """
        Получает сценарий по его ID

        Args:
            scenario_id: ID сценария

        Returns:
            Данные сценария или None, если сценарий не найден
        """
        return self.scenarios.get(scenario_id)

    def get_scenarios_by_type(self, scenario_type: str) -> list[dict[str, Any]]:
        """
        Получает список сценариев определенного типа

        Args:
            scenario_type: Тип сценария

        Returns:
            Список сценариев указанного типа
        """
        return [
            scenario for scenario in self.scenarios.values()
            if scenario.get('type') == scenario_type
        ]

    def save_scenario(self, scenario_data: dict[str, Any]) -> bool:
        """
        Сохраняет сценарий в файл

        Args:
            scenario_data: Данные сценария

        Returns:
            True если сохранение успешно, иначе False
        """
        if 'id' not in scenario_data:
            self.logger.error("Не указан ID сценария для сохранения")
            return False

        scenario_id = scenario_data['id']
        scenario_type = scenario_data.get('type', 'general')

        # Формируем путь для сохранения
        type_dir = os.path.join(self.scenarios_dir, scenario_type)
        if not os.path.exists(type_dir):
            try:
                os.makedirs(type_dir, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Не удалось создать директорию {type_dir}: {str(e)}")
                return False

        file_path = os.path.join(type_dir, f"{scenario_id}.json")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scenario_data, f, ensure_ascii=False, indent=2)

            # Обновляем кэш сценариев
            self.scenarios[scenario_id] = scenario_data
            self.logger.info(f"Сценарий {scenario_id} сохранен в {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при сохранении сценария {scenario_id}: {str(e)}")
            return False