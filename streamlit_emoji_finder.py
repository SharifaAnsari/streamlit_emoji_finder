# """
# Streamlit Emoji Finder App
# File: streamlit_emoji_finder.py

# How to run:
#     1. Install streamlit if you don't have it:
#          pip install streamlit
#     2. From the folder containing this file run:
#          streamlit run streamlit_emoji_finder.py

# Description:
#     - Multi-language (English + Urdu + Roman-Urdu) emoji search
#     - Uses keyword mapping + fuzzy matching for flexible search
#     - Shows top emoji matches and allows quick copying

# Notes:
#     - The app avoids external dependencies beyond Streamlit and Python stdlib
#     - If you want better fuzzy matching later, consider installing 'rapidfuzz'
# """

# import streamlit as st
# import difflib
# import re
# from typing import List, Tuple

# # ---------- Configuration / Data -------------------------------------------------
# st.set_page_config(page_title="Emoji Finder", page_icon="😊", layout="centered")

# # A keyword -> emoji mapping. Add more keywords as needed.
# # Include English, Urdu (in Urdu script), and common romanizations.
# EMOJI_MAP = {
#     # Happiness / Positive
#     "happy": "😀",
#     "khushi": "😀",
#     "خوش": "😀",
#     "smile": "😄",
#     "muskurahat": "😄",
#     "hasna": "😂",
#     "laugh": "😂",
#     "laughter": "😂",
#     "love": "❤️",
#     "dil": "❤️",
#     "محبت": "❤️",
#     "heart": "❤️",
#     "cool": "😎",

#     # Angry / Annoyed
#     "angry": "😡",
#     "gussa": "😡",
#     "naraz": "😠",
#     "narazgi": "😠",
#     "mad": "😠",

#     # Sad / Crying
#     "sad": "😢",
#     "udasi": "😢",
#     "رو": "😢",
#     "cry": "😢",
#     "crying": "😭",

#     # Surprise / Shock
#     "surprised": "😲",
#     "hairan": "😲",
#     "shock": "😱",

#     # Thumbs / OK
#     "ok": "👌",
#     "thumbs up": "👍",
#     "like": "👍",

#     # Gestures
#     "clap": "👏",
#     "namaste": "🙏",
#     "thank you": "🙏",

#     # Food
#     "pizza": "🍕",
#     "coffee": "☕",
#     "chai": "☕",

#     # Misc
#     "party": "🎉",
#     "birthday": "🎂",
#     "sleep": "😴",
#     "tired": "😴",
#     "thinking": "🤔",
#     "idea": "💡",
#     "money": "💰",
#     "work": "💼",
#     "study": "📚",
# }

# # Build reverse index: tokens -> emoji (many keywords can point to same emoji)
# KEYWORDS = sorted(set(EMOJI_MAP.keys()))

# # Helper functions ---------------------------------------------------------------

# def normalize_text(text: str) -> str:
#     """Lowercase and remove extra spaces."""
#     if not text:
#         return ""
#     text = text.strip().lower()
#     # collapse whitespace
#     text = re.sub(r"\s+", " ", text)
#     return text


# def find_exact_matches(query: str) -> List[Tuple[str, str]]:
#     """Return exact or substring matches (keyword, emoji)."""
#     q = normalize_text(query)
#     matches = []
#     if not q:
#         return matches

#     # direct emoji input? if user already typed emoji, return it
#     if any(ch for ch in q if ch in """😀😄😂❤️😡😠😢😭😲😱👌👍👏🙏🍕☕🎉🎂😴🤔💡💰💼📚"""):
#         # Return the unique emoji characters found
#         uniq = sorted({ch for ch in q if ch.strip()})
#         for ch in uniq:
#             matches.append((ch, ch))
#         return matches

#     # Check for direct keyword match
#     for kw in KEYWORDS:
#         if q == kw or q in kw or kw in q:
#             matches.append((kw, EMOJI_MAP[kw]))

#     return matches


# def find_fuzzy_matches(query: str, n: int = 6, cutoff: float = 0.6) -> List[Tuple[str, float, str]]:
#     """Return fuzzy matches using difflib.get_close_matches and ratio estimate.
#     Each result is (keyword, score (0-1), emoji)
#     """
#     q = normalize_text(query)
#     if not q:
#         return []

#     # Use difflib to find close keywords
#     close = difflib.get_close_matches(q, KEYWORDS, n=n, cutoff=cutoff)

#     results = []
#     for kw in close:
#         # rough score using SequenceMatcher
#         score = difflib.SequenceMatcher(None, q, kw).ratio()
#         results.append((kw, float(score), EMOJI_MAP[kw]))

#     # Also add keywords that occur inside query tokens
#     tokens = q.split()
#     for t in tokens:
#         for kw in KEYWORDS:
#             if t == kw or t in kw or kw in t:
#                 if not any(r[0] == kw for r in results):
#                     score = difflib.SequenceMatcher(None, q, kw).ratio()
#                     results.append((kw, float(score), EMOJI_MAP[kw]))

#     # sort by score desc
#     results.sort(key=lambda x: x[1], reverse=True)

#     # unique by emoji keeping highest score
#     seen = set()
#     uniq_results = []
#     for kw, score, emoji in results:
#         if emoji not in seen:
#             uniq_results.append((kw, score, emoji))
#             seen.add(emoji)
#     return uniq_results[:n]


# # UI -----------------------------------------------------------------------------

# st.title("Emoji Finder — Multi‑Language")
# st.markdown("Type any word or emotion in English, Urdu (اُردو), or Roman-Urdu — the app will suggest matching emojis.")

# with st.form(key="search_form"):
#     query = st.text_input("Search emoji by word or emotion:", value="", placeholder="e.g. khushi, angry, smile, دل, laugh")
#     include_fuzzy = st.checkbox("Enable fuzzy search (typo tolerant)", value=True)
#     submit = st.form_submit_button("Find Emoji")

# if submit:
#     q = normalize_text(query)
#     if q == "":
#         st.info("Please type something to search for an emoji.")
#     else:
#         exact = find_exact_matches(q)
#         fuzzy = find_fuzzy_matches(q) if include_fuzzy else []

#         # Display results — prioritize exact matches
#         if exact:
#             st.subheader("Exact / Direct matches")
#             cols = st.columns(len(exact)) if len(exact) <= 6 else st.columns(6)
#             for i, (kw, emoji) in enumerate(exact):
#                 col = cols[i % len(cols)]
#                 with col:
#                     st.markdown(f"### {emoji} ")
#                     st.caption(f"Matched: {kw}")
#                     if st.button(f"Copy {emoji}", key=f"copy_exact_{i}"):
#                         st.write(f"Copied {emoji} — select and copy if automatic copy isn't supported.")

#         if fuzzy:
#             st.subheader("Fuzzy / Suggested matches")
#             for i, (kw, score, emoji) in enumerate(fuzzy):
#                 st.markdown(f"**{emoji}**  — `{kw}`  (match: {score:.2f})")
#                 if st.button(f"Copy {emoji}", key=f"copy_fuzzy_{i}"):
#                     st.write(f"Copied {emoji} — select and copy if automatic copy isn't supported.")

#         # If nothing found, show helpful suggestions
#         if not exact and not fuzzy:
#             st.warning("No emoji found for that input. Try synonyms like 'happy / khushi / smile' or enable fuzzy search.")
#             st.info("You can also try typing emojis directly or using short English words: e.g., 'love', 'laugh', 'angry'.")

# # Sidebar: Tips and extendability
# with st.sidebar:
#     st.header("How it works")
#     st.write(
#         "The app uses a keyword-to-emoji mapping with optional fuzzy matching (difflib).\n"
#         "You can add more keywords in the EMOJI_MAP dictionary at the top of the file."
#     )
#     st.markdown("---")
#     st.subheader("Add more emojis")
#     st.write("To extend, open the file and add more entries like: `\"pleased\": \"😊\"` or Urdu: `\"خوشی\": \"😊\"`.")
#     st.markdown("---")
#     st.caption("Made with ❤️ — modify the keywords to localize further.")

# # Footer / small credits
# st.markdown("---")
# st.write("**Developer note:** This app uses pure Python stdlib for fuzzy matching. For improved performance and multilingual fuzzy matching, consider adding 'rapidfuzz' and a small translation dictionary or using a lightweight language detection layer.")

# # End of file



"""
Streamlit Emoji Finder App
File: streamlit_emoji_finder.py

How to run:
    1. Install streamlit if you don't have it:
         pip install streamlit
    2. From the folder containing this file run:
         streamlit run streamlit_emoji_finder.py

Description:
    - Multi-language (English + Urdu + Roman-Urdu) emoji search
    - Uses keyword mapping + fuzzy matching for flexible search
    - Shows top emoji matches and allows quick copying
"""

import streamlit as st
import difflib
import re
from typing import List, Tuple

# ---------- Configuration / Data -------------------------------------------------
st.set_page_config(page_title="Emoji Finder", page_icon="😊", layout="centered")

# A keyword -> emoji mapping. Add more keywords as needed.
EMOJI_MAP = {
    # Smiling / Happy
    "smile": "😊",
    "happy": "😄",
    "khushi": "😃",
    "grin": "😁",

    # Sad / Cry
    "sad": "😢",
    "cry": "😭",
    "rona": "😭",
    "dukhi": "😔",

    # Angry
    "angry": "😠",
    "naraz": "😡",
    "ghussa": "😤",

    # Love
    "love": "❤️",
    "heart": "❤️",
    "pyar": "🥰",
    "ishq": "😍",

    # Sorry / Maafi
    "sorry": "🙏",
    "maafi": "🙏",
    "mafii": "🙏",
    "maaf karo": "🥺🙏",
    "please": "🙏",

    # Punch / Marna
    "maro": "👊",
    "marna": "👊",
    "punch": "👊",
    "fight": "🤜🤛",

    # Laugh
    "laugh": "😂",
    "lol": "🤣",
    "hansi": "😂",

    # Surprise / Shock
    "shocked": "😲",
    "wow": "😮",

    # Thinking
    "thinking": "🤔",
    "soch": "🤔",

    # Neutral
    "ok": "😐",
    "neutral": "😐",

    # Thumbs Up / Approval
    "thumbs up": "👍",
    "good": "👍",
    "wah": "👏",

    # Dislike
    "thumbs down": "👎",
    "bura": "👎",

    # Fire
    "fire": "🔥",
    "lit": "🔥",

    # Party / Celebration
    "party": "🥳",
    "celebrate": "🎉",

    # Misc
    "cool": "😎",
    "confused": "😕",
    "question": "❓",
    "idea": "💡"
}

KEYWORDS = sorted(EMOJI_MAP.keys())

# Helper functions ---------------------------------------------------------------

def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip().lower()) if text else ''


def find_exact_matches(query: str) -> List[Tuple[str, str]]:
    q = normalize_text(query)
    matches = []
    if not q:
        return matches

    emoji_chars = ''.join(EMOJI_MAP.values())
    if any(ch in emoji_chars for ch in q):
        uniq = sorted({ch for ch in q if ch.strip()})
        return [(ch, ch) for ch in uniq]

    for kw in KEYWORDS:
        if q == kw or q in kw or kw in q:
            matches.append((kw, EMOJI_MAP[kw]))

    return matches


def find_fuzzy_matches(query: str, n: int = 6, cutoff: float = 0.6) -> List[Tuple[str, float, str]]:
    q = normalize_text(query)
    if not q:
        return []

    close = difflib.get_close_matches(q, KEYWORDS, n=n, cutoff=cutoff)
    results = []

    for kw in close:
        score = difflib.SequenceMatcher(None, q, kw).ratio()
        results.append((kw, score, EMOJI_MAP[kw]))

    tokens = q.split()
    for t in tokens:
        for kw in KEYWORDS:
            if t == kw or t in kw or kw in t:
                if not any(r[0] == kw for r in results):
                    score = difflib.SequenceMatcher(None, q, kw).ratio()
                    results.append((kw, score, EMOJI_MAP[kw]))

    results.sort(key=lambda x: x[1], reverse=True)

    seen = set()
    uniq_results = []
    for kw, score, emoji in results:
        if emoji not in seen:
            uniq_results.append((kw, score, emoji))
            seen.add(emoji)

    return uniq_results[:n]

# UI -----------------------------------------------------------------------------

st.title("Emoji Finder — Multi-Language")
st.markdown("Type any word or emotion in English, Urdu (اُردو), or Roman-Urdu — the app will suggest matching emojis.")

with st.form(key="search_form"):
    query = st.text_input("Search emoji by word or emotion:", value="", placeholder="e.g. khushi, angry, smile, دل, laugh, please")
    include_fuzzy = st.checkbox("Enable fuzzy search (typo tolerant)", value=True)
    submit = st.form_submit_button("Find Emoji")

if submit:
    q = normalize_text(query)
    if not q:
        st.info("Please type something to search for an emoji.")
    else:
        exact = find_exact_matches(q)
        fuzzy = find_fuzzy_matches(q) if include_fuzzy else []

        if exact:
            st.subheader("Exact / Direct matches")
            cols = st.columns(len(exact)) if len(exact) <= 6 else st.columns(6)
            for i, (kw, emoji) in enumerate(exact):
                col = cols[i % len(cols)]
                with col:
                    st.markdown(f"### {emoji} ")
                    st.caption(f"Matched: {kw}")
                    if st.button(f"Copy {emoji}", key=f"copy_exact_{i}"):
                        st.write(f"Copied {emoji} — select and copy if automatic copy isn't supported.")

        if fuzzy:
            st.subheader("Fuzzy / Suggested matches")
            for i, (kw, score, emoji) in enumerate(fuzzy):
                st.markdown(f"**{emoji}**  — `{kw}`  (match: {score:.2f})")
                if st.button(f"Copy {emoji}", key=f"copy_fuzzy_{i}"):
                    st.write(f"Copied {emoji} — select and copy if automatic copy isn't supported.")

        if not exact and not fuzzy:
            st.warning("No emoji found for that input. Try synonyms or enable fuzzy search.")
            st.info("You can also try typing emojis directly or using short English words: e.g., 'love', 'laugh', 'angry'.")

with st.sidebar:
    st.header("How it works")
    st.write("The app uses a keyword-to-emoji mapping with optional fuzzy matching. Add more keywords in EMOJI_MAP to extend functionality.")
    st.markdown("---")
    st.subheader("Add more emojis")
    st.write("Open the file and add entries like: `\"pleased\": \"😊\"` or Urdu: `\"خوشی\": \"😊\"`.")
    st.markdown("---")
    st.caption("Made with ❤️ — modify the keywords to localize further.")

st.markdown("---")
st.write("**Developer note:** This app uses pure Python stdlib for fuzzy matching. For improved performance and multilingual fuzzy matching, consider adding 'rapidfuzz'.")
