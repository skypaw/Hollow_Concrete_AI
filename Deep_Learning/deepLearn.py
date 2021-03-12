import creatingDataSet
from sklearn.utils import shuffle
import matplotlib.pyplot as plt

import numpy as np

from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense


class CreatingModel:
    __dim = None
    __cm = None
    __model = None
    __plot_from_model = None

    def __init__(self, dim, cm):
        self.__cm = cm
        self.__dim = dim

        self.optimize_data()
        self.creating_model()
        self.analyzing_model()

    def optimize_data(self):
        self.__dim, self.__cm = shuffle(self.__dim, self.__cm)

    def creating_model(self):
        self.__model = Sequential([Dense(units=16, input_shape=(1,), activation='relu'),
                                   Dense(units=32, activation='relu'),
                                   Dense(units=32, activation='relu'),
                                   Dense(units=8, activation='relu'),
                                   Dense(units=1)])

        self.__model.summary()

        self.__model.compile(optimizer='Adam', loss='mean_squared_error')
        self.__model.fit(x=dim, y=cm, validation_split=0.1, epochs=200, batch_size=10)

    def analyzing_model(self):
        plot_data = self.__model.history['loss']

        plt.xlabel('Epoch Number')
        plt.ylabel('Loss Magnitude')
        plt.plot(plot_data)
        plt.show()
        pass

    def save_model(self):
        save_model(
            self.__model,
            'resources\\model',  # todo -> to config
            overwrite=True,
            include_optimizer=True,
            save_format=None,
            signatures=None,
            options=None,
            save_traces=True)
        pass

    def open_model(self):
        # working on model - > object different class

        pass


# raw data
dim, cm = creatingDataSet.data_for_network()
CreatingModel(dim, cm)
