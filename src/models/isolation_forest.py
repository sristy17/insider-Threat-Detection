from sklearn.ensemble import IsolationForest

def train(X):
    model = IsolationForest(
        n_estimators=200,
        contamination=0.04,
        random_state=42
    )
    model.fit(X)
    return model
