"""
title: Karma Browser Control
author: Karma SADE
version: 1.0.0
description: Allows Karma to control a browser - navigate, click, take screenshots, and extract content.
"""

import subprocess
import json
import os

class Tools:
    def __init__(self):
        pass
    
    def browser_navigate(self, url: str) -> str:
        """
        Navigate the browser to a URL and return the page title.
        Use this to open a webpage and see what's there.
        
        :param url: The URL to navigate to
        :return: The page title and confirmation
        """
        script = '''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("{url}")
    title = page.title()
    page.wait_for_timeout(3000)
    browser.close()
    print(title)
'''.replace("{url}", url)
        try:
            result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return f"Navigated to {url}. Page title: {result.stdout.strip()}"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def browser_screenshot(self, url: str, filename: str = "screenshot.png") -> str:
        """
        Take a screenshot of a webpage and save it.
        
        :param url: The URL to screenshot
        :param filename: Name for the screenshot file
        :return: Path to the saved screenshot
        """
        save_path = os.path.join(r"C:\Users\raest\Documents", filename)
        script = '''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{url}")
    page.wait_for_timeout(2000)
    page.screenshot(path=r"{save_path}")
    browser.close()
    print("saved")
'''.replace("{url}", url).replace("{save_path}", save_path)
        try:
            result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return f"Screenshot saved to: {save_path}"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def browser_get_content(self, url: str) -> str:
        """
        Get the text content of a webpage.
        Use this to read what's on a page.
        
        :param url: The URL to extract content from
        :return: The text content of the page
        """
        script = '''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{url}")
    page.wait_for_timeout(2000)
    content = page.inner_text("body")[:3000]
    browser.close()
    print(content)
'''.replace("{url}", url)
        try:
            result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def browser_get_links(self, url: str) -> str:
        """
        Get all links from a webpage.
        Use this to see what pages are linked.
        
        :param url: The URL to extract links from
        :return: List of links with their text and href
        """
        script = '''
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{url}")
    page.wait_for_timeout(2000)
    links = page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.innerText.trim().substring(0,50), href: e.href})).filter(l => l.text).slice(0,20)")
    browser.close()
    print(json.dumps(links))
'''.replace("{url}", url)
        try:
            result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                links = json.loads(result.stdout.strip())
                formatted = "\n".join([f"- [{l['text']}]({l['href']})" for l in links])
                return f"Links found:\n{formatted}"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def browser_search_google(self, query: str) -> str:
        """
        Search Google and return the top results.
        Use this to search for information online.
        
        :param query: The search query
        :return: Top search results with titles and snippets
        """
        from urllib.parse import quote
        search_url = f"https://www.google.com/search?q={quote(query)}"
        script = '''
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{search_url}")
    page.wait_for_timeout(2000)
    results = page.eval_on_selector_all("div.g", "els => els.slice(0,5).map(e => ({title: e.querySelector('h3')?.innerText || '', link: e.querySelector('a')?.href || '', snippet: e.querySelector('.VwiC3b')?.innerText || ''})).filter(r => r.title)")
    browser.close()
    print(json.dumps(results))
'''.replace("{search_url}", search_url)
        try:
            result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                results = json.loads(result.stdout.strip())
                formatted = "\n\n".join([f"**{r['title']}**\n{r['link']}\n{r['snippet']}" for r in results])
                return f"Google search results for '{query}':\n\n{formatted}"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
