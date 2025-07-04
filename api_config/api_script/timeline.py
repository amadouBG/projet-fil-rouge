from atproto import Client
from atproto_client.models.app.bsky.feed.get_feed import Params
from api_script.config import BLUESKY_HANDLE, APP_PASSWORD
from api_script.models import SessionLocal, Tweet, Author
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import time

FEED_URI = "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot"

def fetch_public_feed(max_posts=4000, batch_size=100):
    client = Client()
    client.login(BLUESKY_HANDLE, APP_PASSWORD)

    session = SessionLocal()
    total_fetched = 0
    cursor = None

    while total_fetched < max_posts:
        try:
            params = Params(feed=FEED_URI, limit=batch_size, cursor=cursor)
            response = client.app.bsky.feed.get_feed(params)

            feed = response.feed
            cursor = response.cursor

            if not feed:
                break

            for item in feed:
                post = item.post
                bluesky_id = post.uri
                content = post.record.text
                posted_at_str = post.record.created_at
                posted_at = datetime.fromisoformat(posted_at_str) if posted_at_str else None
                author_info = post.author
                author_handle = author_info.handle
                author_did = author_info.did
                display_name = getattr(author_info, 'display_name', '')

                # Vérifier si l'auteur existe déjà
                author = session.query(Author).filter_by(handle=author_handle).first()
                if not author:
                    author = Author(
                        handle=author_handle,
                        display_name=display_name,
                        bluesky_id=author_did
                    )
                    session.add(author)
                    session.commit()

                # Vérifier si le tweet existe déjà
                existing_tweet = session.query(Tweet).filter_by(bluesky_id=bluesky_id).first()
                if existing_tweet:
                    continue

                tweet = Tweet(
                    bluesky_id=bluesky_id,
                    author_id=author.id,
                    content=content,
                    posted_at=posted_at
                )

                session.add(tweet)
                try:
                    session.commit()
                    total_fetched += 1
                except IntegrityError:
                    session.rollback()
                    continue

            if not cursor:
                break

            time.sleep(1)  # Pour respecter les limites de l'API

        except Exception as e:
            print(f"Erreur lors de la récupération du feed : {e}")
            break

    session.close()
    print(f"Total des publications récupérées : {total_fetched}")
