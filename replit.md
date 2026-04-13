# GitHub Automation

## Overview

Python script that automates GitHub profile updates using card generation API data.

## Stack

- **Python**: 3.12
- **Browser automation**: camoufox (headless Firefox)
- **HTTP**: requests
- **Config**: python-dotenv

## Files

- `main.py` — main automation script
- `cookies.json` — GitHub session cookies
- `.env.example` — environment variable template

## Environment Variables

- `CARD_API_URL` — API endpoint to generate card data
- `GITHUB_USERNAME` — GitHub username to update

## How to Run

```
python main.py
```
