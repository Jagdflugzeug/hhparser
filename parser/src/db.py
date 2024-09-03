import asyncpg
from schema import HabrArticle, Hub
import os
from typing import List, Union, Callable, Optional

pool = None


async def init_db_pool():
    pg_db = os.getenv("PG_DB")
    pg_username = os.getenv("PG_USERNAME")
    pg_password = os.getenv("PG_PASSWORD")
    pg_host = os.getenv("PG_HOST") if os.getenv("PG_HOST") is not None else "postgres"
    pg_port = os.getenv("PG_PORT") if os.getenv("PG_HOST") is not None else 5432
    db_config = {
        'user': pg_username,
        'password': pg_password,
        'database': pg_db,
        'host': pg_host,
        'port': pg_port
    }

    assert pg_db is not None, "Environment variable PG_DB is not set"
    assert pg_username is not None, "Environment variable PG_USERNAME is not set"
    assert pg_password is not None, "Environment variable PG_PASSWORD is not set"
    global pool
    pool = await asyncpg.create_pool(**db_config, max_size=15)


def db_connect(func: Callable[..., any]) -> Callable[..., any]:
    async def wrapper(*args, **kwargs) -> Optional[any]:
        if pool is None:
            raise Exception("Database pool has not been initialized.")

        async with pool.acquire() as conn:
            try:
                return await func(*args, conn=conn, **kwargs)
            except Exception as e:
                print(f"an error occurred: {e}")
                return None

    return wrapper


@db_connect
async def insert_articles(articles: List[HabrArticle], conn: asyncpg.Connection) -> None:
    #print('we are going to insert these articles', articles)
    query = """
          INSERT INTO app_hubarticle (title, hub_id, post_link, author_name, author_link, datetime_published)
          VALUES ($1, $2, $3, $4, $5, $6)
          ON CONFLICT (post_link) DO NOTHING;
          """
    values = [
        (article.title, article.hub, article.post_link, article.author_name, article.author_link,
         article.datetime_published)
        for article in articles
    ]
    await conn.executemany(query, values)


@db_connect
async def get_articles_from_db(hub_id: int, conn: asyncpg.Connection) -> list:
    query = """
           SELECT post_link, hub_id 
           FROM app_hubarticle
           WHERE hub_id = $1;
       """
    rows = await conn.fetch(query, hub_id)

    articles_urls = [row['post_link'] for row in rows]

    return articles_urls


@db_connect
async def get_hubs_from_db(conn: asyncpg.Connection) -> List[Hub]:
    query = """
        SELECT id, name, active, check_period, url 
        FROM app_hub 
        WHERE active = TRUE;
    """

    rows = await conn.fetch(query)

    hubs = [Hub(**dict(row)) for row in rows]

    print("getting hubs", hubs)

    return hubs
