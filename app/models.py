import json
import logging
import math
import os
import random
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from scenario_loader import ScenarioLoader
from weather_simulator import WeatherSimulator


# Перечисления для свойств работников
class Department(Enum):
    ENGINEERING = 'Engineering'
    MARKETING = 'Marketing'
    MANAGEMENT = 'Management'
    HR = 'Human Resources'
    SUPPORT = 'Support'


class Position(Enum):
    INTERN = 'Intern'
    JUNIOR = 'Junior'
    SENIOR = 'Senior'
    LEAD = 'Lead'
    MANAGER = 'Manager'
    DIRECTOR = 'Director'
    SECURITY = 'Security Guard'


class TaskStatus(Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'


class Personality(Enum):
    DILIGENT = 'Diligent'  # Более высокий уровень успеха
    LAZY = 'Lazy'  # Более низкий уровень успеха
    SOCIAL = 'Social'  # Предпочитает задачи с другими
    INTROVERT = 'Introvert'  # Предпочитает одиночные задачи
    CHAOTIC = 'Chaotic'  # Непредсказуемое поведение


class RoomType(Enum):
    OFFICE = 'Office'
    MEETING_ROOM = 'Meeting Room'
    KITCHEN = 'Kitchen'
    RESTROOM = 'Restroom'
    CORRIDOR = 'Corridor'
    RECEPTION = 'Reception'


# Класс Task, представляющий рабочее задание
class Task:
    def __init__(
        self,
        name: str,
        description: str,
        duration: int,
        success_rate: float,
        required_position: Optional[Position] = None,
        fail_event: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.duration = duration  # в минутах
        self.success_rate = success_rate  # базовый коэффициент успеха 0.0-1.0
        self.status = TaskStatus.PENDING
        self.required_position = required_position
        self.fail_event = fail_event
        self.assigned_to = None
        self.progress = 0

    def can_be_assigned_to(self, worker) -> bool:
        if self.required_position is None:
            return True
        return worker.position == self.required_position

    def update(self, elapsed_time: int) -> None:
        """Обновить прогресс задания на основе прошедшего времени"""
        if self.status == TaskStatus.IN_PROGRESS:
            self.progress += elapsed_time
            if self.progress >= self.duration:
                # Задание завершено, определяем успех или неудачу
                if random.random() < self.get_adjusted_success_rate():
                    self.status = TaskStatus.COMPLETED
                else:
                    self.status = TaskStatus.FAILED

    def get_adjusted_success_rate(self) -> float:
        """Рассчитать скорректированный показатель успеха на основе черт работника"""
        if not self.assigned_to:
            return self.success_rate

        base_rate = self.success_rate

        # Корректировка на основе личности
        if self.assigned_to.personality == Personality.DILIGENT:
            base_rate += 0.1
        elif self.assigned_to.personality == Personality.LAZY:
            base_rate -= 0.1

        # Ограничение в допустимом диапазоне
        return max(0.1, min(0.95, base_rate))


# Класс Worker, представляющий сотрудника
class Worker:
    def __init__(self, name: str, department: Department, position: Position):
        self.id = str(uuid.uuid4())
        self.name = name
        self.department = department
        self.position = position
        self.personality = random.choice(list(Personality))
        self.mood = random.uniform(0.5, 1.0)  # 0.0-1.0
        self.current_task = None
        self.completed_tasks: list[Task] = []
        self.failed_tasks: list[Task] = []
        self.x = 0  # позиция в офисе
        self.y = 0
        self.target_x = 0  # цель движения
        self.target_y = 0
        self.speed = random.uniform(1.5, 3.0)  # скорость передвижения
        self.current_room = None
        self.is_at_office = True  # флаг присутствия в офисе
        self.productivity = 0  # показатель продуктивности за день

    def assign_task(self, task: Task) -> bool:
        """Назначить задание этому работнику, если возможно"""
        if self.current_task is not None or not self.is_at_office:
            return False

        if not task.can_be_assigned_to(self):
            return False

        self.current_task = task
        task.assigned_to = self
        task.status = TaskStatus.IN_PROGRESS
        return True

    def update(self, elapsed_time: int) -> None:
        """Обновить состояние работника на основе прошедшего времени"""
        # Если работник не в офисе, прекращаем обновление
        if not self.is_at_office:
            return

        # Обновить текущее задание, если есть
        if self.current_task:
            self.current_task.update(elapsed_time)
            if self.current_task.status == TaskStatus.COMPLETED:
                self.completed_tasks.append(self.current_task)
                self.mood = min(1.0, self.mood + 0.1)
                self.productivity += 1
                self.current_task = None
            elif self.current_task.status == TaskStatus.FAILED:
                self.failed_tasks.append(self.current_task)
                self.mood = max(0.0, self.mood - 0.1)
                self.current_task = None

        # Движение к целевой точке
        self._move(elapsed_time)

    def _move(self, elapsed_time: int) -> None:
        """Перемещение работника к целевой позиции"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 1:  # Достаточно близко к цели
            self.x = self.target_x
            self.y = self.target_y
            return

        # Нормализуем направление и применяем скорость
        move_distance = min(
            distance, self.speed * elapsed_time / 60
        )  # конвертируем в секунды
        self.x += (dx / distance) * move_distance
        self.y += (dy / distance) * move_distance

    def leave_office(self) -> None:
        """Работник покидает офис в конце рабочего дня"""
        self.is_at_office = False
        if self.current_room:
            self.current_room.remove_occupant(self)

        # Сохраняем статистику дня и сбрасываем счетчики
        self.productivity = 0

        # Незавершенные задания возвращаются назначившей стороне
        if self.current_task:
            self.current_task.status = TaskStatus.PENDING
            self.current_task.progress = 0
            self.current_task.assigned_to = None
            self.current_task = None

        # Перемещаем работника за пределы офиса
        self.x = -100
        self.y = -100
        self.target_x = -100
        self.target_y = -100

    def enter_office(self, room: 'Room') -> None:
        """Работник приходит в офис в начале рабочего дня"""
        self.is_at_office = True
        x, y = room.get_random_position()
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        room.add_occupant(self)

        # Настроение в начале дня зависит от личности
        if self.personality == Personality.DILIGENT:
            self.mood = min(
                1.0, self.mood + 0.1
            )  # Трудолюбивый работник приходит с хорошим настроением
        elif self.personality == Personality.LAZY:
            self.mood = max(
                0.3, self.mood - 0.1
            )  # Ленивый не рад новому рабочему дню

    def set_target(self, x: int, y: int) -> None:
        """Установить цель движения"""
        self.target_x = x
        self.target_y = y


# Класс Room для офисных помещений
class Room:
    def __init__(
        self, room_type: RoomType, x: int, y: int, width: int, height: int
    ):
        self.id = str(uuid.uuid4())
        self.room_type = room_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.occupants: list[Worker] = []
        self.events: list[
            str
        ] = []  # Текущие события в комнате (например, "разлив воды")

    def contains_point(self, x: int, y: int) -> bool:
        """Проверить, содержит ли комната точку"""
        return (
            self.x <= x < self.x + self.width
            and self.y <= y < self.y + self.height
        )

    def add_occupant(self, worker: Worker) -> None:
        """Добавить работника в эту комнату"""
        if worker not in self.occupants:
            self.occupants.append(worker)
            worker.current_room = self

    def remove_occupant(self, worker: Worker) -> None:
        """Удалить работника из этой комнаты"""
        if worker in self.occupants:
            self.occupants.remove(worker)
            if worker.current_room == self:
                worker.current_room = None

    def get_random_position(self) -> Tuple[int, int]:
        """Получить случайную позицию внутри комнаты"""
        return (
            random.randint(self.x + 1, self.x + self.width - 1),
            random.randint(self.y + 1, self.y + self.height - 1),
        )


# Генератор офисной планировки
class OfficeGenerator:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.seed = seed or random.randint(1, 1000000)
        self.width = 800
        self.height = 600
        self.rooms: list[Room] = []
        self.corridors: list[Room] = []

    def generate(self) -> list[Room]:
        """Сгенерировать процедурную планировку офиса с заданным сидом"""
        # Сбросить состояние
        random.seed(self.seed)
        self.rooms = []
        self.corridors = []

        # Сначала создаем главный коридор
        main_corridor = self._create_corridor()
        self.corridors.append(main_corridor)
        self.rooms.append(main_corridor)

        # Добавляем различные комнаты
        self._add_rooms()

        return self.rooms

    def _create_corridor(self) -> Room:
        """Создать главный коридор с нетривиальной формой"""
        # Создаем Г-образный коридор
        corridor_width = 20

        # Начальная позиция и размеры
        start_x = self.width // 4
        start_y = self.height // 3
        horiz_length = self.width // 2
        vert_length = self.height // 2

        # Создаем Г-образный коридор как два перекрывающихся прямоугольника
        corridor_h = Room(
            RoomType.CORRIDOR, start_x, start_y, horiz_length, corridor_width
        )
        corridor_v = Room(
            RoomType.CORRIDOR, start_x, start_y, corridor_width, vert_length
        )

        # Объединяем их в один коридор неправильной формы
        corridor = Room(
            RoomType.CORRIDOR,
            min(corridor_h.x, corridor_v.x),
            min(corridor_h.y, corridor_v.y),
            max(corridor_h.x + corridor_h.width, corridor_v.x + corridor_v.width)
            - min(corridor_h.x, corridor_v.x),
            max(
                corridor_h.y + corridor_h.height,
                corridor_v.y + corridor_v.height,
            )
            - min(corridor_h.y, corridor_v.y),
        )

        return corridor

    def _add_rooms(self) -> None:
        """Добавить различные комнаты вокруг коридора"""
        corridor = self.corridors[0]

        # Добавляем офисы вдоль коридора
        room_count = random.randint(4, 8)
        room_types = [RoomType.OFFICE] * (room_count - 3) + [
            RoomType.MEETING_ROOM,
            RoomType.KITCHEN,
            RoomType.RESTROOM,
        ]
        random.shuffle(room_types)

        # Добавляем комнаты вдоль горизонтальной части коридора
        corridor_y = corridor.y
        x_start = corridor.x + corridor.width // 4
        for i in range(3):
            room_width = random.randint(60, 100)
            room_height = random.randint(60, 80)
            room = Room(
                room_types[i],
                x_start,
                corridor_y - room_height - 5,
                room_width,
                room_height,
            )
            self.rooms.append(room)
            x_start += room_width + random.randint(10, 30)

        # Добавляем комнаты вдоль вертикальной части коридора
        corridor_x = corridor.x
        y_start = corridor.y + corridor.height // 3
        for i in range(3, 6):
            if i < len(room_types):
                room_width = random.randint(60, 100)
                room_height = random.randint(60, 80)
                room = Room(
                    room_types[i],
                    corridor_x + corridor.width // 4,
                    y_start,
                    room_width,
                    room_height,
                )
                self.rooms.append(room)
                y_start += room_height + random.randint(10, 30)

        # Добавляем ресепшн у входа
        reception = Room(
            RoomType.RECEPTION, corridor.x - 80, corridor.y - 5, 80, 60
        )
        self.rooms.append(reception)


# Класс симуляции для управления офисом
class OfficeSimulation:
    """Симуляция офиса"""

    def __init__(self, config: Any):
        # Обработка конфигурации - поддержка как словаря, так и прямого значения seed
        if isinstance(config, dict):
            self.seed = config.get('seed')
        else:
            self.seed = config  # Если передано прямое значение (int)

        self.generator = OfficeGenerator(self.seed)
        self.rooms: list[Room] = []
        self.workers: dict[str, Worker] = {}
        self.tasks: dict[str, Task] = {}
        self.available_tasks: list[Task] = []
        self.time = 8 * 60  # 8:00 утра в минутах
        self.day = 1
        self.weather = WeatherSimulator(self.seed)
        self.scenario_loader = ScenarioLoader()
        self.scenarios: dict[str, dict[str, Any]] = (
            self.scenario_loader.load_all_scenarios()
        )
        self.logger = logging.getLogger(__name__)

    def initialize(self, worker_count=10):
        """Инициализировать симуляцию с процедурным офисом и работниками"""
        # Генерируем планировку офиса
        self.rooms = self.generator.generate()

        # Создаем работников
        departments = list(Department)
        positions = [
            pos for pos in list(Position) if pos != Position.SECURITY
        ]  # Обычные должности

        for i in range(worker_count):
            name = f'Worker-{i + 1}'
            department = random.choice(departments)
            position = random.choice(positions)
            worker = Worker(name, department, position)

            # Размещаем работника в подходящей комнате
            suitable_rooms = [
                r for r in self.rooms if r.room_type == RoomType.OFFICE
            ]
            if suitable_rooms:
                room = random.choice(suitable_rooms)
                x, y = room.get_random_position()
                worker.x = x
                worker.y = y
                worker.target_x = x
                worker.target_y = y
                room.add_occupant(worker)

            self.workers[worker.id] = worker

        # Добавляем одного охранника
        security = Worker('Security', Department.SUPPORT, Position.SECURITY)
        reception = next(
            (r for r in self.rooms if r.room_type == RoomType.RECEPTION), None
        )
        if reception:
            x, y = reception.get_random_position()
            security.x = x
            security.y = y
            security.target_x = x
            security.target_y = y
            reception.add_occupant(security)
        self.workers[security.id] = security

        # Создаем начальный пул заданий
        self._generate_tasks(20)

    def _generate_tasks(self, count: int) -> None:
        """Сгенерировать набор заданий"""
        task_templates = [
            # Общие задания
            {
                'name': 'Review documents',
                'description': 'Review important project documents',
                'duration': 60,
                'success_rate': 0.8,
            },
            {
                'name': 'Team meeting',
                'description': 'Attend team sync meeting',
                'duration': 45,
                'success_rate': 0.9,
            },
            {
                'name': 'Send emails',
                'description': 'Send important emails to clients',
                'duration': 30,
                'success_rate': 0.85,
            },
            {
                'name': 'Phone call',
                'description': 'Make an important phone call',
                'duration': 15,
                'success_rate': 0.75,
            },
            {
                'name': 'Coffee break',
                'description': 'Take a coffee break',
                'duration': 15,
                'success_rate': 0.95,
            },
            # Задания с возможными сбоями
            {
                'name': 'Fill water glass',
                'description': 'Fill glass from water cooler',
                'duration': 5,
                'success_rate': 0.7,
                'fail_event': 'Water spill',
            },
            {
                'name': 'Carry documents',
                'description': 'Carry stack of documents to another room',
                'duration': 10,
                'success_rate': 0.6,
                'fail_event': 'Dropped papers',
            },
            {
                'name': 'Bring coffee',
                'description': 'Bring coffee to colleague',
                'duration': 8,
                'success_rate': 0.65,
                'fail_event': 'Coffee spill',
            },
            # Задания для конкретных отделов
            {
                'name': 'Code review',
                'description': 'Review code for the project',
                'duration': 60,
                'success_rate': 0.7,
                'required_position': Position.SENIOR,
            },
            {
                'name': 'Interview candidate',
                'description': 'Interview job candidate',
                'duration': 90,
                'success_rate': 0.8,
                'required_position': Position.MANAGER,
            },
        ]

        for _ in range(count):
            template = random.choice(task_templates)
            task = Task(**template)
            self.tasks[task.id] = task
            self.available_tasks.append(task)

    def _load_scenarios(self):
        """Загрузка сценариев из JSON-файла"""
        try:
            # Используем новый загрузчик сценариев вместо чтения одного файла
            if not self.scenarios:
                self.scenarios = self.scenario_loader.load_all_scenarios()

            self.logger.info(f'Загружено {len(self.scenarios)} сценариев')
        except Exception as e:
            self.logger.error(f'Не удалось загрузить сценарии: {str(e)}')
            self.scenarios = {}

    def check_scenario_conditions(self, scenario_id: str) -> bool:
        """Проверяет, выполняются ли условия для активации сценария"""
        scenario = self.scenario_loader.get_scenario(scenario_id)
        if not scenario:
            return False

        # Проверка условий активации сценария
        if 'requirements' not in scenario:
            return True  # Нет условий - сценарий всегда активируется

        requirements = scenario['requirements']

        # Проверка времени
        current_time = datetime.now().time()
        if 'time_start' in requirements and 'time_end' in requirements:
            time_start = datetime.strptime(
                requirements['time_start'], '%H:%M'
            ).time()
            time_end = datetime.strptime(
                requirements['time_end'], '%H:%M'
            ).time()

            if not (time_start <= current_time <= time_end):
                return False

        # Проверка дня недели
        if 'weekdays' in requirements:
            current_weekday = datetime.now().weekday()
            if current_weekday not in requirements['weekdays']:
                return False

        # Проверка погоды
        if 'weather' in requirements:
            current_weather = self.weather.get_current_weather()
            if current_weather not in requirements['weather']:
                return False

        # Проверка средней продуктивности
        if (
            'min_productivity' in requirements
            or 'max_productivity' in requirements
        ):
            avg_productivity = self._get_average_productivity()

            if (
                'min_productivity' in requirements
                and avg_productivity < requirements['min_productivity']
            ):
                return False

            if (
                'max_productivity' in requirements
                and avg_productivity > requirements['max_productivity']
            ):
                return False

        return True

    def _get_average_productivity(self) -> float:
        """Получает среднюю продуктивность всех сотрудников в офисе"""
        workers_in_office = [
            w
            for w in self.workers.values()
            if hasattr(w, 'is_at_office') and w.is_at_office
        ]
        if not workers_in_office:
            return 0.0

        return sum(w.productivity for w in workers_in_office) / len(
            workers_in_office
        )

    def check_random_scenarios(self):
        """Проверяет и активирует случайные сценарии"""
        random_scenarios = self.scenario_loader.get_scenarios_by_type('random')

        for scenario in random_scenarios:
            scenario_id = scenario['id']

            # Проверяем, выполняются ли условия для активации сценария
            if not self.check_scenario_conditions(scenario_id):
                continue

            # Вычисляем вероятность активации
            probability = scenario.get('probability', 0.1)

            if random.random() <= probability:
                self.activate_scenario(scenario_id)

    def activate_scenario(self, scenario_id: str):
        """Активирует сценарий по его ID"""
        scenario = self.scenario_loader.get_scenario(scenario_id)
        if not scenario:
            self.logger.warning(
                f'Попытка активировать несуществующий сценарий: {scenario_id}'
            )
            return

        self.logger.info(f'Активирован сценарий: {scenario["name"]}')

        # Создаем задачи из сценария
        if 'tasks' in scenario:
            for task_data in scenario['tasks']:
                self._create_task_from_scenario(task_data, scenario_id)

    def _create_task_from_scenario(
        self, task_data: dict[str, Any], scenario_id: str
    ):
        """Создает задачу из данных сценария"""
        task_id = task_data.get(
            'id', f'{scenario_id}_{random.randint(1000, 9999)}'
        )

        # Если есть ссылка на шаблон задачи, используем его
        if 'reference_task' in task_data:
            reference_id = task_data['reference_task']
            reference_task = self._get_task_template(reference_id)
            if reference_task:
                # Объединяем данные шаблона и текущей задачи
                task_data = {**reference_task, **task_data}

        # Создаем задачу
        task = Task(
            name=task_data.get('name', f'Задача {task_id}'),
            description=task_data.get('description', ''),
            duration=task_data.get('duration', 30),
            success_rate=task_data.get('success_rate', 0.8),
            required_position=task_data.get('required_position'),
            fail_event=task_data.get('fail_event'),
        )

        # Добавляем задачу в офис
        self.tasks[task_id] = task

        # Если указаны исполнители, назначаем задачу
        if 'assignees' in task_data:
            for worker_id in task_data['assignees']:
                if worker_id in self.workers:
                    self.workers[worker_id].assign_task(task)
        else:
            # Если исполнители не указаны, выбираем случайных работников
            assignee_count = task_data.get('random_assignees', 1)
            workers_in_office = [
                w
                for w in self.workers.values()
                if hasattr(w, 'is_at_office') and w.is_at_office
            ]

            if workers_in_office:
                selected_workers = random.sample(
                    workers_in_office,
                    min(assignee_count, len(workers_in_office)),
                )

                for worker in selected_workers:
                    worker.assign_task(task)

    def _get_task_template(self, template_id: str) -> Optional[dict[str, Any]]:
        """Получает шаблон задачи по ID"""
        templates_dir = 'data/tasks'
        template_path = os.path.join(templates_dir, f'{template_id}.json')

        if not os.path.exists(template_path):
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def update(self, dt: float):
        """Обновление состояния симуляции"""
        # Обновляем время
        self.time += dt

        # Проверка на смену дня (после 18:00)
        if self.time >= 18 * 60:
            self.time = 8 * 60  # Сброс на 8:00 утра
            self.day += 1
            # Отправляем работников домой и генерируем новые задания
            self._end_day()
            self._generate_tasks(random.randint(5, 15))

        # Обновляем всех работников
        for worker in self.workers.values():
            worker.update(dt)

            # Пытаемся назначить задания свободным работникам (кроме охраны)
            if (
                worker.current_task is None
                and worker.position != Position.SECURITY
            ):
                self._try_assign_task(worker)

        # Проверяем изменения комнат
        for worker in self.workers.values():
            current_room = None
            for room in self.rooms:
                if room.contains_point(worker.x, worker.y):
                    current_room = room
                    break

            if current_room != worker.current_room:
                if worker.current_room:
                    worker.current_room.remove_occupant(worker)
                if current_room:
                    current_room.add_occupant(worker)

        # Проверка случайных сценариев
        if random.random() < 0.05:  # 5% шанс каждый тик
            self.check_random_scenarios()

    def _try_assign_task(self, worker: Worker) -> None:
        """Попытаться назначить доступное задание работнику"""
        suitable_tasks = [
            t for t in self.available_tasks if t.can_be_assigned_to(worker)
        ]
        if suitable_tasks:
            task = random.choice(suitable_tasks)
            if worker.assign_task(task):
                self.available_tasks.remove(task)

                # Находим подходящее место назначения для задания
                if task.name == 'Coffee break' or task.name.startswith(
                    'Fill water'
                ):
                    destinations = [
                        r for r in self.rooms if r.room_type == RoomType.KITCHEN
                    ]
                elif (
                    task.name == 'Team meeting'
                    or task.name == 'Interview candidate'
                ):
                    destinations = [
                        r
                        for r in self.rooms
                        if r.room_type == RoomType.MEETING_ROOM
                    ]
                else:
                    destinations = [
                        r for r in self.rooms if r.room_type == RoomType.OFFICE
                    ]

                if destinations:
                    destination = random.choice(destinations)
                    x, y = destination.get_random_position()
                    worker.set_target(x, y)

    def _end_day(self) -> None:
        """Завершить рабочий день - сбросить позиции работников, кроме охраны"""
        for worker in self.workers.values():
            if worker.position != Position.SECURITY:
                # Используем метод leave_office для работников
                worker.leave_office()

                # Возвращаем незавершенные задания в пул
                if worker.current_task:
                    self.available_tasks.append(worker.current_task)
            else:
                # Охранники патрулируют ночью
                corridor = next(
                    (r for r in self.rooms if r.room_type == RoomType.CORRIDOR),
                    None,
                )
                if corridor:
                    x, y = corridor.get_random_position()
                    worker.set_target(x, y)

    def start_day(self) -> None:
        """Начать новый рабочий день - вернуть всех работников в офис"""
        offices = [r for r in self.rooms if r.room_type == RoomType.OFFICE]
        if not offices:
            return

        for worker in self.workers.values():
            if worker.position != Position.SECURITY and not worker.is_at_office:
                # Используем метод enter_office для работников
                office = random.choice(offices)
                worker.enter_office(office)

    def get_current_time_str(self) -> str:
        """Получить текущее время в виде строки"""
        hours = self.time // 60
        minutes = self.time % 60
        return f'День {self.day} - {hours:02d}:{minutes:02d}'

    def handle_failed_task(self, task: Task) -> None:
        """Обработать события от неудачных заданий"""
        if not task.fail_event:
            return

        worker = task.assigned_to
        if not worker or not worker.current_room:
            return

        # Добавляем событие в комнату
        worker.current_room.events.append(task.fail_event)

        # Создаем задание на уборку, если применимо
        if task.fail_event == 'Water spill':
            cleanup = Task(
                'Clean spill', 'Clean up water spill', 15, 0.9, fail_event=None
            )
            self.tasks[cleanup.id] = cleanup
            self.available_tasks.append(cleanup)
        elif task.fail_event == 'Dropped papers':
            cleanup = Task(
                'Collect papers',
                'Collect dropped papers',
                10,
                0.95,
                fail_event=None,
            )
            self.tasks[cleanup.id] = cleanup
            self.available_tasks.append(cleanup)
        elif task.fail_event == 'Coffee spill':
            cleanup = Task(
                'Clean coffee',
                'Clean up coffee spill',
                20,
                0.85,
                fail_event=None,
            )
            self.tasks[cleanup.id] = cleanup
            self.available_tasks.append(cleanup)
