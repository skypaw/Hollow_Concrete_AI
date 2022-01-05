from sklearn import model_selection
from sklearn.neural_network import MLPRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from readCSV import shuffle_data
from statistics import mean

from joblib import dump

mse = []

tuple_list = [(1024, 8192)]

kroks = [400]
do_csvki = []


for tuple_item in tuple_list:
    for krok in kroks:
        for j in range(10):
            print(f"tuple ={tuple_item}")
            data_to_split = shuffle_data()
            X = data_to_split[:, 1:7]
            y = data_to_split[:, 7:]

            y[:, 0:2] = y[:, 0:2] / 10 ** 10
            y[:, 2:6] = y[:, 2:6] / 10 ** 9
            y[:, 6:8] = y[:, 6:8] / 10 ** 8
            y[:, 8:] = y[:, 8:] / 10 ** 10

            print(y[2])

            X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

            model = MLPRegressor(
                random_state=1, max_iter=krok, hidden_layer_sizes=tuple_item
            )
            model.fit(X_train, y_train)

            # print(y_test[0], model.predict(X_test)[0])
            test = mean_squared_error(y_test, model.predict(X_test))
            print(f"For model {j} i = {krok}")
            print(f"MSE: {test} ")
            # print(model.score(X_test, y_test))
            mse.append(test)

            dump(model, f"testmodel{j}.joblib")
        sum = 0
        for k in mse:
            sum += k

        print(mse)
        print(f"AVG MSE = {sum / len(mse)}")

        do_csv = (tuple_item, krok, sum / len(mse))
        do_csvki.append(do_csv)

        sum = 0
        mse.clear()

        with open("asdf12.txt", "w") as file_text:
            for tekst in do_csvki:
                file_text.write(str(tekst))
                file_text.write("\n")


# X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
# regr = MLPRegressor(random_state=1, max_iter=1000,hidden_layer_sizes=(200,)).fit(X_train, y_train)
# print(X_test[2])
# print(regr.predict(X_test[2].reshape(1,-1)))
# print(regr.score(X_test, y_test))
