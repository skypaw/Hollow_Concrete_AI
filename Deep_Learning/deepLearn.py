from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import TensorBoard

from readCSV import shuffle_data
import numpy as np
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

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
        data_to_split = shuffle_data()
        self.__dim = data_to_split[:, 1:7]
        self.__res = data_to_split[:, 7:]

        self.__tensor_board = TensorBoard(log_dir=f'logs/{self.__NAME}')

        self.creating_model()
        # self.estimator()
        # self.save_model()

    def creating_model(self):
        """Creating model method
        ========================

        Method where the model is created. Here are assumed number of layers and neural connections.
        """
        print(self.__dim is np.array)

        self.__model = Sequential([Dense(units=32, input_shape=(6,), activation='relu'),
                                   Dense(units=16, activation='relu'),
                                   Dense(units=10), ])

        self.__model.summary()

        self.__model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
        self.__plot_from_model = self.__model.fit(x=self.__dim, y=self.__res, validation_split=0.25,
                                                  epochs=1000, batch_size=100,
                                                  callbacks=self.__tensor_board)




        # print(self.__model.get_weights())
        return self.__model

    def estimator(self):
        estimator = KerasRegressor(build_fn=self.creating_model, epochs=10, batch_size=1100, verbose=0)
        kfold = KFold(n_splits=10)
        results = cross_val_score(estimator, self.__dim, self.__res, cv=kfold)
        print(results.mean())

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


if __name__ == '__main__':
    CreatingModel()
