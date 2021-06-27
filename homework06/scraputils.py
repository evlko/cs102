import typing as tp

import requests
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema


def get_soup(url: str = "https://news.ycombinator.com/newest") -> BeautifulSoup:
    try:
        r = requests.get(url)
    except MissingSchema:
        r = requests.get("http://" + url)
    return BeautifulSoup(r.text, "html.parser")


def extract_news(parser: BeautifulSoup) -> tp.List[tp.Dict[str, tp.Union[int, str]]]:
    news_list: tp.List[tp.Dict[str, tp.Union[int, str]]] = []
    links = parser.select(".storylink")
    subtext = parser.select(".subtext")
    for pos, item in enumerate(links):
        title = item.getText()
        href = item.get("href", None)
        if str(href).startswith("item"):
            href = "https://news.ycombinator.com/" + href
        points = int(subtext[pos].select(".score")[0].getText().split()[0])
        user = subtext[pos].select(".hnuser")[0].getText()
        if user is None:
            user = "None"
        news_list.append({"title": title, "link": href, "points": points, "author": user})
    return news_list


def extract_next_page(parser: BeautifulSoup) -> str:
    link = parser.select(".morelink")[0]["href"]
    if link is None:
        raise Exception("Parsed all news")
    return str(link[link.index("?") :])


def get_news(parser: BeautifulSoup, n_pages: int = 1) -> tp.List[tp.Dict[str, tp.Union[int, str]]]:
    news: tp.List[tp.Dict[str, tp.Union[int, str]]] = []
    while n_pages:
        print(f"Collecting data from page: {n_pages}")
        news_list = extract_news(parser)
        next_page = extract_next_page(parser)
        url = "https://news.ycombinator.com/newest" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
