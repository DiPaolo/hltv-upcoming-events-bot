import datetime
import logging
import re
from typing import List, Optional

from hltv_upcoming_events_bot import config
import hltv_upcoming_events_bot.domain.match_state
from hltv_upcoming_events_bot.domain.language import Language
from hltv_upcoming_events_bot.domain.match import Match
from hltv_upcoming_events_bot.domain.team import Team
from hltv_upcoming_events_bot.domain.tournament import Tournament
from hltv_upcoming_events_bot.domain.match_stars import MatchStars
from hltv_upcoming_events_bot.domain.match_state import MatchState

# delays in sec with weight
from hltv_upcoming_events_bot.domain.translation import Translation
from pywebparser.pywebparser import Parser


def _parse_match_page_and_get_tournament_url(url: str, parser: Parser = None) -> Optional[Match]:
    parser.goto(url)

    tournament_name_elem = parser.find_element("//div[@class='timeAndEvent']/div[contains(@class, 'event')]/a")
    if not tournament_name_elem:
        logging.error(f"failed to parse match page (url={url}) for getting tournament name: "
                      f"no such element (tournament name)")
        return None

    tournament_url = tournament_name_elem.get_attribute('href')

    #
    # get translations
    #

    translations = list()

    # some elements can be hidden, but that's not a problem as long as
    # they contain 'stream-box' property anyway
    streams_elems = parser.find_elements(
        "//div[@class='streams']/div[contains(@class, 'stream-box') and not(contains(@class, 'hltv-live'))]")

    for stream_elem in streams_elems:
        stream_name_elem = stream_elem.find_element("./div[contains(@class, 'stream-box-embed')]")
        if not stream_name_elem:
            logging.warning(f"failed to parse match page (url={url}) for getting translations")
            continue

        streamer_name = stream_name_elem.text

        country_flag_image_elem = stream_name_elem.find_element("./img")
        country = country_flag_image_elem.get_attribute('alt')

        external_link_name_elem = stream_elem.find_element(".//div[contains(@class, 'external-stream')]/a")
        if external_link_name_elem:
            url = external_link_name_elem.get_attribute('href')
        else:
            # there is no external link; check if embedded link exists (it's usually
            # used for YouTube translations)
            url = stream_name_elem.get_attribute('data-stream-embed')

        translations.append(Translation(streamer_name, Language(country), url))

    return Match(Team(''), Team(''), datetime.datetime.utcnow(), MatchStars.ZERO, Tournament(url=tournament_url),
                 MatchState.UNKNOWN, '', translations=translations)


def _parse_tournament_page(url: str, parser: Parser = None) -> Optional[Tournament]:
    parser.goto(url)

    name_elem = parser.find_element("//h1[@class='event-hub-title']")
    if not name_elem:
        logging.error(f"failed to parse tournament page: no such element (name)")
        return None

    name = name_elem.text

    hltv_id = re.search(r'hltv.org\/events\/(\d+)\/', url)
    if not hltv_id or len(hltv_id.groups()) != 1:
        logging.error(f"failed to parse tournament page: failed to parse URL for getting HLTV ID")
        return None

    return Tournament(name, url, int(hltv_id.groups()[0]))


def get_upcoming_matches(parser: Parser = None) -> List[Match]:
    out = list()

    if not parser:
        parser = Parser(is_fast=True)

    parser.goto(config.BASE_URL)

    match_elem_list = parser.find_elements("//h1[contains(@class, 'todaysMatches')]/following-sibling::div/a")

    # parse each match
    for match_elem in match_elem_list:
        team1_elem = match_elem.find_element(".//div[@class='teamrow'][1]/span")
        team2_elem = match_elem.find_element(".//div[@class='teamrow'][2]/span")
        if not team1_elem or not team2_elem:
            placeholder_elem = match_elem.find_element("./div[@class='placeholderrow']")
            if not placeholder_elem:
                logging.error(
                    f"failed to parse nor team1 or team2 row elements or placeholderrow element: no such element(s)")
            continue

        div_elem = match_elem.find_element(".//div")
        stars_count = int(div_elem.get_attribute('stars'))

        time_elem = match_elem.find_element(".//div/div[@class='middleExtra']")
        if not time_elem:
            # match already in progress
            continue

        # time is stored in microseconds
        time_utc = int(time_elem.get_attribute('data-unix')) / 1000

        match_url = match_elem.get_attribute('href')

        # tournaments will be parsed later as ling as we need to stay at the current page to
        # iterate over all upcoming matches

        out.append(Match(Team(team1_elem.text), Team(team2_elem.text),
                         datetime.datetime.fromtimestamp(time_utc),
                         hltv_upcoming_events_bot.domain.match_stars.MatchStars(stars_count),
                         Tournament(), hltv_upcoming_events_bot.domain.match_state.MatchState.PLANNED, match_url,
                         list()))

    # filling tournaments
    for match in out:
        try:
            parsed_match = _parse_match_page_and_get_tournament_url(match.url, parser)
            if not match:
                continue

            match.tournament = _parse_tournament_page(parsed_match.tournament.url, parser)
            match.translations = parsed_match.translations
        except Exception as ex:
            logging.error(ex)
            out.remove(match)
            continue

    return out
