from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/demo-site", tags=["Controlled Demo Site"])

# In-memory storage for demo published articles
DEMO_ARTICLES: List[Dict[str, Any]] = [
    {
        "id": "demo-1",
        "title": "Initial Product Announcement: Quantum AI Engine v1.0",
        "body": "<p>We are thrilled to announce the official release of our Quantum AI Engine v1.0.</p><p>This groundbreaking technology enables real-time competitor content analysis with near-zero latency.</p>",
        "excerpt": "We are thrilled to announce the official release of our Quantum AI Engine v1.0.",
        "author": "Chief Architect",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80"
    }
]

class PublishDemoArticleRequest(BaseModel):
    title: str = Field(..., example="New Breakthrough in Neural Architecture")
    body: str = Field(..., example="Today we are revealing our latest model benchmark results...")
    author: str = Field("Senior Researcher", example="Dr. Alex Rivera")
    published_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), example="2026-09-27T10:00:00Z")
    image: str = Field("https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80")

@router.get("")
@router.get("/")
def get_demo_blog_home():
    """HTML rendered homepage of the controlled demo blog."""
    articles_html = ""
    for a in DEMO_ARTICLES:
        articles_html += f"""
        <article style="border: 1px solid #333; padding: 20px; border-radius: 8px; margin-bottom: 20px; background: #18181b;">
            <h2 style="margin-top:0;"><a href="/api/demo-site/articles/{a['id']}" style="color: #38bdf8; text-decoration: none;">{a['title']}</a></h2>
            <p style="color: #a1a1aa; font-size: 0.9rem;">By <strong>{a['author']}</strong> | Published <time datetime="{a['published_at']}">{a['published_at']}</time></p>
            <div style="color: #e4e4e7;">{a['body']}</div>
        </article>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo Tech Blog — Official Feed</title>
        <link rel="alternate" type="application/rss+xml" title="Demo RSS Feed" href="/api/demo-site/rss.xml" />
        <link rel="canonical" href="http://127.0.0.1:8000/api/demo-site" />
        <meta name="description" content="Controlled Demo Tech Blog for Real-Time Monitoring Evaluation" />
        <style>
            body {{ font-family: system-ui, sans-serif; background: #09090b; color: #f4f4f5; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
            header {{ border-bottom: 1px solid #27272a; padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ color: #38bdf8; }}
        </style>
    </head>
    <body>
        <header>
            <h1>⚡ Acme Corp Official Tech Blog</h1>
            <p style="color: #9ca3af;">Controlled environment for real-time article publication testing.</p>
        </header>
        <main>
            {articles_html}
        </main>
    </body>
    </html>
    """
    return Response(content=html, media_type="text/html")

@router.get("/articles/{article_id}")
def get_demo_article_page(article_id: str):
    article = next((a for a in DEMO_ARTICLES if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{article['title']} — Acme Tech Blog</title>
        <link rel="canonical" href="http://127.0.0.1:8000/api/demo-site/articles/{article['id']}" />
        <meta property="og:title" content="{article['title']}" />
        <meta property="og:description" content="{article['excerpt']}" />
        <meta property="article:published_time" content="{article['published_at']}" />
        <meta name="author" content="{article['author']}" />
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": "{article['title']}",
            "datePublished": "{article['published_at']}",
            "author": {{ "@type": "Person", "name": "{article['author']}" }}
        }}
        </script>
        <style>
            body {{ font-family: system-ui, sans-serif; background: #09090b; color: #f4f4f5; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
            h1 {{ color: #38bdf8; }}
        </style>
    </head>
    <body>
        <article>
            <h1>{article['title']}</h1>
            <p style="color: #a1a1aa;">By {article['author']} | <time datetime="{article['published_at']}">{article['published_at']}</time></p>
            <hr style="border-color: #27272a;" />
            <div style="font-size: 1.1rem; line-height: 1.6;">{article['body']}</div>
        </article>
    </body>
    </html>
    """
    return Response(content=html, media_type="text/html")

@router.get("/rss.xml")
def get_demo_rss_feed():
    """Dynamic RSS feed endpoint."""
    items_xml = ""
    for a in DEMO_ARTICLES:
        items_xml += f"""
        <item>
            <title><![CDATA[{a['title']}]]></title>
            <link>http://127.0.0.1:8000/api/demo-site/articles/{a['id']}</link>
            <guid>http://127.0.0.1:8000/api/demo-site/articles/{a['id']}</guid>
            <pubDate>{a['published_at']}</pubDate>
            <dc:creator><![CDATA[{a['author']}]]></dc:creator>
            <description><![CDATA[{a['excerpt']}]]></description>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel>
        <title>Acme Tech Blog Demo RSS</title>
        <link>http://127.0.0.1:8000/api/demo-site</link>
        <description>Controlled test RSS feed</description>
        {items_xml}
    </channel>
    </rss>
    """
    return Response(content=rss, media_type="application/rss+xml")

@router.get("/sitemap.xml")
def get_demo_sitemap():
    """Dynamic XML sitemap endpoint."""
    urls_xml = f"""
    <url>
        <loc>http://127.0.0.1:8000/api/demo-site</loc>
        <lastmod>{datetime.now(timezone.utc).isoformat()}</lastmod>
    </url>
    """
    for a in DEMO_ARTICLES:
        urls_xml += f"""
        <url>
            <loc>http://127.0.0.1:8000/api/demo-site/articles/{a['id']}</loc>
            <lastmod>{a['published_at']}</lastmod>
        </url>
        """

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {urls_xml}
    </urlset>
    """
    return Response(content=xml, media_type="application/xml")

@router.post("/publish")
def publish_demo_article(req: PublishDemoArticleRequest):
    """
    Simulates a competitor publishing a new article on their website!
    Updates RSS feed, sitemap.xml, and blog page in real-time.
    """
    article_id = f"demo-{len(DEMO_ARTICLES) + 1}"
    new_item = {
        "id": article_id,
        "title": req.title,
        "body": req.body,
        "excerpt": req.body[:200] + "..." if len(req.body) > 200 else req.body,
        "author": req.author,
        "published_at": req.published_at,
        "image": req.image
    }
    DEMO_ARTICLES.insert(0, new_item) # latest first
    return {
        "status": "published",
        "article_id": article_id,
        "title": req.title,
        "published_at": req.published_at,
        "article_url": f"http://127.0.0.1:8000/api/demo-site/articles/{article_id}",
        "rss_url": "http://127.0.0.1:8000/api/demo-site/rss.xml",
        "sitemap_url": "http://127.0.0.1:8000/api/demo-site/sitemap.xml"
    }
