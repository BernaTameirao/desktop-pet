from Pet import Pet
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    pet = Pet(name="bulbasaur")
    pet.show()
    pet1 = Pet(name="charmander")
    pet1.show()
    pet2 = Pet(name="squirtle")
    pet2.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()