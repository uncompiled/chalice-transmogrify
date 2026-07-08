# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-endpoint AWS Lambda service that fetches an XML/RSS feed from a given URL and returns it as JSON. Built on [Chalice](https://github.com/awslabs/chalice), Amazon's serverless microframework for Python.

**Endpoint:** `GET /convert?url=<urlencoded-xml-feed-url>`

## Commands

```bash
pipenv install          # install dependencies
pipenv run pytest       # run all tests
pipenv run pytest tests/test_app.py::test_transform  # run a single test
pipenv run chalice local  # run locally
pipenv run chalice deploy # deploy to AWS Lambda (requires AWS credentials)
```

## Architecture

All application logic lives in [app.py](app.py). There are three functions:

- `index()` — Chalice route handler for `GET /convert`. Validates the `url` query param, calls the two helpers, and raises `BadRequestError` on missing params or invalid XML.
- `get_rss(url)` — fetches the remote URL via `requests` (1s timeout), returns response text or `None` on any error.
- `transform(rss)` — wraps `xmltodict.parse()` to convert XML string to a dict (Chalice serializes it to JSON automatically).

Tests in [tests/test_app.py](tests/test_app.py) import `transform` directly and use parametrized fixtures in [tests/fixtures/](tests/fixtures/) (paired `.xml`/`.rss` + `.json` files for valid cases, malformed XML files for error cases).

Chalice config is in [.chalice/config.json](.chalice/config.json) — the deployment stage is `v1`.
