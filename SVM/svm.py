import sklearn
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
import matplotlib as mpl
import matplotlib.pyplot as plt

def main():
    data = load_iris()
    print(type(data.data))
    # x, y = np.split(data.data, [4], axis = 0)
    x = data.data
    x = x[:, :2] # sample
    y = data.target # label
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state = 1, train_size = 0.6)
    # clf = svm.SVC(C = 0.8, kernel = 'rbf', gamma = 20.0, decision_function_shape = 'ovr')
    clf = DecisionTreeClassifier(criterion = 'gini', min_samples_leaf = 2, min_samples_split = 2)
    clf.fit(x_train, y_train)

    # 0 feature min, max
    x1_min, x1_max = x[:, 0].min(), x[:, 0].max()
    # 1 feature min, max
    x2_min, x2_max = x[:, 1].min(), x[:, 1].max()
    # 1.0e-1j
    x1, x2 = np.mgrid[x1_min:x1_max:200j, x2_min:x2_max:200j]
    grid_test = np.stack((x1, x2), axis = 2)
    grid_test = grid_test.reshape((-1, 2))

    grid_predict = clf.predict(grid_test)

    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    cm_light = mpl.colors.ListedColormap(['#A0FFA0', '#FFA0A0', '#A0A0FF'])
    cm_dark = mpl.colors.ListedColormap(['g', 'r', 'b'])

    # N * 1 => 200 * 200 * 1
    plt.pcolormesh(x1, x2, grid_predict.reshape(x1.shape), cmap = cm_light)
    # plt.scatter(x[:, 0], x[:, 1], c = y, edgecolors = 'k', s = 50, cmap = cm_dark)  # 样本
    plt.scatter(x_test[:, 0], x_test[:, 1], c = y_test, s = 120, facecolors = 'none', cmap = cm_dark)  # 圈中测试集样本
    plt.xlabel('花萼长度', fontsize = 13)
    plt.ylabel('花萼宽度', fontsize = 13)
    plt.xlim(x1_min, x1_max)
    plt.ylim(x2_min, x2_max)
    plt.title('鸢尾花SVM二特征分类', fontsize = 15)
    plt.show()

if __name__ == '__main__':
    main()
