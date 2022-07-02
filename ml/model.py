import re
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import KFold, cross_val_score

from db import db

clf = LogisticRegression(random_state=0)

# metas = db.meta.find({'is_rent': {"$exists": True}})
# metas = db.meta.find({'is_rent_short': {"$exists": True}})
metas = db.meta.find({'is_office': {"$exists": True}})


def normalize(text):
    text = text.lower()
    text = re.sub("[(),]+•", " ", text)
    return text


X = []
y = []
metas = list(metas)
for meta in metas:
    X.append(normalize(meta["data"]))
    # y.append(meta["is_rent"])
    # y.append(meta["is_rent_short"])
    y.append(meta["is_office"])

vectorizer = TfidfVectorizer(analyzer='word', min_df=5, max_df=0.9)
X = vectorizer.fit_transform(X)

clf.fit(X, y)


def predict(text):
    text = normalize(text)
    x = vectorizer.transform([text])
    return dict(zip(clf.classes_, clf.predict_proba(x)[0]))


# def check():
#     global y
#     y = np.array(y)
#     sc = cross_val_score(clf, X, y, scoring="roc_auc")
#     print("AUC: %0.2f (+/- %0.2f)" % (sc.mean(), sc.std() * 2))
#
# check()
