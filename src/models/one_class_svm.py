from sklearn.svm import OneClassSVM

def train(X):
    model = OneClassSVM(
        kernel="rbf",
        nu=0.04,
        gamma="scale"
    )
    model.fit(X)
    return model
