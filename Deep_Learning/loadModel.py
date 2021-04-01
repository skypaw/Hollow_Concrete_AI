from tensorflow.keras.models import load_model


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
        print(self.__model.get_weights())

    def __load_model(self, model_name):
        self.__model = load_model(f'resources\\{model_name}', compile=True, options=None)

    def predict_value(self, value_for_prediction):
        """Predict value method
        =======================

        Method using model to predict expected value of parameter
        """

        predicted_value = self.__model.predict(value_for_prediction)
        return predicted_value

LoadModel('model')

