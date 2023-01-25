import numpy as np


class Layer:
    def __init__(self, input_len: int, output_len: int, activation, activation_deriv):
        # between -1 and 1
        self.weights = (np.random.rand(input_len, output_len) - 0.5) * 2
        self.bias = (np.random.rand(output_len) - 0.5) * 2
        self.activation = activation
        self.activation_deriv = activation_deriv

    def _calc_derivs(self, output_array, target_array):
        cost_deriv = 2*(output_array - target_array)
        sigmoid_deriv = self.activation_deriv(self.output_no_activation)

        input_deriv = np.dot(cost_deriv*sigmoid_deriv, self.weights.T)
        bias_deriv = (cost_deriv * sigmoid_deriv).flatten()
        weights_deriv = np.outer(self.input, (cost_deriv*sigmoid_deriv))

        return weights_deriv, bias_deriv, input_deriv

    def _update_values(self, weights_deriv, bias_deriv, learning_rate):
        self.weights -= weights_deriv * learning_rate
        self.bias -= bias_deriv * learning_rate

    def forward_propagation(self, input_array: np.array):
        self.output_no_activation = np.dot(input_array, self.weights)+self.bias
        return self.activation(self.output_no_activation)

    def backward_propagation(self, input_array, target_array, learning_rate):
        self.input = input_array
        output_array = self.forward_propagation(self.input)

        weights_deriv, bias_deriv, input_deriv = self._calc_derivs(
            output_array, target_array)
        self._update_values(weights_deriv, bias_deriv, learning_rate)

        return input_array - input_deriv
