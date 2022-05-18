from dataclasses import dataclass
from datetime import timedelta, datetime
from time import mktime
from enum import Enum
import feedparser


VORTEX_RSS = 'https://www.vortex.cz/feed/'


class SyUpdate:
    class UpdatePeriod(Enum):
        HOURLY = 'hourly'
        DAILY = 'daily'
        WEEKLY = 'weekly'
        MONTHLY = 'monthly'
        YEARLY = 'yearly'
        pass

    period: UpdatePeriod
    frequency: int

    def __init__(self, period, frequency: int):
        self.period = self.UpdatePeriod(period)
        self.frequency = int(frequency)

    def get_timedelta(self) -> timedelta:
        match self.period:
            case self.UpdatePeriod.HOURLY:
                return timedelta(hours=self.frequency)
            case self.UpdatePeriod.DAILY:
                return timedelta(days=self.frequency)
            case self.UpdatePeriod.WEEKLY:
                return timedelta(days=self.frequency * 7)
            case self.UpdatePeriod.MONTHLY:
                return timedelta(days=self.frequency * 30)
            case self.UpdatePeriod.YEARLY:
                return timedelta(days=self.frequency * 365)


@dataclass
class Tag:
    term: str
    scheme: str = None
    label: str = None


@dataclass
class Post:
    id: str
    title: str
    link: str
    author: str
    authors: [str]
    published: datetime
    tags: [Tag]
    summary: str
    thumbnail: str


def load() -> [Post]:
    parser = feedparser.parse(VORTEX_RSS)
    # sy_update = SyUpdate(parser.feed.sy_updateperiod, parser.feed.sy_updatefrequency)
    # last_update = datetime.fromtimestamp(mktime(parser.feed.updated_parsed))

    posts = []
    for e in parser.entries:
        thumbnail = None
        for enclosure in e.enclosures:
            if enclosure['type'].startswith('image/'):
                thumbnail = enclosure['href']
                break

        posts.append(Post(
            id=e.id,
            title=e.title,
            link=e.link,
            author=e.author,
            authors=[a['name'] for a in e.authors],
            published=datetime.fromtimestamp(mktime(e.published_parsed)) + timedelta(hours=1),
            tags=[Tag(term=t['term'], scheme=t['scheme'], label=t['label']) for t in e.tags],
            summary=e.summary,
            thumbnail=thumbnail,
        ))

    posts.sort(key=lambda x: x.published, reverse=True)
    return posts

