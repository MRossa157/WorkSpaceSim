import random
import sys

import constants as const
import pygame
from models import (
    Department,
    OfficeSimulation,
)

# Инициализация pygame
pygame.init()


class WorkSpaceSimApp:
    """Главный класс приложения WorkSpaceSim."""

    def __init__(self, seed=None):
        """Инициализация приложения."""
        self.screen = pygame.display.set_mode((
            const.SCREEN_WIDTH,
            const.SCREEN_HEIGHT,
        ))
        pygame.display.set_caption('WorkSpaceSim')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 12)
        self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 16)

        # Состояние симуляции
        self.seed = seed or random.randint(1, 1000000)
        self.simulation = OfficeSimulation(self.seed)
        self.simulation.initialize(worker_count=const.DEFAULT_WORKER_COUNT)

        # Состояние интерфейса
        self.paused = False
        self.speed_multiplier = (
            const.BASE_SIMULATION_SPEED * const.SPEED_MULTIPLIER_1
        )  # Начальная скорость
        self.current_speed_level = (
            const.SPEED_MULTIPLIER_1
        )  # Текущий уровень скорости (1, 2 или 3)
        self.selected_worker = None
        self.scroll_speed = const.SCROLL_SPEED

        # Информационная панель
        self.show_info_panel = True
        self.info_panel_width = const.INFO_PANEL_WIDTH

        # Ввод сида
        self.seed_input_active = False
        self.seed_input_text = str(self.seed)

        # Панель списка задач
        self.show_task_panel = False

        # Панель офиса
        self.office_display_surface = pygame.Surface((
            const.SCREEN_WIDTH - self.info_panel_width,
            const.SCREEN_HEIGHT,
        ))
        self.zoom = const.DEFAULT_ZOOM
        self.offset_x = const.DEFAULT_OFFSET_X
        self.offset_y = const.DEFAULT_OFFSET_Y

    def handle_events(self):
        """Обработка событий pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # События клавиатуры
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_1:
                    self.current_speed_level = const.SPEED_MULTIPLIER_1
                    self.speed_multiplier = (
                        const.BASE_SIMULATION_SPEED * const.SPEED_MULTIPLIER_1
                    )
                elif event.key == pygame.K_2:
                    self.current_speed_level = const.SPEED_MULTIPLIER_2
                    self.speed_multiplier = (
                        const.BASE_SIMULATION_SPEED * const.SPEED_MULTIPLIER_2
                    )
                elif event.key == pygame.K_3:
                    self.current_speed_level = const.SPEED_MULTIPLIER_3
                    self.speed_multiplier = (
                        const.BASE_SIMULATION_SPEED * const.SPEED_MULTIPLIER_3
                    )
                elif event.key == pygame.K_i:
                    self.show_info_panel = not self.show_info_panel
                elif event.key == pygame.K_t:
                    self.show_task_panel = not self.show_task_panel
                elif event.key == pygame.K_r:
                    # Сброс симуляции с текущим сидом
                    self.simulation = OfficeSimulation(self.seed)
                    self.simulation.initialize(
                        worker_count=const.DEFAULT_WORKER_COUNT
                    )
                    self.selected_worker = None

                # Обработка ввода сида
                elif self.seed_input_active:
                    self._handle_seed_input(event)

            # События мыши
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    self._handle_click(event.pos)
                elif event.button == 4:  # Прокрутка вверх
                    self.zoom *= const.ZOOM_STEP
                    self.zoom = min(const.MAX_ZOOM, self.zoom)
                elif event.button == 5:  # Прокрутка вниз
                    self.zoom /= const.ZOOM_STEP
                    self.zoom = max(const.MIN_ZOOM, self.zoom)

            # Перетаскивание мышью для панорамирования
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Удерживается левая кнопка
                    dx, dy = event.rel
                    self.offset_x += dx
                    self.offset_y += dy

        # Непрерывный ввод с клавиатуры для панорамирования
        self._handle_continuous_input()

        return True

    def _handle_seed_input(self, event):
        """Обработка ввода значения сида."""
        if event.key == pygame.K_RETURN:
            self.seed_input_active = False
            try:
                new_seed = int(self.seed_input_text)
                self.seed = new_seed
                self.simulation = OfficeSimulation(self.seed)
                self.simulation.initialize(
                    worker_count=const.DEFAULT_WORKER_COUNT
                )
                self.selected_worker = None
            except ValueError:
                self.seed_input_text = str(self.seed)
        elif event.key == pygame.K_BACKSPACE:
            self.seed_input_text = self.seed_input_text[:-1]
        else:
            if event.unicode.isdigit():
                self.seed_input_text += event.unicode

    def _handle_continuous_input(self):
        """Обработка непрерывного ввода (клавиши)."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.offset_x += self.scroll_speed
        if keys[pygame.K_RIGHT]:
            self.offset_x -= self.scroll_speed
        if keys[pygame.K_UP]:
            self.offset_y += self.scroll_speed
        if keys[pygame.K_DOWN]:
            self.offset_y -= self.scroll_speed

    def _handle_click(self, pos):
        """Обработка событий клика мыши."""
        x, y = pos

        # Проверяем, находится ли клик в панели офиса
        panel_width = self.info_panel_width if self.show_info_panel else 0
        if x < const.SCREEN_WIDTH - panel_width:
            # Проверяем, кликнули ли на работника
            for worker in self.simulation.workers.values():
                worker_screen_x = worker.x * self.zoom + self.offset_x
                worker_screen_y = worker.y * self.zoom + self.offset_y

                # Проверяем, находится ли клик внутри значка работника
                radius = 10 * self.zoom
                if (
                    (worker_screen_x - x) ** 2 + (worker_screen_y - y) ** 2
                ) <= radius**2:
                    self.selected_worker = worker
                    return

            # Если ни на одного работника не кликнули, снимаем выделение
            self.selected_worker = None

        # Проверяем, находится ли клик на поле ввода сида в информационной панели
        if self.show_info_panel:
            seed_box_rect = pygame.Rect(
                const.SCREEN_WIDTH - self.info_panel_width + 10,
                140,
                self.info_panel_width - 20,
                30,
            )
            if seed_box_rect.collidepoint(pos):
                self.seed_input_active = not self.seed_input_active

    def update(self):
        """Обновление состояния симуляции."""
        if not self.paused:
            self.simulation.update(int(self.speed_multiplier))

            # Обработка неудачных заданий
            for worker_id, worker in self.simulation.workers.items():
                for task in worker.failed_tasks:
                    if task.fail_event:
                        self.simulation.handle_failed_task(task)
                worker.failed_tasks = []

            # Начинаем день, если сейчас утро
            if (
                self.simulation.time
                == const.WORKDAY_START_HOUR * 60 + const.WORKDAY_START_MINUTE
            ):
                self.simulation.start_day()

    def draw(self):
        """Отрисовка текущего состояния на экране."""
        self.screen.fill(const.WHITE)

        # Рисуем офис
        self._draw_office()

        # Рисуем информационную панель
        if self.show_info_panel:
            self._draw_info_panel()

        # Рисуем панель задач
        if self.show_task_panel:
            self._draw_task_panel()

        pygame.display.flip()

    def _draw_office(self):
        """Отрисовка планировки офиса и работников."""
        self.office_display_surface.fill(const.WHITE)

        # Рисуем комнаты
        for room in self.simulation.rooms:
            color = const.ROOM_COLORS.get(room.room_type, const.GRAY)
            x = room.x * self.zoom + self.offset_x
            y = room.y * self.zoom + self.offset_y
            width = room.width * self.zoom
            height = room.height * self.zoom

            pygame.draw.rect(
                self.office_display_surface, color, (x, y, width, height)
            )
            pygame.draw.rect(
                self.office_display_surface,
                const.BLACK,
                (x, y, width, height),
                2,
            )

            # Рисуем название комнаты
            room_label = self.font.render(
                room.room_type.value, True, const.BLACK
            )
            self.office_display_surface.blit(room_label, (x + 5, y + 5))

            # Рисуем события в комнате
            for i, event in enumerate(room.events):
                event_text = f'Событие: {event}'
                event_label = self.font.render(event_text, True, const.RED)
                self.office_display_surface.blit(
                    event_label, (x + 5, y + 25 + i * 15)
                )

        # Рисуем работников
        self._draw_workers()

        # Отображаем поверхность офиса на основном экране
        self.screen.blit(self.office_display_surface, (0, 0))

    def _draw_workers(self):
        """Отрисовка работников."""
        for worker_id, worker in self.simulation.workers.items():
            x = worker.x * self.zoom + self.offset_x
            y = worker.y * self.zoom + self.offset_y

            # Определяем цвет работника в зависимости от отдела
            if worker.department == Department.ENGINEERING:
                color = const.BLUE
            elif worker.department == Department.MARKETING:
                color = const.GREEN
            elif worker.department == Department.MANAGEMENT:
                color = const.PURPLE
            elif worker.department == Department.HR:
                color = const.YELLOW
            else:
                color = const.ORANGE

            # Больший круг для выбранного работника
            radius = (
                const.SELECTED_WORKER_CIRCLE_RADIUS
                if worker == self.selected_worker
                else const.WORKER_CIRCLE_RADIUS
            )
            radius *= self.zoom

            pygame.draw.circle(
                self.office_display_surface, color, (int(x), int(y)), int(radius)
            )
            pygame.draw.circle(
                self.office_display_surface,
                const.BLACK,
                (int(x), int(y)),
                int(radius),
                1,
            )

            # Рисуем индикатор прогресса задания, если у работника есть задание
            if worker.current_task:
                progress = (
                    worker.current_task.progress / worker.current_task.duration
                )
                indicator_width = const.PROGRESS_BAR_WIDTH * self.zoom
                pygame.draw.rect(
                    self.office_display_surface,
                    const.BLACK,
                    (x - indicator_width / 2, y - 15, indicator_width, 5),
                )
                pygame.draw.rect(
                    self.office_display_surface,
                    const.GREEN,
                    (
                        x - indicator_width / 2,
                        y - 15,
                        indicator_width * progress,
                        5,
                    ),
                )

    def _draw_info_panel(self):
        """Отрисовка информационной панели."""
        panel_x = const.SCREEN_WIDTH - self.info_panel_width
        panel_rect = pygame.Rect(
            panel_x, 0, self.info_panel_width, const.SCREEN_HEIGHT
        )

        # Рисуем фон панели
        pygame.draw.rect(self.screen, const.LIGHT_GRAY, panel_rect)
        pygame.draw.line(
            self.screen,
            const.BLACK,
            (panel_x, 0),
            (panel_x, const.SCREEN_HEIGHT),
            2,
        )

        # Рисуем заголовок
        title = self.title_font.render('WorkSpaceSim', True, const.BLACK)
        self.screen.blit(title, (panel_x + 10, 10))

        # Рисуем время симуляции
        time_text = self.simulation.get_current_time_str()
        time_label = self.info_font.render(time_text, True, const.BLACK)
        self.screen.blit(time_label, (panel_x + 10, 80))

        # Рисуем ввод сида
        seed_label = self.info_font.render('Сид:', True, const.BLACK)
        self.screen.blit(seed_label, (panel_x + 10, 110))

        seed_box_color = (
            const.LIGHT_BLUE if self.seed_input_active else const.WHITE
        )
        pygame.draw.rect(
            self.screen,
            seed_box_color,
            (panel_x + 10, 140, self.info_panel_width - 20, 30),
        )
        seed_value = self.info_font.render(
            self.seed_input_text, True, const.BLACK
        )
        self.screen.blit(seed_value, (panel_x + 15, 145))

        # Рисуем информацию о скорости
        if self.current_speed_level == const.SPEED_MULTIPLIER_1:
            speed_label = const.SPEED_SLOW_LABEL
        elif self.current_speed_level == const.SPEED_MULTIPLIER_2:
            speed_label = const.SPEED_NORMAL_LABEL
        else:
            speed_label = const.SPEED_FAST_LABEL

        speed_text = f'Скорость: {speed_label} (×{self.current_speed_level})'
        if self.paused:
            speed_text += ' (Пауза)'
        speed_info = self.info_font.render(speed_text, True, const.BLACK)
        self.screen.blit(speed_info, (panel_x + 10, 180))

        # Рисуем справку по управлению
        controls = [
            'Управление:',
            'Пробел - Пауза/Запуск',
            '1,2,3 - Скорость (×1,×2,×3)',
            'R - Сброс симуляции',
            'I - Показать/скрыть панель',
            'T - Показать/скрыть задачи',
            'Стрелки - Перемещение вида',
            'Колесо мыши - Масштаб',
            'Клик - Выбрать работника',
        ]

        for i, control in enumerate(controls):
            control_label = self.font.render(control, True, const.BLACK)
            self.screen.blit(control_label, (panel_x + 10, 220 + i * 20))

        # Отображаем информацию о выбранном работнике
        if self.selected_worker:
            self._draw_worker_info(panel_x)

    def _draw_worker_info(self, panel_x):
        """Отрисовка информации о выбранном работнике."""
        worker_y = 450
        pygame.draw.line(
            self.screen,
            const.BLACK,
            (panel_x + 5, worker_y - 10),
            (panel_x + self.info_panel_width - 5, worker_y - 10),
            1,
        )

        worker_title = self.info_font.render(
            f'Работник: {self.selected_worker.name}', True, const.BLACK
        )
        self.screen.blit(worker_title, (panel_x + 10, worker_y))

        worker_info = [
            f'Отдел: {self.selected_worker.department.value}',
            f'Должность: {self.selected_worker.position.value}',
            f'Личность: {self.selected_worker.personality.value}',
            f'Настроение: {self.selected_worker.mood:.2f}',
            f'Выполнено заданий: {len(self.selected_worker.completed_tasks)}',
            f'Провалено заданий: {len(self.selected_worker.failed_tasks)}',
        ]

        for i, info in enumerate(worker_info):
            info_label = self.font.render(info, True, const.BLACK)
            self.screen.blit(info_label, (panel_x + 10, worker_y + 30 + i * 20))

        # Рисуем текущее задание, если есть
        if self.selected_worker.current_task:
            self._draw_task_info(panel_x, worker_y + 180)

    def _draw_task_info(self, panel_x, task_y):
        """Отрисовка информации о текущем задании работника."""
        task_title = self.info_font.render('Текущее задание:', True, const.BLACK)
        self.screen.blit(task_title, (panel_x + 10, task_y))

        task = self.selected_worker.current_task
        task_info = [
            f'Название: {task.name}',
            f'Описание: {task.description}',
            f'Прогресс: {task.progress}/{task.duration} мин',
            f'Шанс успеха: {task.get_adjusted_success_rate():.2f}',
        ]

        for i, info in enumerate(task_info):
            info_label = self.font.render(info, True, const.BLACK)
            self.screen.blit(info_label, (panel_x + 10, task_y + 30 + i * 20))

    def _draw_task_panel(self):
        """Отрисовка панели задач, показывающей все доступные задания."""
        panel_width = const.TASK_PANEL_WIDTH
        panel_height = const.TASK_PANEL_HEIGHT
        panel_x = (const.SCREEN_WIDTH - panel_width) // 2
        panel_y = (const.SCREEN_HEIGHT - panel_height) // 2

        # Рисуем фон панели
        pygame.draw.rect(
            self.screen,
            const.LIGHT_GRAY,
            (panel_x, panel_y, panel_width, panel_height),
        )
        pygame.draw.rect(
            self.screen,
            const.BLACK,
            (panel_x, panel_y, panel_width, panel_height),
            2,
        )

        # Рисуем заголовок
        title = self.title_font.render('Доступные задания', True, const.BLACK)
        self.screen.blit(title, (panel_x + 10, panel_y + 10))

        # Рисуем список заданий
        for i, task in enumerate(
            self.simulation.available_tasks[: const.MAX_TASKS_DISPLAYED]
        ):
            y_pos = panel_y + 40 + i * 20
            task_text = f'{task.name} - {task.duration}мин'
            task_label = self.font.render(task_text, True, const.BLACK)
            self.screen.blit(task_label, (panel_x + 10, y_pos))

        # Рисуем инструкции по закрытию
        close_text = 'Нажмите T для закрытия'
        close_label = self.font.render(close_text, True, const.BLACK)
        self.screen.blit(
            close_label,
            (panel_x + panel_width - 150, panel_y + panel_height - 20),
        )

    def run(self):
        """Основной игровой цикл."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(const.FPS)

        pygame.quit()
        sys.exit()


# Основная точка входа
if __name__ == '__main__':
    # Случайный сид по умолчанию
    seed = random.randint(1, 1000000)
    app = WorkSpaceSimApp(seed)
    app.run()
