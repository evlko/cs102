import math
import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize

from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:
    idea = f"""
    var i = 0;
        var result = [];
            while (i < {max_count}){{
                if ({offset}+i+100 > {count}){{
                    result.push(API.wall.get({{
                    "owner_id": "{owner_id}",
                    "domain": "{domain}",
                    "offset": "{offset} +i",
                    "count": "{count}-(i+{offset})",
                    "filter": "{filter}",
                    "extended": "{extended}",
                    "fields": "{fields}"
                 }}));
            }}
            result.push(API.wall.get({{
            "owner_id": "{owner_id}",
            "domain": "{domain}",
            "offset": "{offset} +i",
            "count": "{count}",
            "filter": "{filter}",
            "extended": "{extended}",
            "fields": "{fields}"
            }}));
            i = i + {max_count};
        }}
        return result;
    """
    data = {
        "code": idea,
        "access_token": VK_CONFIG["access_token"],
        "v": VK_CONFIG["version"],
    }
    response = session.post("execute", data=data)
    doc = response.json()
    if "error" in doc or not response.ok:
        raise APIError(doc["error"]["error_msg"])
    return doc["response"]["items"]


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """
    result = pd.DataFrame()
    progress = lambda x: x

    for i in progress(range(math.ceil(count / 2500))):
        result = result.append(
            json_normalize(
                get_posts_2500(
                    owner_id, domain, offset, count, max_count, filter, extended, fields
                )
            )
        )
        time.sleep(1)
    return result
