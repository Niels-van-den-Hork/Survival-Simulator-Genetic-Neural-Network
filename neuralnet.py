import argparse

import numpy as np
from matplotlib import pyplot as plt
from sklearn.neural_network import MLPRegressor,MLPClassifier
from sklearn.model_selection import train_test_split

import utils

def abs(x):
	if x > 0:
		return x
	return -x
	
def dna_to_weights(dna):
	dna = iter(dna)
	weights = []
	ls = [5,10,10,2]
	
	weights.append(np.array([[next(dna) for _ in range(ls[1])] for _ in range(ls[0])]))
	
	weights.append(np.array([[next(dna) for _ in range(ls[2])] for _ in range(ls[1])]))
	
	weights.append(np.array([[next(dna) for _ in range(ls[3])] for _ in range(ls[2])]))
		
	return weights
	
	
class Brain:
	def __init__(self,dna):
		self.network = MLPRegressor(hidden_layer_sizes=(10,10),activation='tanh')
		self.dna = dna
		
		#fit on nothing so coefs_ get initialised (it needs to know the input and output dimensions)
		self.network.fit([[0,0,0,0,0]],[[0,0]])
		#print(self.network.coefs_)
		self.network.coefs_ = dna_to_weights(dna)
		
	def predict(self,input):
		return self.network.predict([input])[0]

	def get_dna(self):
		return weights_to_dna(dna)



