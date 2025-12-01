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
    df = pd.read_csv("data/linguistic_agg_century.csv")
    X = df.copy()
    y = X.pop("attribution_analysis")
    X.pop("taisho_no")
    X.pop("total_length")
    X.pop("century")
    train_X, val_X, train_y, val_y = train_test_split(X, y, random_state = 0)
    model = RandomForestClassifier()
    model.fit(train_X, train_y)
    y_pred = model.predict(val_X)
    print(classification_report(val_y, y_pred))
    print(classification_report(val_y, y_pred))
    report_mi_scores(X, y)

if __name__ == "__main__":
    print("Fitting linguistic model by translator...")
    main()