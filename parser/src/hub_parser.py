import asyncio
import aiohttp
from bs4 import BeautifulSoup
from schema import HabrArticle, Hub
from typing import Union


semaphore = asyncio.Semaphore(10)

habr_main = 'https://habr.com'


async def fetch(url):
    try:
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
    except Exception as e:
        print(f"exception while requesting {url} {e}")


async def get_articles(url: str) -> Union[set, None]:
    html = await fetch(url)
    if html is None:
        return None
    soup = BeautifulSoup(html, 'html.parser')

    articles_list = soup.find_all('article', class_='tm-articles-list__item')
    article_links = set()
    print("articles_list", len(articles_list))
    if articles_list:
        for article in articles_list:
            title = article.find('h2')
            link = title.find('a', href=True)
            article_links.add(habr_main + link['href'])
    else:
        print("articles_list wasn't found")

    return article_links


async def parse_articles(link: str, hub_id: int) -> Union[HabrArticle, None]:
    habr_article = {}
    habr_article['post_link'] = link
    habr_article["hub"] = hub_id
    html = await fetch(link)
    if html is None:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    article_presenter = soup.find('div', class_="tm-article-presenter__header")
    user_info = article_presenter.find('a', class_='tm-user-info__username')
    title = article_presenter.find(attrs={'data-test-id': 'articleTitle'})

    if title:
        article_title = title.get_text().strip()
        print('article_title', article_title)
        habr_article["title"] = article_title
    if user_info:
        author_link = user_info['href']
        autor_name = user_info.get_text(strip=True)
        print("author_link", author_link, "autor_name", autor_name)
        habr_article["author_link"] = habr_main + author_link
        habr_article["author_name"] = autor_name

    datetime_published = article_presenter.find('span', class_='tm-article-datetime-published')
    if datetime_published:
        time_tag = datetime_published.find('time')
        if time_tag and 'datetime' in time_tag.attrs:
            datetime_value = time_tag['datetime']
            habr_article['datetime_published'] = datetime_value
            print("datetime published:", datetime_value)

    print("HABR ARTICLE", habr_article)

    return HabrArticle(**habr_article)


#async def main():
#    res = await get_articles("https://habr.com/ru/hubs/gadgets/articles/")
#    print(res)

#asyncio.run(main())

