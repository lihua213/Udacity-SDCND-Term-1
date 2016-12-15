### Import
import pickle
import numpy as np
import pandas as pd
import matplotlib.image as mpimg
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn import preprocessing
import cv2
import math
import time
import h5py
import json
import os


from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, Adam, RMSprop
from keras.utils import np_utils


### Load data
#TODO Improve the following if possible.

# Read in CSV file
csv_loc = "data/driving_log.csv"
df = pd.read_csv(csv_loc)
features_col = df['center']
features_col = features_col.map(lambda x: x.lstrip('IMG/'))
labels_col = df['steering']
labels_col = labels_col.values.tolist()
features_col = features_col.values.tolist()

print("Length of Features: {0}, Labels: {1}".format(len(features_col), len(labels_col)))

# Read in images
images = os.listdir("data/IMG/")
center_images = []

for idx in range(len(features_col)):
    # reading in an image
	image = mpimg.imread("data/IMG/" + features_col[idx])
	center_images.append(image)

features = np.array(center_images)
labels = np.array(labels_col)

print("Length of Features: {0}, Labels: {1}".format(len(features), len(labels)))

### Split data
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.15, random_state=432422)
'''
mpimg.imsave("pre_crop_test_1.jpg", X_train[0])
mpimg.imsave("pre_crop_test_2.jpg", X_train[1])
mpimg.imsave("pre_crop_test_3.jpg", X_train[50])
'''

### Pre-Process
# Resize
def resize_img(image):
    # And crop
    image = image[60:140,40:280]
    return cv2.resize(image, (160, 80))
    
# Normalize
def normalize_img(image):
	return cv2.normalize(image, None, alpha=-0.5, beta=0.5, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

X_train = np.array([resize_img(image) for image in X_train], dtype=np.float32)
X_test = np.array([resize_img(image) for image in X_test], dtype=np.float32)
'''
mpimg.imsave("crop_test_1.jpg", X_train[0])
mpimg.imsave("crop_test_2.jpg", X_train[1])
mpimg.imsave("crop_test_3.jpg", X_train[50])
'''
X_train = np.array([normalize_img(image) for image in X_train], dtype=np.float32)
X_test = np.array([normalize_img(image) for image in X_test], dtype=np.float32)

### Helper Functions
'''
def data_generator(train_features, train_labels, batch_size):
	num_rows = int(len(train_features))
	ctr = None
	batch_x = np.zeros((batch_size, train_features.shape[1], train_features.shape[2], 3))
    batch_y = np.zeros(batch_size)
	while True:
		print("In while")
		for i in range(batch_size):
			print("In for")
			if ctr is None or ctr >= num_rows:
				ctr = 0
				train_features, train_labels = shuffle(train_features, train_labels)

			batch_x[i] = train_features[i]
			batch_y[i] = train_labels[i]
			ctr += 1
		print("Outside for and ctr: {0}".format(ctr))
		yield (batch_x, batch_y)
'''
print("Test")
print(X_train.shape[1:])
	
### Parameters
layer_1_depth = 24
layer_2_depth = 36
layer_3_depth = 48
filter_size = 5
num_classes = len(np.unique(y_train))
num_neurons_1 = 512
num_neurons_2 = 128
epochs = 5
batch_size = 64
samples_per_epoch = X_train.shape[0]
 
### Model
model = Sequential()
model.add(Convolution2D(layer_1_depth, filter_size, filter_size, border_mode = 'valid', subsample = (2,2), input_shape = X_train.shape[1:]))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))
model.add(Convolution2D(layer_2_depth, filter_size, filter_size, border_mode = 'valid', subsample = (1,1)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))
model.add(Convolution2D(layer_3_depth, 3, 3, border_mode = 'valid', subsample = (1,1)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))

model.add(Flatten())
model.add(Dense(num_neurons_1))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(num_neurons_2))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))

model.summary()

### Compile and Train
#X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2],X_train.shape[3] )
#X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[3], X_test.shape[3])

model.compile(loss='mse',
              optimizer=Adam(lr = 0.0001),
              metrics=['mean_absolute_error', 'accuracy'])

### Save Model
with open('model.json', 'w') as f:
	json.dump(model.to_json(), f)
with open('model_read.json', 'w') as f:
	json.dump(json.loads(model.to_json()), f,
			indent=4, separators=(',', ': '))


history = model.fit(X_train, y_train,
                    batch_size=batch_size, nb_epoch=epochs,
                    verbose=1, validation_data=(X_test, y_test))                                            
'''
history = model.fit_generator(data_generator(X_train, y_train, batch_size), 
											samples_per_epoch=samples_per_epoch, 
											nb_epoch = epochs,
											verbose = 1,
											validation_data = (X_test, y_test))
'''

### Save weights
model.save_weights('model.h5')
