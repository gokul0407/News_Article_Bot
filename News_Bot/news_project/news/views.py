import requests
from django.shortcuts import render
from newspaper import Article
import pyttsx3
import time

NEWS_API_KEY = '6e5beb0b986942439f884ccaa40833c7'

def get_top_headlines(limit=5):
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'ok' and data['totalResults'] > 0:
        return [article['url'] for article in data['articles'][:limit]]
    else:
        raise Exception('Failed to fetch top headlines')

def scrape_article(article_url):
    article = Article(article_url)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            article.download()
            article.parse()
            article.nlp()
            return article.text, article.summary, article.keywords
        except Exception as e:
            print(f'Attempt {attempt + 1} to scrape {article_url} failed: {e}')
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                raise e

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def news_list(request):
    articles_data = []
    try:
        article_urls = get_top_headlines()
        for index, article_url in enumerate(article_urls):
            text, summary, keywords = scrape_article(article_url)
            articles_data.append({
                'url': article_url,
                'text': text,
                'summary': summary,
                'keywords': keywords,
            })
    except Exception as e:
        return render(request, 'news/error.html', {'error': str(e)})

    return render(request, 'news/news_list.html', {'articles': articles_data})
