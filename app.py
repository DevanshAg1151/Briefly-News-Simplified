import feedparser
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {
    'Yahoo Finance' : 'https://finance.yahoo.com/news/rssindex',
    'BBC' : 'http://feeds.bbci.co.uk/news/rss.xml',
    'CNN' : 'http://rss.cnn.com/rss/edition.rss',
    'The Guardian' : 'https://www.theguardian.com/world/rss',
    'TechCrunch' : 'http://feeds.feedburner.com/TechCrunch/',
    'Wired' : 'https://www.wired.com/feed/rss',
    'The Verge' : 'https://www.theverge.com/rss/index.xml',
    'Forbes' : 'https://www.forbes.com/most-popular/feed/',
    'Financial Times' : 'https://www.ft.com/rss/home',
    'Bloomberg' : 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
    'Investing.com' : 'https://www.investing.com/rss/news.rss',
    'IGN' : 'https://feeds.ign.com/ign/all',
    'Polygon' : 'https://www.polygon.com/rss/index.xml',
    'Kotaku': 'https://kotaku.com/rss',
    'ESPN' : 'https://www.espn.com/espn/rss/news',
    'Sky Sports' : 'https://www.skysports.com/rss/12040',
    'BBC Sport' : 'http://feeds.bbci.co.uk/sport/rss.xml',
    'NASA' : 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
    'Science Daily' : 'https://www.sciencedaily.com/rss/all.xml'
}

@app.route('/')
def index():
    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feeds = feedparser.parse(feed)
        for entry in parsed_feeds.entries:
            # Handle different possible date formats
            published_time = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_time = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "published"):
                published_time = entry.published
            elif hasattr(entry, "updated"):
                published_time = entry.updated

            articles.append((source, {
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", ""),
                "published": published_time
            }))

    # Sort articles by published date, handling None values
    articles = sorted(articles, key=lambda x: x[1]["published"] or datetime.min, reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template('index.html', articles = paginated_articles, page = page, 
                           total_pages = total_articles // per_page + 1)    


@app.route('/search')
def search():
    query = request.args.get('q')

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feeds = feedparser.parse(feed)
        for entry in parsed_feeds.entries:
            # Handle different possible date formats
            published_time = None
            if hasattr(entry, "published_parsed"):
                published_time = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "published"):
                published_time = entry.published
            elif hasattr(entry, "updated"):
                published_time = entry.updated

            articles.append((source, {
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", ""),  # Handle missing summaries
                "published": published_time
            }))

    results = [article for article in articles if query.lower() in article[1]["title"].lower()]

    return render_template('search_results.html', articles=results, query=query)


if __name__ == '__main__':
    app.run(debug = True)    
