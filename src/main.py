from Pet import Pet
from PyQt5.QtWidgets import QApplication
import sys
import os
import logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    app = QApplication(sys.argv)

    pet_names = set()
    for img in os.listdir("imgs"):
        pet_name = img.split("_")[0]
        pet_names.add(pet_name)

    logging.info(f"Starting pets: {', '.join(pet_names)}")
    pets = []
    for name in pet_names:
        pets.append(Pet(name=name))
        pets[-1].show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
