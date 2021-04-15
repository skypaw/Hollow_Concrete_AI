from tensorflow.keras.models import load_model
import numpy as np
from readCSV import read_csv


class LoadModel:
    """Load Model Class
    ===================

    Class responsible for loading learned model from file and doing operations on it.

    Possible operations:
    1. Predict value

    """

    __model = None

    def __init__(self, model_name):
        """Initialization of the class
        ==============================

        Loading model called on creating object of the class
        """

        self.__load_model(model_name)

    def __load_model(self, model_name):
        self.__model = load_model(f'resources\\{model_name}', compile=True, options=None)

    def predict_value(self, value_for_prediction):
        """Predict value method
        =======================

        Method using model to predict expected value of parameter
        """

        predicted_value = self.__model.predict(value_for_prediction)
        return predicted_value


ste = LoadModel('model')

_dim = read_csv('dimensions')
_res = read_csv('results')

i = 0
for f in _dim:
    pred = LoadModel.predict_value(ste, np.array([f]))

    print(pred, _res[i]/1e10)
    i =i+1

