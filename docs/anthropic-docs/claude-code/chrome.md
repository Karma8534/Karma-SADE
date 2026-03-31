---
source: https://code.claude.com/docs/en/chrome
scrape_date: 2026-03-23
section: claude-code
---

# Use Claude Code with Chrome (beta)

> Connect Claude Code to your Chrome browser to test web apps, debug with console logs, automate form filling, and extract data from web pages.

Claude Code integrates with the Claude in Chrome browser extension to give you browser automation capabilities from the CLI or the VS Code extension. Build your code, then test and debug in the browser without switching contexts.

Claude opens new tabs for browser tasks and shares your browser's login state, so it can access any site you're already signed into. Browser actions run in a visible Chrome window in real time. When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually.

Note: Chrome integration is in beta and currently works with Google Chrome and Microsoft Edge. Not supported on Brave, Arc, or other Chromium-based browsers. WSL is also not supported.

## Capabilities

* **Live debugging**: read console errors and DOM state, then fix the code that caused them
* **Design verification**: build a UI from a Figma mock, then open it in the browser to verify
* **Web app testing**: test form validation, check visual regressions, or verify user flows
* **Authenticated web apps**: interact with Google Docs, Gmail, Notion, or any app you're logged into
* **Data extraction**: pull structured information from web pages and save it locally
* **Task automation**: automate repetitive browser tasks like data entry or form filling
* **Session recording**: record browser interactions as GIFs

## Prerequisites

* Google Chrome or Microsoft Edge browser
* [Claude in Chrome extension](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) version 1.0.36 or higher
* Claude Code version 2.0.73 or higher
* A direct Anthropic plan (Pro, Max, Teams, or Enterprise)

Note: Not available through Amazon Bedrock, Google Cloud Vertex AI, or Microsoft Foundry.

## Get started in the CLI

**Step 1: Launch Claude Code with Chrome**
```bash
claude --chrome
```

Or enable from within an existing session: `/chrome`

**Step 2: Ask Claude to use the browser**
```text
Go to code.claude.com/docs, click on the search box,
type "hooks", and tell me what results appear
```

Run `/chrome` at any time to check connection status, manage permissions, or reconnect.

### Enable Chrome by default

Run `/chrome` and select "Enabled by default".

Note: Enabling by default increases context usage since browser tools are always loaded.

### Manage site permissions

Site-level permissions are inherited from the Chrome extension. Manage permissions in the Chrome extension settings.

## Example workflows

### Test a local web application

```text
I just updated the login form validation. Can you open localhost:3000,
try submitting the form with invalid data, and check if the error
messages appear correctly?
```

### Debug with console logs

```text
Open the dashboard page and check the console for any errors when
the page loads.
```

### Automate form filling

```text
I have a spreadsheet of customer contacts in contacts.csv. For each row,
go to the CRM at crm.example.com, click "Add Contact", and fill in the
name, email, and phone fields.
```

### Draft content in Google Docs

```text
Draft a project update based on the recent commits and add it to my
Google Doc at docs.google.com/document/d/abc123
```

### Extract data from web pages

```text
Go to the product listings page and extract the name, price, and
availability for each item. Save the results as a CSV file.
```

### Run multi-site workflows

```text
Check my calendar for meetings tomorrow, then for each meeting with
an external attendee, look up their company website and add a note
about what they do.
```

### Record a demo GIF

```text
Record a GIF showing how to complete the checkout flow, from adding
an item to the cart through to the confirmation page.
```

## Troubleshooting

### Extension not detected

1. Verify the Chrome extension is installed and enabled in `chrome://extensions`
2. Verify Claude Code is up to date: `claude --version`
3. Check that Chrome is running
4. Run `/chrome` and select "Reconnect extension"
5. Restart both Claude Code and Chrome

The first time you enable Chrome integration, Claude Code installs a native messaging host configuration file. Restart Chrome to pick up the new configuration if needed.

**Native messaging host configuration file locations:**

For Chrome:
- **macOS**: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Linux**: `~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Windows**: `HKCU\Software\Google\Chrome\NativeMessagingHosts\` in Registry

For Edge:
- **macOS**: `~/Library/Application Support/Microsoft Edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Linux**: `~/.config/microsoft-edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- **Windows**: `HKCU\Software\Microsoft\Edge\NativeMessagingHosts\` in Registry

### Browser not responding

1. Check if a modal dialog is blocking the page — dismiss it manually then tell Claude to continue
2. Ask Claude to create a new tab and try again
3. Restart the Chrome extension by disabling and re-enabling it in `chrome://extensions`

### Connection drops during long sessions

The Chrome extension's service worker can go idle. Run `/chrome` and select "Reconnect extension".

### Windows-specific issues

* **Named pipe conflicts (EADDRINUSE)**: restart Claude Code and close other Claude Code sessions
* **Native messaging host errors**: try reinstalling Claude Code

### Common error messages

| Error | Cause | Fix |
| :--- | :--- | :--- |
| "Browser extension is not connected" | Native messaging host cannot reach the extension | Restart Chrome and Claude Code, then run `/chrome` |
| "Extension not detected" | Extension not installed or disabled | Install or enable in `chrome://extensions` |
| "No tab available" | Claude tried to act before a tab was ready | Ask Claude to create a new tab and retry |
| "Receiving end does not exist" | Extension service worker went idle | Run `/chrome` and select "Reconnect extension" |

## See also

* [Use Claude Code in VS Code](/en/vs-code#automate-browser-tasks-with-chrome)
* [CLI reference](/en/cli-reference): `--chrome` flag
* [Common workflows](/en/common-workflows)
* [Getting started with Claude in Chrome](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome)
