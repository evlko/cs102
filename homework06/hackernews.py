import typing as tp

from bottle import route, run, template, request, redirect

from scraputils import get_news
from db import News, get_session, engine, update_label, reload_news, extract_all_news_from_db
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = get_session(engine)
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@tp.no_type_check
@route("/add_label/")
def add_label() -> None:
    s = get_session(engine=engine)
    label = request.query["label"]
    id = request.query["id"]
    update_label(session=s, id=id, label=label)
    redirect("/news")


@tp.no_type_check
@route("/update")
def update_news() -> None:
    s = get_session(engine)
    reload_news(s)
    redirect("/news")


@tp.no_type_check
@route("/classify")
def recommendations():
    s = get_session(engine=engine)

    labeled_news = s.query(News).filter(News.label != None).all()
    unlabeled_news = s.query(News).filter(News.label == None).all()
    model = NaiveBayesClassifier()

    X: tp.List[str] = []
    y: tp.List[str] = []

    for article in labeled_news:
        X.append(article.title)
        y.append(article.label)

    model.fit(X, y)

    for article in unlabeled_news:
        prediction = model.predict(article.title)
        article.prediction = prediction

    s.commit()

    news = extract_all_news_from_db(session=s)
    return template("news_template", rows=news)


if __name__ == "__main__":
    run(host="localhost", port=8080)
