from flask import Flask, request, render_template
import requests
import json
import os
import tracker

app = Flask(__name__)

GEMINI_API_KEY = 'AIzaSyD2UzpYWhaOC-g73BBzmJsqzPRzZN9g30g'
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def search_wikipedia(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "utf8": "",
        "format": "json",
        "srlimit": 10
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    if "query" in data and "search" in data["query"]:
        for item in data["query"]["search"]:
            results.append({
                "title": item["title"],
                "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                "snippet": item["snippet"]# This usually contains HTML spans for highlighting
            })
    return results

def get_ai_summary(query, wiki_results):
    tracker.add_search(query)
    context = tracker.get_ai_context()
    
    # Pre-parse snippets to remove HTML for the prompt to save tokens/make it clean
    wiki_context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in wiki_results[:5]])
    
    prompt = f"""
You are Amisphere AI, a personalized smart search assistant. 
User's current query: '{query}'
User History Profile: {context}

Top 5 Wikipedia results for context:
{wiki_context}

Based on the user's current query, their historical interests, and the provided Wikipedia knowledge, write a highly concise, helpful, and insightful summary.
Focus on answering the user's query directly while also suggesting 1-2 external sites or related topics they might like based on their history. No markdown code blocks, just plain HTML snippets allowed (e.g. <b>, <i>, <br>, <ul>, <li>) so it renders directly nicely.
"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 300}
    }
    
    try:
        res = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        res_data = res.json()
        if "candidates" in res_data and res_data["candidates"]:
            return res_data["candidates"][0]["content"]["parts"][0]["text"].replace("```html", "").replace("```", "")
        return "Amisphere AI is currently analyzing this topic..."
    except Exception as e:
        return f"Amisphere AI is currently unavailable. ({str(e)})"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("index.html")
    
    wiki_results = search_wikipedia(query)
    ai_summary = get_ai_summary(query, wiki_results)
    
    return render_template("results.html", query=query, results=wiki_results, ai_summary=ai_summary)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
