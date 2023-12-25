import csv
import numpy as np
from sklearn.linear_model import LinearRegression

full_list = []

# Rent, Feet, Years, Dist, Years, Office, Power, Clear, Park, Lot
with open('Sheet1-Table 1.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        full_list.append(row)

    full_list = full_list[2:]


full_list = np.array(full_list, dtype=float)
response = full_list[:, 1]
predictors = full_list[:, 2:][:, [0, 3]]
print(predictors)
print(response)

model = LinearRegression().fit(predictors, response)
r_sq = model.score(predictors, response)
print('coefficient of determination: ', r_sq)
print('intercept: ', model.intercept_)
print('coefficients: ', model.coef_)


# statsmodels advanced linear regression
x = predictors.copy()
y = response.copy()
import statsmodels.api as sm
x = sm.add_constant(x)

print(x)
print(y)

advanced_model = sm.OLS(y, x)
results = advanced_model.fit()

print(results.summary())

# compute VIF
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
