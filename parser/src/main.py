import asyncio
from asyncio import Task
from hub_parser import get_articles, parse_articles
from schema import Hub, HabrArticle
from db import init_db_pool,  get_hubs_from_db, get_articles_from_db, insert_articles


async def schedule_hub(hub: Hub):
    interval = hub.check_period.total_seconds()
    tasks = []
    while True:
        articles_already_exist = await get_articles_from_db(hub.id)
        if articles_already_exist is None:
            print(f'hub {hub.name} error while retrieving articles from db')
            await asyncio.sleep(interval)
        print('hub', hub.name, 'articles', len(articles_already_exist))
        article_links = await get_articles(hub.url)
        print('article_links', article_links)
        if article_links:
            for link in article_links:
                if link not in articles_already_exist:
                    tasks.append(parse_articles(link, hub.id))
        results = await asyncio.gather(*tasks)

        articles = [article for article in results if article is not None]
        print("hub", hub.name, "got", len(articles), "articles")

        await insert_articles(articles)
        await asyncio.sleep(interval)


async def main():
    current_hubs = {}
    current_tasks = {}
    await init_db_pool()

    async def cancel_task(hub_id: int) -> None:
        task_to_cancel = current_tasks.get(hub_id)
        if task_to_cancel and not task_to_cancel.done():
            task_to_cancel.cancel()
            try:
                await task_to_cancel
            except asyncio.CancelledError:
                print(f"Task for hub {hub_id} was cancelled")

    while True:
        hubs = await get_hubs_from_db()
        if hubs:
            print("active hubs", hubs)
            for hub in hubs:
                if hub.id not in current_hubs:
                    task = asyncio.create_task(schedule_hub(hub))
                    current_tasks[hub.id] = task
                    current_hubs[hub.id] = hub
                    await asyncio.sleep(1)
                else:
                    current_hub = current_hubs[hub.id]
                    if (current_hub.check_period != hub.check_period or
                            current_hub.url != hub.url):

                        await cancel_task(hub.id)

                        task = asyncio.create_task(schedule_hub(hub))
                        current_tasks[hub.id] = task
                        current_hubs[hub.id] = hub

        for hub in list(current_hubs.values()):
            if hub not in hubs:
                await cancel_task(hub.id)
                del current_hubs[hub.id]
                del current_tasks[hub.id]

        await asyncio.sleep(60)
        print("current tasks", current_tasks)

if __name__ == "__main__":
    asyncio.run(main())
