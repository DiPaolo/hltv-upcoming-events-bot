import datetime
import logging
from typing import List, Optional

import pywebparser.pywebparser as pwp
from hltv_upcoming_events_bot.domain import NewsItem

_BASE_URL = 'https://www.cybersport.ru/tags/cs-go?sort=internalRating'


def parse_news_to_date(date_time: datetime.datetime = None) -> List[NewsItem]:
    logging.info(f'Parse news until {date_time}')

    if date_time is None:
        date_time = datetime.datetime(1970, 1, 1)

    parser = pwp.Parser(is_fast=True, use_delay=True)
    articles_parser = pwp.Parser(is_fast=True, use_delay=True)
    parser.goto(_BASE_URL)

    out = list()

    article_elems = parser.find_elements('//article')
    for article_elem in article_elems:
        news_item = _parse_article_elem(article_elem, articles_parser)
        if news_item is None:
            continue

        if news_item.date_time_utc.astimezone(datetime.timezone.utc) < date_time.astimezone(datetime.timezone.utc):
            break

        out.append(news_item)

    return out


def _parse_article_elem(elem: pwp.Element, articles_parser: pwp.Parser) -> Optional[NewsItem]:
    #
    # datetime
    #

    link_elem = elem.find_element('./a')
    if link_elem is None:
        logging.error("failed to parse article: couldn't find link element")
        return None

    date_elem = link_elem.find_element('.//time')
    if date_elem is None:
        logging.error("failed to parse article: couldn't find time element")
        return None

    date_time_value = date_elem.get_attribute('datetime')
    if not date_time_value:
        logging.error("failed to parse article: datetime attribute is either missed in the element or it's empty")
        return None

    date_time_utc = datetime.datetime.fromisoformat(date_time_value).astimezone(datetime.timezone.utc)

    #
    # title
    #

    title_elem = elem.find_element(".//h3[@class='title_nSS03']")
    if title_elem is None:
        logging.error("failed to parse article: couldn't find title element")
        return None

    title = title_elem.text
    if not title:
        logging.error("failed to parse article: title is empty")
        return None

    #
    # URL
    #

    url = link_elem.get_attribute('href')
    if not url:
        logging.error("failed to parse article: URL link is either missed in the element or it's empty")
        return None

    #
    # comment count + comment_avg_hour
    #

    comment_count = 0
    comment_avg_hour = 0.0

    comment_count_elem = elem.find_element(".//div[@class='count_7Zuhe']")
    if comment_count_elem is None:
        logging.warning(f'failed to parse comment count for news item (title={title}): ')
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
        logging.warning("failed to parse article: failed to get short description")

    return NewsItem(date_time_utc=date_time_utc, title=title, short_desc=short_desc, url=url,
                    comment_count=comment_count, comment_avg_hour=comment_avg_hour)


def _parse_news_item_page(url: str, parser: pwp.Parser) -> Optional[str]:
    """
    Returns: short description or None
    """

    logging.info(f'Parse news item page {url}')

    parser.goto(url)

    try:
        paragraph_elems = parser.find_elements("//div[contains(@class, 'text-content')]/p")
        if len(paragraph_elems) == 0:
            logging.error(f'failed to parse news item (url={url}): no paragraphs found')
            return None
    except:
        logging.error('!!! paragraph_elems !!!')
        return None

    # takes the first paragraph
    try:
        short_desc = paragraph_elems[0].text
        if not short_desc:
            logging.error(f"failed to parse news item (url={url}): first paragraph is empty")
            return None
    except:
        logging.error('!!! short_desc !!!')
        return None

    return short_desc
