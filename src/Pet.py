import sys
import random
import math
import os
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap, QPainter, QColor, QTransform
from PyQt5.QtCore import Qt, QTimer

from InfoWindow import InfoWindow

class Pet(QLabel):
    def __init__(self, name):
        super().__init__()

        # image related variables
        self.name = name
        self.evolution_stage = 0
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.img_dir = os.path.join(base_dir, "../imgs")
        self.image_path = os.path.join(
            self.img_dir, f"{self.name}_{self.evolution_stage}.png"
        )

        # Pet state
        self.pos_x, self.pos_y = random.randint(500, 1500), random.randint(200, 400)
        self.direction = random.choice([1, -1])
        self.vx, self.vy = random.randint(0, 3)*self.direction, 0
        self.level = 5
        self.walk_cycle = 0
        self.manager = None

        # Flags / Utility
        self.drag_offset = None
        self.last_mouse_pos = None
        self.on_delay = False
        self.is_walking = False
        self.in_battle = False

        # Initial configuration
        self._load_image()
        self._setup_window()
        self._setup_timers()
        self._setup_screens()
        self._create_context_menu()

    # ========== Setup ==========

    def _load_image(self):
        self.original_pixmap = QPixmap(self.image_path)
        pixmap = self.original_pixmap
        
        if self.direction == 1:
            transform = QTransform()
            transform.scale(-1, 1)
            pixmap = pixmap.transformed(transform)
        
        self.setPixmap(pixmap)

    def _setup_window(self):
        self.setGeometry(self.pos_x, self.pos_y, 128, 128)
        # Unique window title for each pet
        self.setWindowTitle(f"Pet - {self.name.capitalize()}")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)

    def _setup_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._move_pet)
        self.timer.start(15)
        self.delay_timer = QTimer()
        self.delay_timer.timeout.connect(self._end_delay)

    def _setup_screens(self):
        self.screens = QApplication.instance().screens()
        area = self.screens[0].virtualGeometry()
        self.left, self.top = area.left(), area.top()
        self.right = area.right() - self.width()
        self.floor = area.bottom() - self.height() - 20

    def _create_context_menu(self):
        
        # Loads the qss file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(base_dir, "../stylesheets/menu.qss"), "r") as f:
                menu_style = f.read()
        except FileNotFoundError:
            menu_style = ""
    
        # Creates the menu and stores it as an attribute
        self.context_menu = QMenu(self)
        self.context_menu.setStyleSheet(menu_style)
    
        # Creates actions
        self.info_action = QAction("[   ⓘ   Info   ]", self)
        self.close_action = QAction("[   ✖   Close  ]", self)
    
        # Connects actions
        self.info_action.triggered.connect(self.show_info)
        self.close_action.triggered.connect(self.close_pet)
    
        # Adds them to the menu
        self.context_menu.addAction(self.info_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.close_action)

    # ========== Movement ==========

    def _move_pet(self):
        """
        Main movement loop.
        """

        if self.drag_offset:
            return

        if not self._fall_pet():
            self._walk_pet()

            if self.level >= 15 and self.evolution_stage == 0:
                self._evolve_pet()

            if self.level >= 36 and self.evolution_stage == 1:
                self._evolve_pet()

        self._cant_escape_bounds()
        self.move(self.pos_x, self.pos_y)

    def _fall_pet(self):
        """
        Simulates gravity.

        Returns:
            if the pet is falling (bool).
        """

        if self.is_walking:
            return False

        # If the pet is above the floor level, it will begin to fall.
        if self.pos_y < self.floor:

            # Its vertical speed will increase with each iteration, until it reaches terminal velocity.
            self.vy = min(self.vy + 1, 50)
            self.pos_y += self.vy

            # Its horizontal speed remains the same, to simulate inertia.
            self.vx = min(self.vx, 50)
            self.pos_x += self.vx

            return True

        else:
            self.is_walking = True
            return False

    def _walk_pet(self):
        """
        Makes the pet walk.
        """

        if not self.is_walking or self.on_delay or self.in_battle:
            return

        self.walk_cycle += 1
        self.vx = 2 * self.direction
        self.pos_x += self.vx

        # Smooth vertical motion (sinusoidal rocking)
        offset_y = 5 * math.sin(self.walk_cycle * 0.5)
        self.pos_y = math.floor(self.floor + offset_y)

        # Chance to change directions
        if random.random() < 0.005:
            self.direction *= -1
            self.vx *= -1
            self._flip_image()

        # Chance to pause (delay)
        elif random.random() < 0.002:
            self._start_delay()

        # Chance to jump
        elif random.random() < 0.001:
            self._jump_pet()

    def _jump_pet(self, min_height: int = -30, max_height: int = -15):
        """
        Makes the pet jump.

        Parameters
            min_height (int): minimum value.
            max_height (int): maximum value.
        """

        self.is_walking = False

        # Adds a random vertical speed to the pet.
        self.vy = random.randint(min_height, max_height)
        self.pos_y += self.vy

    def _cant_escape_bounds(self):
        """
        Prevents the pet from escaping the screen bounds.
        """

        # Floor is determined by the bottom bound of which screen the pet is in.
        bounds = [screen.geometry() for screen in self.screens]
        for bound in bounds:
            if self.pos_x >= bound.left() and self.pos_x <= bound.right():
                self.floor = bound.bottom() - self.height() - 20
                break

        # If beyond any of the limits, the pet is obstructed to go any further.
        self.pos_x = max(self.left, min(self.pos_x, self.right))
        self.pos_y = max(self.top, min(self.pos_y, self.floor))

    def _evolve_pet(self):
        """
        Evolves the pet.
        """

        iteration_counter = 0
        # The sprite is whiten to simulate evolution.
        self._color_image(r=255, g=255, b=255, alpha=200)

        def animate():
            nonlocal iteration_counter
            iteration_counter += 1

            # When the evolution is over
            if iteration_counter >= 300:
                # Changes the pet sprite.
                self.evolution_stage += 1
                self.image_path = os.path.join(
                    self.img_dir, f"{self.name}_{self.evolution_stage}.png"
                )
                self._load_image()

                # The original timer is run again.
                self.reset_timer(callback=self._move_pet, interval=15)

        # Starts a timer for the pet to evolve.
        self.reset_timer(callback=animate, interval=15)

    def lose_battle(self):
        """
        Does the animation when losing a battle.
        """

        self._jump_pet(min_height=-20, max_height=-10)
        self.vx = random.randint(10, 15) * -self.direction

    def win_battle(self):
        """
        Does the animation when winning a battle.
        """
        self._jump_pet(min_height=-10, max_height=-10)

    # ========== Visual effects ==========

    def _flip_image(self):
        """
        Flips the image on the horizontal axis.
        """
        transform = QTransform()
        transform.scale(-1, 1)
        flipped_pixmap = self.pixmap().transformed(transform)
        self.setPixmap(flipped_pixmap)

    def _color_image(self, r: int, g: int, b: int, alpha: int = 200):
        """
        Colors the image.

        Parameters:
            alpha (int): Transparency.
            r (int): Color red.
            g (int): Color green.
            b (int): Color blue.
        """
        pixmap = self.pixmap().copy()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(r, g, b, alpha))
        painter.end()
        self.setPixmap(pixmap)

    # ========== Mouse events ==========

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.pos()  # Click position within the pet.
            self.is_walking = False

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_offset:
            global_pos = self.mapToGlobal(event.pos())
            new_x = global_pos.x() - self.drag_offset.x()
            new_y = global_pos.y() - self.drag_offset.y()

            # Calculates the velocity using the difference between positions.
            if self.last_mouse_pos:
                dx = global_pos.x() - self.last_mouse_pos.x()
                dy = global_pos.y() - self.last_mouse_pos.y()

                self.vx = math.floor(dx)
                self.vy = math.floor(dy)

            self.last_mouse_pos = global_pos

            # Updates the pet position to the mouse position.
            self.pos_x = new_x
            self.pos_y = new_y
            self.move(self.pos_x, self.pos_y)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.last_mouse_pos = None

    
    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    # ========== Utility Functions ==========

    def reset_timer(self, callback, interval: int =15):
        """
        Resets the pet timer and connects a new callback.

        Parameters:
            callback: The new function that will be run every x seconds.
            interval (int): The interval (in milliseconds).
        """
        self.timer.stop()
        try:
            self.timer.timeout.disconnect()
        except TypeError:
            pass
    
        self.timer.timeout.connect(callback)
        self.timer.start(interval)

    def _start_delay(self):
        """
        Put the pet in pause mode.
        """

        self.on_delay = True
        delay_ms = random.randint(2000, 4000)  # between 2 and 4 seconds.
        self.delay_timer.start(delay_ms)

    def _end_delay(self):
        """
        Exit pause mode.
        """
        self.on_delay = False

    def show_info(self):
        """
        Shows the pet info.
        """
        self.info_window = InfoWindow(pet=self)
        self.info_window.show()

    def close_pet(self):
        """
        Close the pet window, destroy it and remove it from the manager's pet list.
        """
        self.manager.remove_pet(pet=self)
        self.close()      
        self.deleteLater()  