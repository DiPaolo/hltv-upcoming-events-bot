import datetime
import logging
import time
from typing import List, Optional

import pywebparser.pywebparser as pwp
from hltv_upcoming_events_bot.domain import NewsItem
from hltv_upcoming_events_bot.domain.game_type import GameType

_BASE_URL = {
    GameType.CS2: 'https://www.cybersport.ru/tags/cs2?sort=-publishedAt',
    GameType.DOTA2: 'https://www.cybersport.ru/tags/dota-2?sort=-publishedAt'
}

_logger = logging.getLogger('hltv_upcoming_events_bot.service.cybersport_parser')


def parse_news_to_date(game_type: GameType, date_time: datetime.datetime = None) -> List[NewsItem]:
    _logger.info(f'Parse news until {date_time}')

    if date_time is None:
        date_time = datetime.datetime(1970, 1, 1)

    base_url = _BASE_URL[game_type] if game_type in _BASE_URL else None
    if not base_url:
        _logger.error(f'Failed to parse news: unknown game type (game={game_type})')
        return list()

    parser = pwp.Parser(is_fast=True, delay_func=pwp.gaussian_low_delay, use_cloudflare_bypass=True)
    parser.goto(base_url)

    out = list()

    article_elems = parser.find_elements('//article')
    if len(article_elems) == 0:
        _logger.error('failed to parse news: no any news item found')
        return out

    articles_parser = pwp.Parser(is_fast=True, delay_func=None, use_cloudflare_bypass=True)

    for article_elem in article_elems:
        news_item = _parse_article_elem(article_elem, articles_parser)
        if news_item is None:
            continue

        if news_item.date_time_utc.astimezone(datetime.timezone.utc) < date_time.replace(tzinfo=datetime.timezone.utc):
            break

        news_item.game_type = game_type

        out.append(news_item)

    return out


def _parse_article_elem(elem: pwp.Element, articles_parser: pwp.Parser) -> Optional[NewsItem]:
    #
    # datetime
    #

    link_elem = elem.find_element('./a')
    if link_elem is None:
        _logger.error("failed to parse article: couldn't find link element")
        return None

    date_elem = link_elem.find_element('.//time')
    if date_elem is None:
        _logger.error("failed to parse article: couldn't find time element")
        return None

    date_time_value = date_elem.get_attribute('datetime')
    if not date_time_value:
        _logger.error("failed to parse article: datetime attribute is either missed in the element or it's empty")
        return None

    date_time_utc = datetime.datetime.fromisoformat(date_time_value).astimezone(datetime.timezone.utc)

    #
    # title
    #

    title_elem = elem.find_element(".//h3[@class='title_nSS03']")
    if title_elem is None:
        _logger.error("failed to parse article: couldn't find title element")
        return None

    title = title_elem.text
    if not title:
        _logger.error("failed to parse article: title is empty")
        return None

    #
    # URL
    #

    url = link_elem.get_attribute('href')
    if not url:
        _logger.error("failed to parse article: URL link is either missed in the element or it's empty")
        return None

    # to skip advertisement materials;
    # they are trying to be opened in a new tab;
    # we were stuck at such item (specifically, https://cologne2024.cybersport.ru/)
    target = link_elem.get_attribute('target')
    if target and target == '_blank':
        return None

    #
    # comment count + comment_avg_hour
    #

    comment_count = 0
    comment_avg_hour = 0.0

    comment_count_elem = elem.find_element(".//div[@class='count_7Zuhe']")
    if comment_count_elem is None:
        _logger.warning(f'failed to parse comment count for news item (title={title}): ')
    else:
        comment_count = int(comment_count_elem.text)
        duration = datetime.datetime.now().astimezone(datetime.timezone.utc) - date_time_utc
        duration_hour = duration.seconds / 3600
        comment_avg_hour = comment_count / duration_hour

    #
    # short description
    #

    short_desc = _parse_news_item_page(url, articles_parser)
    if not url:
        _logger.warning("failed to parse article: failed to get short description")

    return NewsItem(game_type=GameType.UNKNOWN, date_time_utc=date_time_utc, title=title, short_desc=short_desc,
                    url=url, comment_count=comment_count, comment_avg_hour=comment_avg_hour)


def _parse_news_item_page(url: str, parser: pwp.Parser) -> Optional[str]:
    """
    Returns: short description or None
    """

    _logger.info(f'Parse news item page {url}')

    try:
        found = False
        for i in range(1, 6):
            parser.goto(url)
            paragraph_elems = parser.find_elements("//div[contains(@class, 'text-content')]/p")
            if len(paragraph_elems) > 0:
                found = True
                break

            _logger.info(f'failed to parse news item (url={url}): no paragraphs found. Wait and retry ({i})...')
            time.sleep(3)

        if not found:
            _logger.error(f'failed to parse news item (url={url}): no paragraphs found')
            return None
    except Exception as ex:
        _logger.error(f"failed to parse news item's paragraphs: {ex}")
        return None

    # takes the first paragraph
    try:
        short_desc = paragraph_elems[0].text
        if not short_desc:
            _logger.error(f"failed to parse news item (url={url}): first paragraph is empty")
            return None
    except:
        _logger.error('!!! short_desc !!!')
        return None

    return short_desc
