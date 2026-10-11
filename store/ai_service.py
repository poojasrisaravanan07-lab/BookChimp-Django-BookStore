"""
Google Gemini API integration used to generate a short, engaging
summary/overview for a given book title + author.

To enable this feature:
1. Get a free API key from https://aistudio.google.com/app/apikey
2. Set it as the GEMINI_API_KEY environment variable before starting the
   server, e.g.:
       export GEMINI_API_KEY="your_key_here"      (Mac/Linux)
       set GEMINI_API_KEY=your_key_here            (Windows)
3. Restart the Django dev server.

If no key is configured, a friendly placeholder summary is returned
instead so the site keeps working out of the box.
"""

import json
import requests
from django.conf import settings

REQUEST_TIMEOUT = 12  # seconds


def _fallback_summary(book):
    return (
        f"\u201c{book.title}\u201d by {book.author} is a highly rated title in the "
        f"{book.category.name if book.category else 'General'} category. "
        "Add your GEMINI_API_KEY in the environment to unlock live AI-generated "
        "summaries for every book on the site."
    )


def get_ai_summary(book):
    """
    Returns an AI-generated summary for the given Book instance.
    Falls back gracefully to a static message if the API key is missing
    or the request fails for any reason.
    """
    if book.ai_summary:
        return book.ai_summary

    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        return _fallback_summary(book)

    prompt = (
        f"Write a short, engaging, spoiler-free book summary (max 80 words) "
        f"for the book '{book.title}' written by {book.author}. "
        f"Category: {book.category.name if book.category else 'General'}. "
        "Write it like an enticing back-cover blurb for an online bookstore."
    )

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(
            f"{settings.GEMINI_API_URL}?key={api_key}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        ).strip()

        if text:
            # Cache it on the model so we don't call the API again.
            book.ai_summary = text
            book.save(update_fields=["ai_summary"])
            return text

        return _fallback_summary(book)

    except Exception:
        # Network issue, bad key, quota exceeded, etc. Fail silently
        # with a friendly fallback rather than breaking the page.
        return _fallback_summary(book)
