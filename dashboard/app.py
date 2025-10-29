import os
import streamlit as st
import httpx
from datetime import datetime

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def api_get(path, params=None):
    url = f"{API_BASE}{path}"
    r = httpx.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


st.set_page_config(page_title="KidsSmart+", layout="wide")
st.title("KidsSmart+ — Educational Program Intelligence Platform")

tabs = st.tabs(["Search & Filter", "Map View", "Insights", "Data Export", "Admin & Audit"])

with tabs[0]:
    st.subheader("Search & Filter")
    cols = st.columns(6)
    q = cols[0].text_input("Query")
    category = cols[1].selectbox("Category", ["", "Language & Literature", "Early Childhood Education"]) or None
    city = cols[2].text_input("City") or None
    price_free = cols[3].selectbox("Free", ["Any", "Free", "Paid"]) 
    price_free_val = None if price_free=="Any" else (True if price_free=="Free" else False)
    online = cols[4].selectbox("Mode", ["Any", "Online", "In-person"]) 
    online_val = None if online=="Any" else (True if online=="Online" else False)
    size = cols[5].selectbox("Page size", [10, 20, 50], index=1)
    params = dict(q=q or None, category=category, city=city, price_free=price_free_val, online=online_val, size=size)
    data = api_get("/programs", {k:v for k,v in params.items() if v is not None})
    st.caption(f"{data['total']} results")
    for item in data["items"]:
        with st.expander(item["title"]):
            st.write(item.get("description_text") or "")
            meta = st.columns(4)
            meta[0].markdown(f"**Source:** {item['source']}")
            meta[1].markdown(f"**City:** {item.get('city') or '-'}")
            meta[2].markdown(f"**When:** {item.get('start_datetime') or '-'}")
            meta[3].markdown(f"**Tags:** {', '.join(item.get('tags') or [])}")
            st.markdown(f"[Open]({item['source_url']})")

with tabs[1]:
    st.subheader("Map View")
    params = dict(size=200)
    data = api_get("/programs", params)
    items = data.get("items", [])
    import pandas as pd
    points = [
        {"lat": it.get("lat"), "lon": it.get("lon"), "title": it.get("title")}
        for it in items
        if it.get("lat") is not None and it.get("lon") is not None
    ]
    if points:
        df = pd.DataFrame(points)
        st.map(df, latitude="lat", longitude="lon")
    else:
        st.info("No geocoded items yet. Run ETL or enable geocoding.")

with tabs[2]:
    st.subheader("Insights")
    s = api_get("/stats")
    st.json(s)

with tabs[3]:
    st.subheader("Data Export")
    q = st.text_input("Filter query (optional)")
    data = api_get("/programs", {"q": q or None, "size": 100})
    items = data.get("items", [])
    import pandas as pd, json
    df = pd.DataFrame(items)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, file_name="kidssmart_export.csv", mime="text/csv")
    st.download_button("Download JSON", json.dumps(items, indent=2).encode("utf-8"), file_name="kidssmart_export.json", mime="application/json")

with tabs[4]:
    st.subheader("Admin & Audit")
    st.caption("Trigger ETL run (requires admin JWT in Authorization header — set via environment or proxy)")
    st.code("curl -X POST http://localhost:8000/ingest/run -H 'Authorization: Bearer <ADMIN_JWT>'")
    st.markdown("---")
    st.subheader("Provenance & Diffs")
    program_id = st.text_input("Program ID for snapshots/diff")
    if program_id:
        try:
            snaps = api_get(f"/programs/{program_id}/snapshots")
            st.write(snaps)
            diff = api_get(f"/programs/{program_id}/diff")
            st.text_area("Diff (last two snapshots)", diff.get("diff", ""), height=200)
        except Exception as e:
            st.error(str(e))

# Footer displayed on all tabs/pages
st.markdown(
    """
    <style>
    .ks-footer {position: fixed; left: 0; bottom: 0; width: 100%;
                background: rgba(255,255,255,0.8); color: #444;
                text-align: center; padding: 8px 12px; z-index: 1000;}
    </style>
    <div class="ks-footer">all rights reserved Mohamed Imaad Muhinudeen and kavin nathakumar</div>
    """,
    unsafe_allow_html=True,
)
