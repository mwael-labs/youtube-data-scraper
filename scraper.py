from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import isodate
import os

# === 1. SETUP ===
API_KEY = "YOUR-API-KEY"
youtube = build("youtube", "v3", developerKey=API_KEY)

# === 2. CONFIG ===
RESULTS_PER_QUERY = 50 # Use 50 for best usage of quotas (50 is max)
MAX_PAGES = 8 # (100 quotas per page)
OUTPUT_FILE = "the_data.csv"
QUERY = "the" # Universal keyword

YT_CATEGORY_IDS = [
    1, 2, 10,
    15, 17, 20, 22, 23,
    24, 25, 26, 27, 28, 29,
 ]


# Write header only if the file doesn't exist
file_exists = os.path.isfile(OUTPUT_FILE)


# Fetch subscriber counts for up to 50 channels

def fetch_subscribers_safe(channel_ids):
    """Return {channelId: subscriberCount or None}"""

    subs_map = {cid: None for cid in channel_ids}  # default None

    if not channel_ids:
        return subs_map

    try:
        request = youtube.channels().list(
            part="statistics",
            id=",".join(channel_ids[:50])
        )
        response = request.execute()

        for item in response.get("items", []):
            cid = item["id"]
            subs = item["statistics"].get("subscriberCount")
            subs_map[cid] = int(subs) if subs is not None else None

    except HttpError as e:
        # If quota exceeded or other error → return None safely
        print("⚠️ Could not fetch subscriber counts for this batch.")
        print("   Error was:", e)
        print("   → Proceeding with subscriber_count = NaN for this batch.")

    return subs_map


# MAIN SCRAPING LOOP

for query in YT_CATEGORY_IDS:
    print(f"\n🔍 Starting category {query}...")
    next_page_token = None

    for page in range(MAX_PAGES):

        # SEARCH REQUEST
        search_req = youtube.search().list(
            part="id,snippet",
            q=QUERY,
            videoCategoryId=query,
            type="video",
            regionCode="US",
            videoDuration="medium", # any, medium or long
            maxResults=RESULTS_PER_QUERY,
            pageToken=next_page_token,
            order="viewCount",
            relevanceLanguage="en"
        )
        search_resp = search_req.execute()

        video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
        next_page_token = search_resp.get("nextPageToken")

        if not video_ids:
            print(f"⚠️ No videos found for category {query}, page {page+1}")
            break

        # VIDEO DETAILS REQUEST
        vids_req = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids)
        )
        vids_resp = vids_req.execute()

        # PARSE VIDEO DATA
        rows = []
        channel_ids_in_batch = []

        for item in vids_resp.get("items", []):
            snip = item["snippet"]
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            try:
                duration = isodate.parse_duration(
                    content.get("duration", "PT0S")
                    ).total_seconds()
            except:
                duration = None

            cid = snip.get("channelId", "")
            cname = snip.get("channelTitle", "")
            channel_ids_in_batch.append(cid)

            rows.append({
                "video_id": item["id"],
                "title": snip.get("title", ""),
                "description": snip.get("description", "")[:500], # 500 characters max (you can increase)   
                "category_id": snip.get("categoryId"),
                "thumbnail": snip.get("thumbnails", {})
                               .get("default", {})
                               .get("url", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "duration_sec": int(duration) if duration else None,
                "publish_date": snip.get("publishedAt", ""),
                "channel_id": cid,
                "channel_name": cname,
                "subscriber_count": None,  # Will be filled after
            })

        # FETCH SUBSCRIBERS FOR THIS BATCH ONLY
        unique_cids = list(set(channel_ids_in_batch))
        subs_map = fetch_subscribers_safe(unique_cids)

        # Inject subscriber counts
        for r in rows:
            r["subscriber_count"] = subs_map.get(r["channel_id"], None)

        # SAVE
        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_FILE, index=False, mode="a", header=not file_exists)
        file_exists = True  # After the first write

        print(f"✅ Saved {len(df)} videos from category {query}, page {page+1}")

        if not next_page_token:
            break

print("\nDONE. All videos saved.")