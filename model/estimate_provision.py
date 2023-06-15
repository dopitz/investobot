import numpy as np
from sklearn.linear_model import LinearRegression

X = np.array([97.84, 195.68, 397.48, 501.43, 1002.86, 1999.6 , 3002.46, 3999.21]).reshape(-1, 1)
Y = np.array([ 5.17,   5.44,   5.99,   6.5 ,    8.1 ,   11.82,   14.47,   17.66])

model = LinearRegression()
model.fit(X, Y)

def estimate_cost(value):
    return model.predict([[value]])[0]