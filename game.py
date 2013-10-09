import core
import pyglet
import pyglet.clock
from pyglet.window import key
from core import GameElement
import sys
import random
import time

#### DO NOT TOUCH ####
GAME_BOARD = None
DEBUG = False
KEYBOARD = None
PLAYER = None
######################

GAME_WIDTH = 7
GAME_HEIGHT = 7


#### Put class definitions here ####
class Rock(GameElement):
    IMAGE = "Rock"
    SOLID = True

    def interact(self, player):
        next_y = self.y
        next_x = self.x
        if KEYBOARD[key.UP]:
            if self.y - 1 > 1:
                next_y = self.y - 1
        elif KEYBOARD[key.DOWN]:
            if self.y + 1 < GAME_HEIGHT - 1:
                next_y = self.y + 1
        elif KEYBOARD[key.LEFT]:
            if self.x - 1 > 1:
                next_x = self.x - 1
        elif KEYBOARD[key.RIGHT]:
            if self.x + 1 < GAME_WIDTH - 1:
                next_x = self.x + 1
        existing_el = GAME_BOARD.get_el(next_x, next_y)
        if not existing_el:
            GAME_BOARD.del_el(self.x, self.y)
            new_rock = Rock()
            GAME_BOARD.register(new_rock)
            GAME_BOARD.set_el(next_x, next_y, new_rock)
            GAME_BOARD.del_el(PLAYER.x, PLAYER.y)
            GAME_BOARD.set_el(self.x, self.y, PLAYER)

                
class Character(GameElement):
    IMAGE = "Cat"

    def next_pos(self, direction):
        # only move to the next position if it's in bounds.
        if direction == "up":
            if self.y == 1:
                return (self.x, self.y)
            return (self.x, self.y-1)
        elif direction == "down":
            if self.y == GAME_HEIGHT-2:
                return (self.x, self.y)
            return (self.x, self.y+1)
        elif direction == "left":
            if self.x == 1:
                return (self.x, self.y)
            return (self.x-1, self.y)
        elif direction == "right":
            if self.x == GAME_WIDTH-2:
                return (self.x, self.y)
            return (self.x+1, self.y)
        return None

    def __init__(self):
        GameElement.__init__(self)
        self.inventory = []

    
class Princess(Character):
    IMAGE = "Princess"
    SOLID = True

    def interact(self, player):
        GAME_BOARD.draw_msg("Collect the treasure and open the chest!")


class Open_Chest(GameElement):
    IMAGE = "Chest_Open"
    SOLID = True

    

class Closed_Chest(GameElement):
    IMAGE = "Chest_Closed"
    SOLID = True

    def interact(self, player):
        # If no key in the inventory, won't open the chest.
        if not player.inventory:
            GAME_BOARD.draw_msg("You need a key to open this.")
        key_found = False
        for item in player.inventory:
            if item.IMAGE == "Key":
                key_found = True

                break
        if not key_found:
            GAME_BOARD.draw_msg("You need a key to open this.")
        else:
            # If there's a key object in the inventory, removes closed chest
            # and sets an open chest object in place
            GAME_BOARD.del_el(self.x, self.y)
            open_chest = Open_Chest()
            GAME_BOARD.register(open_chest)
            GAME_BOARD.set_el(self.x, self.y, open_chest)
            go_to_new_level()
            

class Key(GameElement):
    IMAGE = "Key"
    SOLID = False

    def interact(self, player):
        player.inventory.append(self)
        GAME_BOARD.draw_msg("You just acquired a key! You have %d items!" %(len(player.inventory)))


class Boy(GameElement):
    IMAGE = "Boy"
    SOLID = True

    def interact(self, player):
        GAME_BOARD.draw_msg("Collect two blue gems and open the door!")

class Green_Gem(GameElement):
    IMAGE = "GreenGem"
    SOLID = False

    def interact(self, player):
        player.inventory.append(self)
        GAME_BOARD.draw_msg("You just acquired a green gem! You have %d items!" %(len(player.inventory)))

class Bug(GameElement):
    IMAGE = "Bug"
    SOLID = False

    def interact(self, player):
        if player.inventory:
            stolen_item = player.inventory.pop()
            inventory = len(player.inventory)
            if inventory == 1:
                GAME_BOARD.draw_msg("The bug ate a %s. You have %d item left. Tread carefully." %(stolen_item.IMAGE, inventory))
            else:
                GAME_BOARD.draw_msg("The bug ate a %s. You have %d items left. Tread carefully." %(stolen_item.IMAGE, inventory))                
        else:
            GAME_BOARD.draw_msg("Watch where you step, bugs eat what you pick up.")

class Closed_Door(GameElement):
    IMAGE = "DoorClosed"
    SOLID = True

    def interact(self, player):
        # If no gem in the inventory, won't open the chest.
        if not player.inventory:
            GAME_BOARD.draw_msg("You need two gems to open this.")

        num_of_blue_gem = 0
  
        for item in player.inventory:
            if item.IMAGE == "BlueGem":
                num_of_blue_gem += 1

        if num_of_blue_gem < 2:
            GAME_BOARD.draw_msg("You need two blue gems to open this.")
        else:
            GAME_BOARD.del_el(self.x, self.y)
            open_door = Open_Door()
            GAME_BOARD.register(open_door)
            GAME_BOARD.set_el(self.x, self.y, open_door)
            go_to_new_level()
            

class Open_Door(GameElement):
    IMAGE = "DoorOpen"
    SOLID = True

class Heart(GameElement):
    IMAGE = "Heart"
    SOLID = False

    def interact(self, player):
        player.inventory.append(self)
        GAME_BOARD.draw_msg("You just acquired a heart! You have %d items!" %(len(player.inventory)))

class Soft_Rock(GameElement):
    IMAGE = "Rock"
    SOLID = True

    def interact(self, player):
        if len(player.inventory) >= 3:
            self.SOLID = False
            go_to_new_level()
        else:
            GAME_BOARD.draw_msg("You need three items to defeat me!")

class Horn_Girl(GameElement):
    IMAGE = "Horns"
    SOLID = True

    def interact(self, player):
        GAME_BOARD.draw_msg("Find the soft rock!")


class Gem(GameElement):
    IMAGE = "BlueGem"
    SOLID = False

    def interact(self, player):
        player.inventory.append(self)
        GAME_BOARD.draw_msg("You just acquired a blue gem! You have %d items!" %(len(player.inventory)))
####   End class definitions    ####

def keyboard_handler():
    direction = None

    if KEYBOARD[key.UP]:
        direction = "up"
    elif KEYBOARD[key.DOWN]:
        direction = "down"
    elif KEYBOARD[key.LEFT]:
        direction = "left"
    elif KEYBOARD[key.RIGHT]:
        direction = "right"
    elif KEYBOARD[key.SPACE]:
        GAME_BOARD.erase_msg()
    elif KEYBOARD[key.ENTER]:
        create_new_level()
    elif KEYBOARD[key.DELETE]:
        global READY_FOR_NEXT_LEVEL
        if READY_FOR_NEXT_LEVEL:
            READY_FOR_NEXT_LEVEL = False
            restart()

    if direction:
        next_location = PLAYER.next_pos(direction)
        next_x = next_location[0]
        next_y = next_location[1]

        existing_el = GAME_BOARD.get_el(next_x, next_y)

        if existing_el:
            existing_el.interact(PLAYER)

        if existing_el is None or not existing_el.SOLID:
            GAME_BOARD.del_el(PLAYER.x, PLAYER.y)
            GAME_BOARD.set_el(next_x, next_y, PLAYER)


def make_rocks(number_of_rocks):
    rocks_made = 0
    while rocks_made < number_of_rocks:
        x = random.randint(1, GAME_WIDTH-2)
        y = random.randint(1, GAME_HEIGHT-2)
        existing_el = GAME_BOARD.get_el(x, y)
        if not existing_el:
            rock = Rock()
            make_anything(x, y, rock)
            rocks_made += 1

def make_anything(x, y, el):
    GAME_BOARD.register(el)
    GAME_BOARD.set_el(x, y, el)

def make_key(x,y):
    key = Key()
    make_anything(x, y, key)

def make_green_gem(x,y):
    gem = Green_Gem()
    make_anything(x,y,gem)

def make_gem(x,y):
    gem = Gem()
    make_anything(x,y,gem)

def make_closed_chest(x,y):
    closed_chest = Closed_Chest()
    make_anything(x,y, closed_chest)

def make_horn_girl(x,y):
    horn_girl = Horn_Girl()
    make_anything(x,y, horn_girl)

def make_heart(x,y):
    heart = Heart()
    make_anything(x,y,heart)

def make_soft_rock(number_of_rocks):
    rocks_made = 0
    while rocks_made < number_of_rocks:
        x = random.randint(1, GAME_WIDTH-2)
        y = random.randint(1, GAME_HEIGHT-2)
        existing_el = GAME_BOARD.get_el(x, y)
        if not existing_el:
            soft_rock = Soft_Rock()
            make_anything(x,y, soft_rock)
            rocks_made += 1
    

def make_bug(x,y):
    bug = Bug()
    make_anything(x,y, bug)

def make_princess(x,y):
    npc = Princess()
    make_anything(x,y,npc)

def make_boy(x,y):
    npc = Boy()
    make_anything(x,y,npc)

def make_closed_door(x,y):
    closed_door = Closed_Door()
    make_anything(x, y, closed_door)

def initialize():
    """Put game initialization code here"""
    global CURRENT_LEVEL 
    CURRENT_LEVEL = 1

    global READY_FOR_NEXT_LEVEL 
    READY_FOR_NEXT_LEVEL = False

    global PLAYER
    PLAYER = Character()
    GAME_BOARD.register(PLAYER)
    GAME_BOARD.set_el(2,2,PLAYER)

    GAME_BOARD.draw_msg("This is level 1.")

    make_key(1,1)
    make_key(5,5)
    make_gem(3,1)
    make_bug(2,4)
    make_closed_chest(4,3)
    make_princess(1,3)
    make_rocks(4)

def go_to_new_level():
    global READY_FOR_NEXT_LEVEL
    READY_FOR_NEXT_LEVEL = True
    global CURRENT_LEVEL
    if CURRENT_LEVEL < 3:
        GAME_BOARD.draw_msg("Do you want to advance to the next level? Press ENTER for yes, DELETE to start on level 1 again.")
    if CURRENT_LEVEL == 3:
        GAME_BOARD.draw_msg("You completed all 3 levels. You win! Congratulations! If you want to start over, press DELETE.")

def delete_board():
    for x in range(GAME_WIDTH):
        for y in range(GAME_HEIGHT):
            element = GAME_BOARD.get_el(x, y)
            if element:
                GAME_BOARD.del_el(x, y)

def restart():
    global CURRENT_LEVEL
    if CURRENT_LEVEL < 4:
        GAME_BOARD.draw_msg("You completed this level. Thanks for playing! Start again on level 1.")

    delete_board()

    GAME_BOARD.set_el(2,2,PLAYER)
    PLAYER.inventory = []
    CURRENT_LEVEL = 1
    make_key(5,5)
    make_key(1,1)
    make_gem(3,1)
    make_bug(2,4)
    make_closed_chest(4,3)
    make_princess(1,3)
    make_rocks(4)

def create_new_level():

    global READY_FOR_NEXT_LEVEL

    if READY_FOR_NEXT_LEVEL:

        READY_FOR_NEXT_LEVEL = False

        global CURRENT_LEVEL 
        CURRENT_LEVEL += 1

        if CURRENT_LEVEL < 4:
            GAME_BOARD.draw_msg("level %d"%CURRENT_LEVEL)
            delete_board()

            if CURRENT_LEVEL == 2:
                GAME_BOARD.set_el(2,2,PLAYER)
                PLAYER.inventory = []
                make_gem(4,2)
                make_gem(1,3)
                make_green_gem(5,1)
                make_gem(3,5)
                make_boy(5,4)
                make_closed_door(4,4)
                make_rocks(6)
            elif CURRENT_LEVEL == 3:
                GAME_BOARD.set_el(2,2,PLAYER)
                PLAYER.inventory = []
                make_heart(2,4)
                make_heart(4,4)
                make_gem(3,4)
                make_gem(1,2)
                make_green_gem(4,2)
                make_horn_girl(5,3)
                make_soft_rock(1)
                make_rocks(5)            
        else: 
            GAME_BOARD.draw_msg("Thanks for playing. Goodbye!")