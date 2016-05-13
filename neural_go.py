
import pygame
from sys import exit

from game_controller import *

def main():
  game_controller = GameController()
  game_controller.run()
  # game_controller.sim()

if __name__ == '__main__':
  main()
