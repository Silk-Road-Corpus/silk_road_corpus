"""Use linguistics data with a RandomForestClassifier to try to predict translator.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


def report_mi_scores(X, y):
    mi_scores = mutual_info_classif(X, y)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    mi_scores = mi_scores.sort_values(ascending=False)
    print("Mutual information:\n")
    print(mi_scores[::3])

def main():
    df = pd.read_csv("data/linguistic_by_translator.csv")

    # Separate target and features
    y = df["attribution_analysis"].astype(str)
    X = df.drop(columns=["attribution_analysis", "length_average"])

    # Ensure all feature data is numeric
    X = X.apply(pd.to_numeric, errors='coerce')

    # Align X and y and drop NaNs
    data = pd.concat([X, y], axis=1).dropna()
    y = data.pop("attribution_analysis")
    X = data

    train_X, val_X, train_y, val_y = train_test_split(X, y, random_state = 0)
    model = RandomForestClassifier()
    model.fit(train_X, train_y)
    y_pred = model.predict(val_X)
    print(classification_report(val_y, y_pred))
    y_encoded, _ = pd.factorize(y)
    report_mi_scores(X, y_encoded)

if __name__ == "__main__":
    print("Fitting linguistic model by translator...")
    main()