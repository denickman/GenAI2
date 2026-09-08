from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()

"""
Tavily — это поисковый API (Search API), специально заточенный под использование в связке с LLM и AI-агентами. 
По сути это альтернатива обычному Google Search API, но заточенная под то, чтобы результаты сразу удобно скармливать модели.

Что он делает
Принимает поисковый запрос (строку) и возвращает результаты поиска в структурированном виде (JSON) — заголовки, URL, 
сниппеты контента, а иногда и краткий сгенерированный ответ на запрос.
Умеет не просто отдавать ссылки, а сразу вытаскивать и чистить релевантный текст со страниц 
(в отличие от сырых сниппетов Google), чтобы не нужно было отдельно парсить HTML.
Есть режим include_answer — Tavily сам суммирует найденное в короткий ответ.
Поддерживает фильтры: домены, свежесть результатов, глубину поиска (basic / advanced), поиск картинок и т.д.
"""

from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model

queries = ["coffee health benefits", "organic coffee benefits studies", "coffee antioxidants wellness"]


def search_for_articles(queries):
    tavily_search = TavilySearch(
        max_results=5,
        topic="news",
        search_depth="advanced",
        time_range="week",
        include_raw_content=False,
        include_answer=False
    )
    seen_urls = set()
    unique_results = []

    for query in queries:
        results = tavily_search.invoke(query)
        
        for r in results.get("results", []):
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_results.append(r)

    return unique_results


def format_results_for_prompt(results):
    blocks = []
    for r in results:
        blocks.append(
            f"Title: {r.get('title')}\nURL: {r['url']}\nContent: {r.get('content', '')}\n"
        )
    return "\n---\n".join(blocks)


def generate_newsletter(search_results):
    formatted_results = format_results_for_prompt(search_results)

    prompt = f"""
    You are a professional newsletter writer for an organic coffee business.
    Below are the search results for this week's coffee news. Each result includes the content and the 
    source url. 

    SEARCH RESULTS:
    {formatted_results}

    Write the article in markdown format.

    Rules:
    - Focus on the positive news about coffee
    - Provide references using the URLs from the SEARCH RESULTS
    """
    model = init_chat_model("gemini-3-flash-preview", model_provider="google_genai", temperature=0.5)
    response = model.invoke(prompt)
    if isinstance(response.content, list):
        return response.content[0]['text']
    return response.content


output = search_for_articles(queries=queries)

if not output:
    raise ValueError("Не найдено новостей за период — статью писать не из чего")

article = generate_newsletter(output)
print(article)

with open('article.md', 'w') as file:
    file.write(article)