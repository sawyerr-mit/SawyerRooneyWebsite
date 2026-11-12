import os
from platform import system

#Just to disable errors, I had to look up how to do this
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import numpy as np
import pickle

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)



def init_params_he(layer_sizes, seed=None):
    # if seeded random number generation
    if seed is not None:
        np.random.seed(seed)
    # parameter dictionary for neural network
    params = {}
    # for "layer" in range 1 to layer_sizes
    for l in range(1, len(layer_sizes)):
        # inputs into the node descriped as nodes_in
        nodes_in = layer_sizes[l-1]
        # He initilization using normal distribution and variance adjustment term
        params['W'+str(l)] = np.random.randn(layer_sizes[l], nodes_in) * np.sqrt(2.0 / nodes_in)
        # Bias vector initialized to 0 due to symmetry preservation
        params['b'+str(l)] = np.zeros((layer_sizes[l], 1))
    return params

# definition of the sigmoid activation function to normalize activation values
def sigmoid(Z):
    A = 1 / (1 + np.exp(-Z))
    return A, Z

# definition of the softmax activation function to normalize activation values
def softmax(Z):
    expZ = np.exp(Z - np.max(Z, axis=0, keepdims=True))
    return expZ / np.sum(expZ, axis=0, keepdims=True)

# definition of the relu activation function to normalize activation values. I used this activation function as it
# is most commonly used with the He initialization
def relu(Z):
    return np.maximum(0, Z), Z

# forward propogation handling, parameters include input vector X and weight parameters
def forward_prop(X, params):
    # input layer equals X
    A = X
    # temporary data storage
    caches = []
    # number of layers (pairs W/b)
    L = len(params) // 2
    # for all the weights/biases in our network
    for l in range(1, L + 1):
        # save the current activation layer as the previous - we are moving on
        A_prev = A
        # create a temp matrix to store weights
        W = params['W'+str(l)]
        # create a temp vector to store biases
        b = params['b'+str(l)]
        # compute linear hypothesis
        Z = np.dot(W, A_prev) + b
        # save information to linear cache
        linear_cache = (A_prev, W, b)
        # For all non-final activation layers, use the relu activation function, for the final layer, use softmax
        if l == L:
            # set A to new activations
            A = softmax(Z)
            # save activation linear hypothesis to activation cache
            activation_cache = Z
        else:
            A, activation_cache = relu(Z)
        caches.append((linear_cache, activation_cache))
        # return both the final activation layer (the output) and the caches used for data handling
    return A, caches

# cost function, in this case I used corss entropy. But you could use quadratic loss if you implemented multi-class
# classification
def cost_function(AL, Y):
    m = Y.shape[1]
    cost = -np.sum(Y * np.log(AL + 1e-12)) / m
    return float(np.squeeze(cost))

# computes back propagation for the previous layer. Parameters include the difference from the expected solution dA,
# the cache values found earlier, and the activation type set to 'relu'
def one_layer_backward(dA, cache, activation='relu'):
    # saves linear and activation cache that were computed earlier
    linear_cache, activation_cache = cache
    A_prev, W, b = linear_cache
    m = A_prev.shape[1]
    # handles different activation functions
    if activation == 'relu':
        dZ = dA.copy()
        dZ[activation_cache <= 0] = 0
    elif activation == 'sigmoid':
        A, _ = sigmoid(activation_cache)
        dZ = dA * A * (1 - A)
    elif activation == 'softmax':
        dZ = dA
    else:
        exit('Invalid activation function')

    # Same for all activation functions as we've used dA and the activation type to compute dZ. Computes the changes
    # in the W and b values needed to minimize the cross-entropy cost function
    dW = (1.0/m) * np.dot(dZ, A_prev.T)
    db = (1.0/m) * np.sum(dZ, axis=1, keepdims=True)
    dA_prev = np.dot(W.T, dZ)
    return dA_prev, dW, db

# iterates over the entire network and computes back-propagation for everything, parameters include the output layer
# found through forward propagation, the expected values in Y, and the caches calculated
def backprop(AL, Y, caches):
    # gradient dictionary
    grads = {}
    L = len(caches)
    dAL = AL - Y  # softmax + cross-entropy
    # set current cache to the cache of the last layer
    current_cache = caches[L-1]
    # use softmax to compute the gradient changes for the previous layer
    grads['dA'+str(L-1)], grads['dW'+str(L)], grads['db'+str(L)] \
        = one_layer_backward(dAL, current_cache, activation='softmax')
    # use relu for the rest of the gradient descent
    for l in reversed(range(L-1)):
        current_cache = caches[l]
        grads['dA'+str(l)], grads['dW'+str(l+1)], grads['db'+str(l+1)] \
            = one_layer_backward(grads['dA'+str(l+1)], current_cache)
    # return the gradient descent
    return grads

# a method to update the parameters of the network depending on the values computed from the gradient descent.
# The learning rate is the small step we take in the direction of the gradient
def update_parameters(parameters, grads, learning_rate):
    L = len(parameters) // 2
    for l in range(1, L+1):
        # changes are made OPPOSITE the gradient in the direction of greatest decrease
        parameters['W'+str(l)] -= learning_rate * grads['dW'+str(l)]
        parameters['b'+str(l)] -= learning_rate * grads['db'+str(l)]
    return parameters

# Converts the mnist data set into 10 one-hot valued vectors
def one_hot(Y, num_classes=10):
    return np.eye(num_classes)[Y.reshape(-1)].T

# Instead of iterating over all inputs, take a randomly selected batch of inputs
def get_mini_batches(X, Y, batch_size, seed=None):
    # fairly readable code, it shuffles both the inputs and outputs together, and selects up to batch size
    m = X.shape[1]
    if seed is not None:
        np.random.seed(seed)
    perm = np.random.permutation(m)
    X_shuffled = X[:, perm]
    Y_shuffled = Y[:, perm]
    mini_batches = []
    for k in range(0, m, batch_size):
        X_batch = X_shuffled[:, k:k+batch_size]
        Y_batch = Y_shuffled[:, k:k+batch_size]
        mini_batches.append((X_batch, Y_batch))
    return mini_batches

# training algorithm. Parameters of note are epochs, which is the number of iterations that will be done, and
# learning_rate, which is the magnitude of the step taken opposite the gradient. Others hav been explained or are
# self-explanatory.
def train_minibatch(X, Y, layer_dims, epochs, learning_rate, batch_size=64, print_every=1):
    # initilize network for training
    params = init_params_he(layer_dims)
    cost_history = []
    grads = None
    # iterate over the data set once for every epoch
    for epoch in range(epochs):
        # initialize a mini-set of batches to reduce run-time
        minibatches = get_mini_batches(X, Y, batch_size)
        epoch_cost = 0.0
        # begins training, first is forward prop, then cost function evaluation, then back prop, then reassignment
        for X_batch, Y_batch in minibatches:
            # forward prop
            AL, caches = forward_prop(X_batch, params)
            # cost evaluation
            cost = cost_function(AL, Y_batch)
            # backpropagation and gradient descent
            grads = backprop(AL, Y_batch, caches)
            # parameter updating from gradient descent
            params = update_parameters(params, grads, learning_rate)
            # the cost of every epoch is the cost of the output times the number of classes
            # should reduce with time as the neural network converges
            epoch_cost += cost * X_batch.shape[1]
        # final epoch output
        epoch_cost /= X.shape[1]
        cost_history.append(epoch_cost)
        # print the estimated average gradient magnitude for each epoch - should get smaller over time
        if (epoch % print_every) == 0:
            grad_norm = 0.0
            if grads is not None:
                for l in range(1, len(layer_dims)):
                    grad_norm += np.linalg.norm(grads['dW'+str(l)])
            print(f"Epoch {epoch:03d} - cost: {epoch_cost:.4f} - grad_norm(est): {grad_norm:.4f}")
    return params, cost_history

# just a shortcut to covert the one-hot vectors back into numeric values
def forward_predict(X, params):
    AL, _ = forward_prop(X, params)
    return np.argmax(AL, axis=0)

# main function where the network is first trained, and where the parameters are then stored
def main():
    # imported here (not at top) so testing.py can use forward_predict without installing tensorflow
    from tensorflow.keras.datasets import mnist
    # X contains images, Y contains solutions. Train is used to train the network, test is used to test after
    (X_train, Y_train_raw), (X_test, Y_test_raw) = mnist.load_data()
    # normalize image data
    X_train = X_train.reshape(X_train.shape[0], -1).T.astype(np.float32) / 255.0
    X_test = X_test.reshape(X_test.shape[0], -1).T.astype(np.float32) / 255.0
    # convert answer keys into one-hot vectors
    Y_train = one_hot(Y_train_raw)
    Y_test = one_hot(Y_test_raw)

    # neural network initializations. There are 784 input nodes (28*28) 2 hidden layers, and one output layer
    layer_sizes = [784, 128, 64, 10]
    epochs = 100
    learning_rate = 0.1
    batch_size = 32

    # train the algorithm and save parameters
    params, cost_history = (
        train_minibatch(X_train, Y_train, layer_sizes, epochs, learning_rate, batch_size=batch_size, print_every=1))

    # save to pkl file to test in testing file
    with open('trained_params.pkl', 'wb') as f:
        pickle.dump(params, f)

    # save predictions and compare to real labels and compute accuracy
    predictions = forward_predict(X_test, params)
    labels = np.argmax(Y_test, axis=0)
    accuracy = np.mean(predictions == labels) * 100
    print(f"Test accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    main()
