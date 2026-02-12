"""
Karma Browser Control
Allows Karma to control a browser under user supervision.
Each action requires approval before execution.
"""

import sys
import json
from playwright.sync_api import sync_playwright

class KarmaBrowser:
    def __init__(self, headless=False):
        self.playwright = None
        self.browser = None
        self.page = None
        self.headless = headless
    
    def start(self):
        """Start the browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        print("[OK] Browser started")
        return True
    
    def stop(self):
        """Close the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("[OK] Browser closed")
    
    def navigate(self, url):
        """Navigate to a URL."""
        self.page.goto(url)
        print(f"[OK] Navigated to: {url}")
        return self.page.title()
    
    def click(self, selector):
        """Click an element."""
        self.page.click(selector)
        print(f"[OK] Clicked: {selector}")
    
    def fill(self, selector, text):
        """Fill a text field."""
        self.page.fill(selector, text)
        print(f"[OK] Filled: {selector}")
    
    def get_text(self, selector):
        """Get text content of an element."""
        text = self.page.text_content(selector)
        return text
    
    def screenshot(self, path="screenshot.png"):
        """Take a screenshot."""
        self.page.screenshot(path=path)
        print(f"[OK] Screenshot saved: {path}")
        return path
    
    def get_page_content(self):
        """Get the page's text content."""
        return self.page.inner_text("body")[:2000]
    
    def get_links(self):
        """Get all links on the page."""
        links = self.page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.innerText.trim(), href: e.href})).filter(l => l.text)")
        return links[:20]  # Limit to 20 links
    
    def wait(self, ms=1000):
        """Wait for a specified time."""
        self.page.wait_for_timeout(ms)
    
    def run_interactive(self):
        """Run in interactive mode with approval for each action."""
        print("=" * 50)
        print("Karma Browser Control - Interactive Mode")
        print("=" * 50)
        print("Commands: navigate <url>, click <selector>, fill <selector> <text>")
        print("          screenshot, content, links, quit")
        print("=" * 50)
        
        self.start()
        
        while True:
            try:
                cmd = input("\n[KARMA]> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=2)
                action = parts[0].lower()
                
                if action == "quit" or action == "exit":
                    break
                elif action == "navigate" and len(parts) > 1:
                    title = self.navigate(parts[1])
                    print(f"Page title: {title}")
                elif action == "click" and len(parts) > 1:
                    self.click(parts[1])
                elif action == "fill" and len(parts) > 2:
                    self.fill(parts[1], parts[2])
                elif action == "screenshot":
                    path = parts[1] if len(parts) > 1 else "screenshot.png"
                    self.screenshot(path)
                elif action == "content":
                    print(self.get_page_content())
                elif action == "links":
                    for link in self.get_links():
                        print(f"  [{link['text'][:30]}] -> {link['href'][:60]}")
                elif action == "title":
                    print(f"Title: {self.page.title()}")
                elif action == "url":
                    print(f"URL: {self.page.url}")
                else:
                    print("Unknown command. Try: navigate, click, fill, screenshot, content, links, quit")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] {e}")
        
        self.stop()


def execute_action(action, params):
    """Execute a single browser action (for scripted use)."""
    browser = KarmaBrowser(headless=False)
    browser.start()
    
    result = None
    try:
        if action == "navigate":
            result = browser.navigate(params.get("url"))
        elif action == "screenshot":
            result = browser.screenshot(params.get("path", "screenshot.png"))
        elif action == "content":
            result = browser.get_page_content()
        elif action == "links":
            result = browser.get_links()
        # Add more actions as needed
    finally:
        input("Press Enter to close browser...")
        browser.stop()
    
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Scripted mode: python karma_browser.py navigate https://example.com
        action = sys.argv[1]
        params = {"url": sys.argv[2]} if len(sys.argv) > 2 else {}
        result = execute_action(action, params)
        if result:
            print(json.dumps(result, indent=2) if isinstance(result, (list, dict)) else result)
    else:
        # Interactive mode
        browser = KarmaBrowser(headless=False)
        browser.run_interactive()
