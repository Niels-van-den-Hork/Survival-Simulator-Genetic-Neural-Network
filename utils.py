from classes import *
import pygame
import random

DEBUG = False
def load(map_path):
	map = open(map_path, "r")
	obj = []
	for lines in map:
		elem = lines[:-1].split(";")
		elem[0] = elem[0].split(":")
		elem[0] = Pos(elem[0])
		elem[1] = float(elem[1])
		obj.append(elem)
		if DEBUG:
			bcol.blue( "loaded " + elem[2] + " at " + elem[0].toString()) 
	map.close()
	return obj

def save(map_path,drawables):
	map = open(map_path,"w")
	for elem in drawables:
		map.write(elem.pos.toString() +";"+ format(elem.rot,4) +";"+ elem.toString()+"\n")
		if DEBUG:
			bcol.blue( "saved " + elem.pos.toString() +";"+ format(elem.rot) +";"+ elem.toString())
	map.close()

def save_training(file_path,inputs,outputs):
	file = open(file_path+".in","a")
	for input in inputs:
		file.write(format(input[0],dig=4) + ":"  + format(input[1],dig=4) + ":" + format(input[2],dig=4) + ":"  + format(input[3],dig=4) + ":" + format(input[4],dig=4)+"\n")
	file.close()
	file = open(file_path+".out","a")
	for output in outputs:
		file.write(format(output[0],dig=4) + ":"  + format(output[1],dig=4)+ "\n")
	file.close()
def load_training(file_path):
	all_input = []
	all_output = []

	file = open(file_path+".in","r")
	for lines in file:
		all_input.append(list(map(lambda c: float(c),lines[:-1].split(":"))))
	file.close()

	file = open(file_path+".out","r")
	for lines in file:
		all_output.append(list(map(lambda c: float(c),lines[:-1].split(":"))))

	file.close()
	return all_input,all_output

def format(num,dig=0):
	n = str(num).split(".")
	if len(n) <= 1 or dig == 0:
		return n[0]
	else:
		return n[0] +'.'+ n[1][0:dig]

def frange(b, e, step = 1,inclusive = False):
	while  b < e or (inclusive and b <= e):
		yield b
		b += step
	
def get_closest(drawables,pos):
	match = drawables[0]
	lowest = 100000000
	for elem in drawables:
		dist = pos.dist(elem.pos)
		if dist < lowest:
			lowest = dist
			match = elem
	return match

def get_rand_pos(x = 1024, y = 720):
	pad = 50
	nx = random.randrange(0+pad,x-pad)
	ny = random.randrange(0+pad,y-pad)
	
	return Pos((nx,ny))
	
def gen_rand_dna(len):
	return [(random.random()*2)-1 for _ in range(len)]
	
#after blockades are drawn!
def ray(screen,origin,angle = 0,range = 300, steps = 4):
	delta = 64
	cur = origin.copy()
	dx = math.cos(angle)*steps
	dy = math.sin(-angle)*steps
	finished = False
	while delta < range:
		cur.x += dx
		cur.y += dy
		if pixel_at(screen,cur):
			if DEBUG:
				bcol.green("dist: " + str(delta) +" pos: " + cur.toString())
			finished = True
			
			return delta/range,cur
		delta += steps
	return range/range,cur

def pixel_at(screen,pos):
	if pos.smaller_than(Pos((0,0))) or Pos((screen.get_width(),screen.get_height())).smaller_than(pos):
		return False,(0,0,0,0)
	colour = screen.get_at((int(pos.x),int(pos.y))	)
	return 180 < colour[2] and  colour[2] < 200 #colour[0] + colour[1] +

def rad(deg):
	return deg/360*2*math.pi
