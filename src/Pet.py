import sys
import random
import math
import os
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QColor, QTransform
from PyQt5.QtCore import Qt, QTimer


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
        self.x, self.y = random.randint(500, 1500), random.randint(200, 400)
        self.vx, self.vy = -2, 0
        self.direction = -1
        self.walk_cycle = 0
        self.drag_offset = None
        self.last_mouse_pos = None
        self.is_paused = False
        self.is_walking = False
        self.level = 5

        # Initial configuration
        self._load_image()
        self._setup_window()
        self._setup_timers()
        self._setup_screens()

    # ========== Setup ==========

    def _load_image(self):
        self.original_pixmap = QPixmap(self.image_path)
        self.setPixmap(self.original_pixmap)

    def _setup_window(self):
        self.setGeometry(self.x, self.y, 128, 128)
        self.setWindowTitle(f"Pet Window")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
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
        self.move(self.x, self.y)

    def _fall_pet(self):
        """
        Simulates gravity.

        Returns:
            if the pet is falling (bool).
        """

        if self.is_walking:
            return False

        # If the pet is above the floor level, it will begin to fall.
        if self.y < self.floor:

            # Its vertical speed will increase with each iteration, until it reaches terminal velocity.
            self.vy = min(self.vy + 1, 50)
            self.y += self.vy

            # Its horizontal speed remains the same, to simulate inertia.
            self.vx = min(self.vx, 50)
            self.x += self.vx

            return True

        else:
            self.vy = 0
            self.vx = 2 * self.direction
            self.is_walking = True
            self.on_delay = False
            return False

    def _walk_pet(self):
        """
        Makes the pet walk.
        """

        if self.on_delay:
            return

        self.walk_cycle += 1
        self.x += self.vx

        # Smooth vertical motion (sinusoidal rocking)
        offset_y = 5 * math.sin(self.walk_cycle * 0.5)
        self.y = math.floor(self.floor + offset_y)

        # Chance to change directions
        if random.random() < 0.005:
            self.direction *= -1
            self.vx *= -1
            self._flip_image()

        # Chance to pause (delay)
        elif random.random() < 0.005:
            self._start_delay()

        # Chance to jump
        elif random.random() < 0.001:
            self._jump_pet()

    def _jump_pet(self):
        """
        Makes the pet jump.
        """

        self.on_delay = True
        self.is_walking = False

        # Adds a random vertical speed to the pet.
        self.vy = random.randint(-30, -15)
        self.y += self.vy

    def _cant_escape_bounds(self):
        """
        Prevents the pet from escaping the screen bounds.
        """

        # Floor is determined by the bottom bound of which screen the pet is in.
        bounds = [screen.geometry() for screen in self.screens]
        for bound in bounds:
            if self.x >= bound.left() and self.x <= bound.right():
                self.floor = bound.bottom() - self.height() - 20
                break

        # If beyond any of the limits, the pet is obstructed to go any further.
        self.x = max(self.left, min(self.x, self.right))
        self.y = max(self.top, min(self.y, self.floor))

    def _evolve_pet(self):
        """
        Evolves the pet.
        """

        self.on_delay = True
        iteration_counter = 0

        def animate():
            nonlocal iteration_counter

            iteration_counter += 1

            # The sprite is whiten to simulate evolution.
            self._whiten_image(alpha=200)

            # When the evolution is over
            if iteration_counter >= 100:
                self.timer.stop()

                # Changes the pet sprite.
                self.evolution_stage += 1
                self.image_path = os.path.join(
                    self.img_dir, f"{self.name}_{self.evolution_stage}.png"
                )
                self._load_image()

                # The original timer is run again.
                self.timer.stop()
                self.timer.timeout.disconnect()
                self.timer.timeout.connect(self._move_pet)
                self.timer.start(15)

                self.on_delay = False

        # Starts a timer for the pet to evolve.
        self.timer.stop()
        self.timer.timeout.disconnect()
        self.timer.timeout.connect(animate)
        self.timer.start(15)

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

    # ========== Visual effects ==========

    def _flip_image(self):
        """
        Flips the image on the horizontal axis.
        """
        transform = QTransform()
        transform.scale(-1, 1)
        flipped_pixmap = self.pixmap().transformed(transform)
        self.setPixmap(flipped_pixmap)

    def _whiten_image(self, alpha: int = 200):
        """
        Whitens the image.

        Parameters:
            alpha (int): Transparency.
        """
        pixmap = self.original_pixmap.copy()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(255, 255, 255, alpha))
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
            self.x = new_x
            self.y = new_y
            self.move(self.x, self.y)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.last_mouse_pos = None


app = QApplication(sys.argv)
pet = Pet(name="bulbasaur")
pet.show()
pet1 = Pet(name="charmander")
pet1.show()
pet2 = Pet(name="squirtle")
pet2.show()
sys.exit(app.exec_())
