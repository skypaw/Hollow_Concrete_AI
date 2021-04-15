from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import TensorBoard
import tensorflow as tf
from readCSV import read_csv
import numpy as np

import time


class CreatingModel:
    __dim = None
    __res = None
    __res_optimized = None
    __model = None
    __plot_from_model = None
    __tensor_board = None

    __NAME = f"Concrete-parameter-RF{int(time.time())}"

    def __init__(self):
        self.__dim = read_csv('dimensions')
        self.__res = read_csv('results')

        self.__res_optimized = []

        for i in self.__res:
            self.__res_optimized.append(i/1e10)

        self.__res_optimized = np.array(self.__res_optimized)

        print(self.__res_optimized[1])
        print(self.__dim[0])

        self.__tensor_board = TensorBoard(log_dir=f'logs/{self.__NAME}')

        self.optimize_data()
        self.creating_model()
        self.analyzing_model()
        self.save_model()

    def optimize_data(self):
        self.__dim, self.__res_optimized = shuffle(self.__dim, self.__res_optimized)

    def creating_model(self):
        """Creating model method
        ========================

        Method where the model is created. Here are assumed number of layers and neural connections.
        """
        print(self.__dim is np.array)

        self.__model = Sequential([Dense(units=16, input_shape=(6,), activation='relu'),
                                   Dense(units=16),
                                   Dense(units=8, activation='relu'),
                                   Dense(units=8),
                                   Dense(units=4, activation='relu'),
                                   Dense(units=4),
                                   Dense(units=2, activation='relu'),
                                   Dense(units=2),
                                   Dense(units=1)])

        self.__model.summary()

        self.__model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
        self.__plot_from_model = self.__model.fit(x=self.__dim, y=self.__res_optimized, validation_split=0.2,
                                                  epochs=100, batch_size=5,
                                                  callbacks=self.__tensor_board)

    def analyzing_model(self):
        """Analyzing model method
        =========================

        Method responsible for creating a plots of losses in next epochs
        """

        plot_data = self.__plot_from_model.history['loss']

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


CreatingModel()
