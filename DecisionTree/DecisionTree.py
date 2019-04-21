import sklearn
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier

def main():
    data = load_iris()
    sample = dada.data
    label = data.target
    clf = DecisionTreeClassifier(criterion = 'gini', min_samples_leaf = 2, min_samples_split = 1)
