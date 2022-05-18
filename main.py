import os.path

from rss import load, Post
from requests import post
from webhooks import WEBHOOKS
from datetime import timezone
from time import sleep
import click


def make_embed(p: Post):
    content = f'{p.summary}'

    img = p.thumbnail

    return {
        'url': p.link,
        'thumbnail': {
            'url': img,
        },
        'color': 0xefd613,
        'timestamp':
            p.published.astimezone(timezone.utc).isoformat(timespec='milliseconds'),
        'title': p.title,
        'description': content,
        'footer': {
            'text': p.author,
        },
    }


@click.command()
@click.option('--interval', type=click.INT, default=60, help='Inverval kontrol ve vteřinách')
@click.option('--last-post-id', help='Nastaví od kterého posledního postu se má začít posílat')
def cli(interval: int = 60, last_post_id: str = None):
    if last_post_id is None:
        if os.path.exists('.last_report_id'):
            with open('.last_report_id') as f:
                x = f.read().strip()
                if x:
                    last_post_id = x
        else:
            last_post_id = None

    while True:
        posts = load()

        new_posts = []
        for r in posts:
            if r.id == last_post_id:
                break

            new_posts.append(r)

        new_posts.reverse()

        for i in range((len(new_posts) // 10) + (1 if len(new_posts) % 10 > 0 else 0)):
            embeds = []
            for r in new_posts[i * 10:(i + 1) * 10]:
                embeds.append(make_embed(r))

            for wi, webhook in enumerate(WEBHOOKS):
                res = post(
                    url=webhook,
                    json={
                        'content': None,
                        'embeds': embeds,
                    }
                )

                print(f'#{wi}\t{res.status_code}')

        last_post_id = posts[0].id

        with open('.last_report_id', 'w') as f:
            f.write(last_post_id)

        sleep(interval)
    pass


if __name__ == '__main__':
    cli()
    pass
