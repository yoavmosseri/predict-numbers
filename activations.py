import numpy as np


# Sigmoid function
def sigmoid(x): return 1 / (1 + np.exp(-x))
def sigmoid_deriv(x): return sigmoid(x) * (1 - sigmoid(x))


# Tanh function 
def tanh(x): return np.tanh(x)
def tanh_deriv(x): return 1-np.tanh(x)**2


# ReLU function 
def ReLU(x): return x * (x > 0)
def ReLU_deriv(x): return 1 * (x > 0)

activations_derivs = {'sigmoid':sigmoid_deriv,'tanh':tanh_deriv,'ReLU':ReLU_deriv}
