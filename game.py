import pygame
import utils
import random

from classes import *
from pygame.locals import *


fps = 30

#todo load settings from config file
player = True
leveleditor = False
DEBUG = True

spawnrate_food = 1/(2 * fps)
spawnrate_herbivore = 1/(3 * fps)
spawnrate_carnivore = 1/(50 * fps)

print ("Imports Ready")

true_stopped = False
while not true_stopped:
	stopped = False

	pygame.init()
	screen = pygame.display.set_mode((1024,720))
	pygame.display.set_caption('nn-gen-survive')
	clock = pygame.time.Clock()

	print("Window Initialised")

	entities = []
	[entities.append(Cell(entities,utils.get_rand_pos(),0,utils.gen_rand_dna(170),Entity.HERBIVORE)) for _ in range(10)]
	entities.append(Food(entities,utils.get_rand_pos()))
	
	#for pos,rot,type in utils.load(map):
	#	if type == "blockade":
	#		#entities.append(Blockade(pos,rot))
	#		pass
	#	elif type == "car":
	#		car = Car(pos,rot)
	#	elif type[:3] == "map": #so map_1.png refers to the image 1.png
	#		backgroundmap = Map(type)

	
	print("Entities Loaded")
	
	while not stopped:
		dt = clock.get_time()/fps
		
		#handle user input
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
				stopped = True
				true_stopped = True
			if DEBUG:
				if event.type != pygame.MOUSEMOTION:
					if event.type == pygame.MOUSEBUTTONDOWN:
						print(event.pos)
			if player:
				if event.type == pygame.KEYDOWN:
					if   event.key == K_UP:    up    = True
					elif event.key == K_DOWN:  down  = True
					elif event.key == K_LEFT:  left  = True
					elif event.key == K_RIGHT: right = True
				if event.type == pygame.KEYUP:
					if   event.key == K_UP:    up    = False
					elif event.key == K_DOWN:  down  = False
					elif event.key == K_LEFT:  left  = False
					elif event.key == K_RIGHT: right = False
			if leveleditor:
				# todo:
				# 	move to other file
				# 	make generic (button => function mapping)
				if event.type == pygame.MOUSEBUTTONDOWN:
					elem = utils.get_closest(drawables,Pos(event.pos))
					if event.button == 1:
						move = elem
					if event.button == 2:
						bpos = Pos(event.pos)
						drawables.append(Blockade(bpos,0))
					elif event.button == 3:
						drawables.remove(elem)
					elif event.button == 4:
						elem.rot += utils.rad(15)
					elif event.button == 5:
						elem.rot -= utils.rad(15)
				if event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						move = 0
				if move != 0:
					move.pos = Pos(event.pos)

					
		
			
		#spawn in new objects
		if random.random() < spawnrate_food:
			food = Food(entities,utils.get_rand_pos())
			print (f"spawned {food}")
			entities.append(food)
			
		herbivores = list(filter(lambda x: x.type == Entity.HERBIVORE,entities))	
		if len(herbivores) <= 10 and random.random() < spawnrate_herbivore :
			
			if len(herbivores) >= 3:
				sorted_herbivores = list(sorted(herbivores,key = lambda x: -x.getFitness()))
			
				#randomly pick two herbivores (but prefer fitter ones)
				h0 = sorted_herbivores[0]
				h1 = sorted_herbivores[1]
				
				#crossgenerate new DNA
				dna = h0.combineDNA(h1)
				
				#spawn an agent with this new DNA
				entities.append(Cell(entities,utils.get_rand_pos(),0,dna,Entity.HERBIVORE))
			else:
				entities.append(Cell(entities,utils.get_rand_pos(),0,utils.gen_rand_dna(170),Entity.HERBIVORE))
			
		if random.random() < spawnrate_carnivore:
			#randomly pick two carnivores (but prefer fitter ones)
			
			#crossgenerate new DNA
			
			#spawn an agent with this new DNA
			pass				
		
			
		
			
		
		
		
		#transition every object to the next state
		for ent in entities:
			if not ent.pos.is_inside(Pos((0,0)),Pos((1024,720))):
				ent.die()
		for ent in entities:
			ent.raycast(screen)
		for ent in entities:
			ent.update(dt)
			
		#update screen
		screen.fill((200,200,200))
		for ent in entities:
			ent.draw(screen)

		pygame.display.flip()
		pygame.display.update()
		
		clock.tick(fps)
		pygame.display.set_caption('nn-gen-survive ' + utils.format(clock.get_fps()))

	pygame.quit()

print("Game Stoppped")

if leveleditor:
	drawables.append(car) #also save the car
	drawables.append(backgroundmap)
	utils.save(map,drawables)
	
print("Data has been saved")
quit()
