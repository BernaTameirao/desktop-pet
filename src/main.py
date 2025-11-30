from PyQt5.QtWidgets import QApplication
import sys
import os
import logging

from Pet import Pet
from PetManager import PetManager

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet_names = set()
    for img in os.listdir("imgs"):
        pet_name = img.split("_")[0]
        pet_names.add(pet_name)
    
    logging.info(f"Starting pets: {', '.join(pet_names)}")

    manager = PetManager()
    pets = []
    for name in pet_names:
        pets.append(Pet(name=name))
        pets[-1].show()

        manager.add_pet(pets[-1])
    app.exec_()

if __name__ == "__main__":
    main()
