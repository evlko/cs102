import io
import re

import pytest
import requests
from bs4 import BeautifulSoup
from scraputils import *
from bayes import NaiveBayesClassifier
import csv


@pytest.fixture
def page():
    return """<tr class="athing" id="26596092">
        <td class="title"><a href="https://lwn.net/Articles/850218/" class="storylink">First one</a>
        </td></tr> <tr><td class="subtext">
        <span class="score" id="score_26596092">1 point</span>
        <a href="user?id=me" class="hnuser">me</a></td></tr>
        <tr class="athing" id="26596092">
        <td class="title"><a href="https://lwn.net/Articles/850218/" class="storylink">Second</a>
        </td></tr> <tr><td class="subtext">
        <span class="score" id="score_26596092">1 point</span>
        <a href="user?id=me" class="hnuser">me</a></td></tr>
        <tr class="athing" id="26596092">
        <td class="title"><a href="https://lwn.net/Articles/850218/" class="storylink">Last</a>
        </td></tr> <tr><td class="subtext">
        <span class="score" id="score_26596092">1 point</span>
        <a href="user?id=me" class="hnuser">me</a></td></tr>
        <a href="?nextpagelink" class="morelink" rel="next">More</a>
        """


@pytest.fixture()
def fake_page():
    return """<a>There is nothing here, actually</a>"""


@pytest.fixture()
def soup(page):
    return BeautifulSoup(page, "html.parser")


def test_get_soup_works():
    url = "https://google.com"
    soup_actual = get_soup(url)

    assert type(soup_actual) == BeautifulSoup


def test_extract_news_count(soup) -> None:
    """Test to check if "extract_news" func returns exact count of news"""
    result = extract_news(parser=soup)
    print(result)
    assert len(result) == 3


def test_extract_news_wrong_page(fake_page) -> None:
    """Test to check if "extract_news" func returns [] when you parse news from wrong ycombinator page"""
    tmp_soup = BeautifulSoup(fake_page, "html.parser")
    result = extract_news(parser=tmp_soup)
    assert result == []


def test_extract_new_page(soup) -> None:
    """Test to check if "extract_new_page" func returns correct next page link"""
    result = extract_next_page(parser=soup)
    assert result == "?nextpagelink"


def test_extract_new_page_no_button(fake_page) -> None:
    """Test to check if "extract_new_page" func returns correct next page link"""
    with pytest.raises(Exception):
        result = extract_next_page(parser=BeautifulSoup(fake_page, "html.parser"))


def test_get_news_works_properly(soup) -> None:
    """Test to check if "extract_new_page" works properly"""
    result = get_news(soup, n_pages=0)
    assert result == []

    result = get_news(soup, n_pages=1)
    assert len(result) == 3
    assert result[0]["title"] == "First one"


@pytest.fixture()
def data():
    return ["First statement", "Second statement"], ["pos", "neg"]


@pytest.fixture()
def spam_data():
    with io.open("data/SMSSpamCollection", encoding="utf-8") as f:
        data = list(csv.reader(f, delimiter="\t"))
    return data


@pytest.fixture()
def classifier():
    return NaiveBayesClassifier()


def test_alpha_has_default_value_equal_to_1():
    model = NaiveBayesClassifier()
    assert model.alpha == 1


def test_make_words_list():
    words, labels = ["a b c"], ["pos"]
    expected_result = {"pos": {"a": 1, "b": 1, "c": 1}}
    actual_result = NaiveBayesClassifier.make_words_list(words, labels)

    assert expected_result == actual_result

    words, labels = [], []
    expected_result = {}
    actual_result = NaiveBayesClassifier.make_words_list(words, labels)

    assert expected_result == actual_result

    words, labels = ["a b c", "c c c"], ["pos", "neg"]
    expected_result = {"pos": {"a": 1, "b": 1, "c": 1}, "neg": {"c": 3}}
    actual_result = NaiveBayesClassifier.make_words_list(words, labels)

    assert expected_result == actual_result


def test_make_classes_list():
    classes = ["pos", "neg", "pos", "neg"]
    expected_result = {"pos": 2 / 4, "neg": 2 / 4}
    actual_result = NaiveBayesClassifier.make_classes_list(classes)

    assert expected_result == actual_result

    classes = []
    expected_result = {}
    actual_result = NaiveBayesClassifier.make_classes_list(classes)

    assert expected_result == actual_result


def test_count_entries():
    data = {"pos": {"a": 1, "b": 1, "c": 1}, "neg": {"c": 3}}
    expected_result = 3
    actual_result = NaiveBayesClassifier.count_entries(data)

    assert expected_result == actual_result

    data = {"pos": {}, "neg": {}}
    expected_result = 0
    actual_result = NaiveBayesClassifier.count_entries(data)

    assert expected_result == actual_result

    data = {}
    expected_result = 0
    actual_result = NaiveBayesClassifier.count_entries(data)

    assert expected_result == actual_result


def test_fit(data, classifier):
    model = classifier
    X, y = data
    model.fit(X, y)

    assert model._d == 3
    assert model._words_count == {
        "pos": {"first": 1, "statement": 1},
        "neg": {"second": 1, "statement": 1},
    }
    assert model._class_freq == {"pos": 0.5, "neg": 0.5}


def test_predict(data, classifier):
    model = classifier
    X, y = data
    model.fit(X, y)

    statement = "First"
    assert model.predict(statement) == "pos"

    statement = "Second"
    assert model.predict(statement) == "neg"


def test_score(spam_data, classifier):
    model = classifier
    y, X = zip(*spam_data)
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]

    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)

    assert score >= 0.8


def test_bayes_classifier(spam_data):
    model = NaiveBayesClassifier()
    y, X = zip(*spam_data)
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]

    model.fit(X_train, y_train)
    assert model.predict("Hello, how are you?") == "ham"

    score = model.score(X_test, y_test)
    assert score >= 0.8
