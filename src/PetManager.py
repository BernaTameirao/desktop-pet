import time
import random
import math

from PyQt5.QtCore import QTimer

class PetManager:
    def __init__(self):
        self.pets = [] 

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # 20 frames/second

    def add_pet(self, pet):
        """
        Adds a pet to the list of managed pets.

        Parameters:
            pet: object to be added to the list.
        """
        self.pets.append(pet)
        pet.manager = self

    def remove_pet(self, pet):
        """
        Removes a pet from the list of managed pets.

        Parameters:
            pet: object to be removed from the list.
        """
        if pet in self.pets:
            self.pets.remove(pet)

    def update(self):
        """
        Checks for interactions between the pets.
        """

        # Gets a list of only avaliable pets.
        active_pets = [p for p in self.pets if not p.in_battle]
        
        for i, pet1 in enumerate(active_pets):
            for pet2 in active_pets[i+1:]:

                # If all conditions are met, there is a random chance that a battle occurs.
                if self.check_proximity(pet1, pet2, proximity_x=100, proximity_y=100) and random.random() < 0.02:
                    self.battle(pet1, pet2)

    
    def check_proximity(self, pet1, pet2, proximity_x: int = 100, proximity_y: int = 100):
        """
        Checks if two pets are close, and facing each other.

        Parameters:
            pet1: First pet.
            pet2: Second pet.
            proximity_x (int): Maximum number of pixels in the x-axis for the interaction to occur.
            proximity_y (int): Maximum number of pixels in the y-axis for the interaction to occur.

        Returns:
            If all the conditions are met. (bool)
        """
        # Gets the distance between the pets.
        dx = abs(pet1.pos_x - pet2.pos_x)
        dy = abs(pet1.pos_y - pet2.pos_y)

        # Checks if they are facing each other.
        if pet1.pos_x < pet2.pos_x:
            facing_each_other = pet1.direction == 1 and pet2.direction == -1
        else:
            facing_each_other = pet1.direction == -1 and pet2.direction == 1
            
        return dx < proximity_x and dy < proximity_y and facing_each_other

    def battle(self, pet1, pet2):
        """
        Group the functions related to battle.

        Parameters:
            pet1: First pet.
            pet2: Second pet.
        """

        winner = self.resolve_battle(pet1, pet2)
        self.handle_battle_result(pet1, pet2, winner)

    def resolve_battle(self, pet1, pet2):
        """
        Decides the winner of the battle.

        Parameters:
            pet1: First pet.
            pet2: Second pet.

        Returns:
            The winner of the battle. (object)
        """

        n = 5
        # Two moves are chosen at random.
        move1 = random.randint(1, n)
        time.sleep(0.001)
        move2 = random.randint(1, n)

        # A rock-paper-scissor like script decides the winner.
        # If tie, the winner is None
        if move1 == move2:
            return None
        
        if (move1 + 1) % n == move2:
            return pet1
        elif (move2 + 1) % n == move1:
            return pet2
        else: # If an error happens
            return None 

    def handle_battle_result(self, pet1, pet2, winner):
        """
        Animates the pets according to the battle results.

        Parameters:
            pet1: First pet.
            pet2: Second pet.
            winner: Pet that won the battle.
        """
        iteration_counter = 0
        pet1.in_battle = True
        pet2.in_battle = True

        def animate():
            nonlocal iteration_counter
            iteration_counter += 1

            # If the pet is moved to somewhere distant from the other pet, the battle ends.
            if not self.check_proximity(pet1, pet2, proximity_x=200, proximity_y=200):
                pet1.in_battle = False
                pet2.in_battle = False
                timer.stop()
                return

            # Idle animation that the pets do when in battle.
            offset_y = 5 * math.sin(iteration_counter * 0.5)
            if pet1.is_walking:
                pet1.pos_y = math.floor(pet1.floor + offset_y)
            if pet2.is_walking:
                pet2.pos_y = math.floor(pet2.floor + offset_y)
            
            # When the battle is over
            if iteration_counter >= 500:
                timer.stop()
                
                if winner is pet1:
                    pet1.win_battle()
                    pet2.lose_battle()
                    pet1.level += 1
                    
                elif winner is pet2:
                    pet1.lose_battle()
                    pet2.win_battle()
                    pet2.level += 1

                else:
                    pet1.win_battle()
                    pet2.win_battle()
                
                pet1.in_battle = False
                pet2.in_battle = False

        # Starts the timer for the battle animations.
        timer = QTimer()
        timer.timeout.connect(animate)
        timer.start(15)