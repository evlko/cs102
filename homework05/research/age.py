import datetime as dt
import statistics
import typing as tp

import dateutil.relativedelta as du
from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    years = []
    friends = get_friends(user_id, fields=["bdate"]).items
    for friend in friends:
        try:
            bdate = dt.datetime.strptime(friend["bdate"], "%d.%m.%Y")  # type: ignore
        except (KeyError, ValueError):
            continue
        years.append(du.relativedelta(dt.date.today(), bdate).years)

    return statistics.median(years) if years else None
