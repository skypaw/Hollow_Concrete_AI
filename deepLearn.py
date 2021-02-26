# calling a function
import creatingDataSet
from sklearn.utils import shuffle
import matplotlib.pyplot as plt

import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# raw data
dim, cm = creatingDataSet.data_for_network()

print(dim)
print(cm)

# rescaling data and shuffling
dim, cm = shuffle(dim, cm)

# sequential model
model = Sequential([Dense(units=16, input_shape=(1,), activation='relu'),
                    Dense(units=32, activation='relu'),
                    Dense(units=32, activation='relu'),
                    Dense(units=8, activation='relu'),
                    Dense(units=1)])

model.summary()

model.compile(optimizer='Adam', loss='mean_squared_error')
plot_from_model = model.fit(x=dim, y=cm, validation_split=0.1, epochs=200, batch_size=10)

plt.xlabel('Epoch Number')
plt.ylabel('Loss Magnitude')
plt.plot(plot_from_model.history['loss'])
plt.show()

test_data, test_mass = creatingDataSet.data_for_testing()

plot_mass = np.empty((0, 1), float)
plot_predicted_mass = np.empty((0, 1), float)

# todo -> 2 interpreters (abaqus + neural network)
# todo -> class for creating dataset, class for creating and learning model + saving model, analyzing data in next class
# todo -> documentation

for element in test_data:
    plot_mass = np.append(plot_mass, creatingDataSet.mass(element, 2500))
    plot_predicted_mass = np.append(plot_predicted_mass, model.predict([element]))

plt.xlabel('Dimensions - volume [m^3]')
plt.ylabel('Mass [kg]')
plt.plot(test_data, plot_predicted_mass)
plt.plot(test_data, plot_mass)
plt.grid(linestyle='-', linewidth=0.1)
plt.show()
