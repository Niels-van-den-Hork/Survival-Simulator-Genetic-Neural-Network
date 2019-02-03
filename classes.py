import pygame
import math
import utils
import neuralnet
import random

DEBUG = False

'''
todo:
	high:
		x make runnable
		x Agents have a neuralnetwork
		Agents can breed
		x randomspawns
		herbivores can eat food
		

	med:
		redo raycasting the proper way (not based on pixel values)
		redo movement
		cell update: first filter then check for collision
		Entity init:shared entity list possibly better to acces this through a non class function?
		'player' can add food and agents on demand
		
	low:
		give dna seperate class
		Agents have dash ability
		dna also contains ray angles
		network input contains agents health
		let agents decide on a goal. It should then commit to that goal until succes or failure.
		implement natural events where agents need to learn to react to (maybe a fire spreading) Can also let only part of the population learn to react, and thus split into a new specie. 
		can only breed if touching
		any agent can breed but only if they have enough food, is that better than the current fitness?
		
		randomness in lifespan
			
		Allow a human to control an agent

'''

class Entity(pygame.sprite.Sprite):
	ENTITY = 0
	FOOD = 1
	CELL = -1
	CARNIVORE = 2
	HERBIVORE = 3
	
	def __init__(self,entities,img_path,pos,rot,type = 0):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img_path)
		self.rot = rot
		self.pos = pos
		self.type = type
		self.entities = entities #shared entity list possibly better to acces this through a non class function?
		
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos.tuple()

	def draw(self,screen):
		rotated = pygame.transform.rotate(self.image,self.rot/(2*math.pi)*360)
		self.rect = rotated.get_rect()
		self.rect.center = self.pos.tuple()
		screen.blit(rotated,self.rect)
		self.mask = pygame.mask.from_surface(rotated)
		if DEBUG:

			pygame.draw.rect(screen,(200,0,0),self.rect,1)
			pygame.draw.lines(screen,(0,200,0),1,self.mask.outline())
	
	def getCollision(self,entities):
		return pygame.sprite.spritecollide(self,entities,False)#check if works
		
	def update(self,dt):
		return False
		
	def raycast(self,screen,numrays = 5,angle = 45):
		return False
	
	def die(self):
		self.entities.remove(self)
	
	def __str__(self):
		return f"{self.pos};{self.rot};{self.type}"
		
	#def __repr__(sefl):
	#	return f"{self.pos};{self.rot};{self.type}"
		
	def toString(self):
		return self

		
class Food(Entity):
	def __init__(self,entities,pos,rot = 0):
		Entity.__init__(self,entities,"berry.png",pos,rot,Entity.FOOD)
		self.nutrition = 50
	
	def getNutrition(self):
		return self.nutrition
		
class Cell(Entity):
	
	def __init__(self,entities,pos,rot,dna,species,human = False):
		Entity.__init__(self,entities,"herbivore.png",pos,rot,species)
		
		self.brain = neuralnet.Brain(dna)
		self.dna = dna
		self.species = species
		
		self.health = 100
		self.age = 0
		self.hunger = 0.1
		self.carnivore_nutrition_factor = 0.5
		self.herbivore_nutrition_factor = 1
		
		self.steer_coef = 0.05
		self.steer_growth = 0.5
		self.acc_coef = 0.4
		self.dec_coef = -0.02
		self.vel_min = 0
		self.vel_max = 5
		self.vel = 0
		
		
				
	def update(self,dt):
		
		self.age += dt
		self.health -= self.hunger * dt
		
		if (self.health < 0):
			self.die()
		#if outside of bounds
		situation = [r.range for r in self.rays]
		accel,steer = self.brain.predict(situation)
		
		self.accelerate(accel,dt)
		self.turn(steer,dt)
		
		self.pos.x += math.cos(self.rot)*self.vel*dt
		self.pos.y += math.sin(-self.rot)*self.vel*dt
		
		#todo: first filter then check for collision
		collisions = self.getCollision(self.entities)
		
		if self.type == Entity.CARNIVORE:
			herbivores = filter(
				lambda x: x.type == Entity.HERBIVORE,
				collisions
			)
			for herb in herbivores:
				self.health = min(200,self.health+(herb.health*self.carnivore_nutrition_factor))
				herb.die()
		elif self.type == Entity.HERBIVORE:
			foods = filter(
				lambda x: x.type == Entity.FOOD,
				collisions
			)
			for food in foods:
				print(food)
				self.health = min(200,self.health+(food.nutrition*self.herbivore_nutrition_factor))
				food.die()
					
	#dna should get it's own class
	def combineDNA(self,partner,mutationfactor = 0.01):
		dn = []
		for d1,d2 in zip(self.dna,partner.dna):
			if (random.random() < mutationfactor):
				dn.append(random.random())
			elif (random.random() < 0.5):
				dn.append(d1)
			else:
				dn.append(d1)
		return dn	
	
	def getFitness(self):
		return self.age + self.health
	
	#maybe every method after this should be part of a 'movable' class
	def accelerate(self,p,dt):
		p = max(-3,min(1,p))

		self.vel += p*self.acc_coef*dt

		self.vel = max(self.vel_min,min(self.vel_max,self.vel))

	def turn(self,r,dt):
		r = max(-1,min(r,1))

		self.rot += r*self.steer_coef*(self.vel/(self.vel_max*self.steer_growth)+1-self.steer_growth)*dt

		if self.rot > math.pi:
			self.rot = -math.pi
		if self.rot < -math.pi:
			self.rot = math.pi
		self.accelerate(-0.1,dt)
	
	def raycast(self,screen,numrays = 5,angle = 45):
		self.rays = []
		for curangle in utils.frange(-angle,angle,angle/2,inclusive=True):
			r,c = utils.ray(screen, self.pos, self.rot+utils.rad(curangle ))
			self.rays.append(Ray(r,c,self.pos))
	
	def draw(self,screen):#propagates
		Entity.draw(self,screen)
		for r in self.rays:
			r.draw(screen)	
			
	
	
class Map(Entity):
	def __init__(self,filename):
		Entity.__init__(self,filename[4:],Pos((1024/2,720/2)),0)
		self.filename = filename

	def toString(self):
		return self.filename;

class Ray:
	def __init__(self,range,point,origin):
		self.range = range
		self.point = point
		self.origin = origin
	def draw(self,screen):
		colour = ((self.range)*255,(1-self.range)*255,0)
		endpoints = [self.point.tuple(),self.origin.tuple()]
		pygame.draw.lines(screen,colour,5,endpoints)
	def toString(self):
		return self.origin.toString() + " :  " + self.point.toString() + " : " + str(self.range)

class Pos:
	def __init__(self,p):
		self.x = float(p[0])
		self.y = float(p[1])
		
	def tuple(self):
		return (int(self.x),int(self.y))
		
	def toString(self):
		return utils.format(self.x,2)+":"+utils.format(self.y,2)
		
	def __str__(self):
		return self.toString()
		
	def dist(self,pos):
		return math.sqrt((pos.x-self.x)**2+(pos.y-self.y)**2)
		
	def smaller_than(self,pos):
		return self.x <= pos.x or self.y <= pos.y
	
	def is_inside(self,lt, rb ):
		return self.x > lt.x and self.x < rb.x and self.y > lt.y and self.y < rb.y
	
	def copy(self):
		return Pos((self.x,self.y))
