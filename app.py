import streamlit as st
import tweepy
import pandas as pd
from datetime import datetime, timedelta


# bearer_token = "AAAAAAAAAAAAAAAAAAAAAIsn2QEAAAAA44lphf0zJoJD%2FRizn02mRAHQvJU%3Diu7NvEXdWam223TERYhyHxD0S77o7RiEyOFS2VJuG6zhjM6Mfo"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAJdd2QEAAAAAQdymHmRbgP%2Bo2wqeJxhqtQ9b4HY%3DViWZK2GQUxroQttOv7gdDPeWfEB1uRG1Fc8eCoOg7FmPWjNBqr"

client = tweepy.Client(bearer_token=bearer_token)

st.set_page_config(page_title="X", layout="wide")
st.title("X - Scraper")



keywords_input = st.text_input("Enter keywords" )
max_results = st.slider("Number of tweets to fetch (per keyword)", 10, 200, 25)
search = st.button("Search Tweets")

if search and keywords_input:
    keyword_list = [kw.strip() for kw in keywords_input.split(",")]
    query = " OR ".join(keyword_list)

    start_time = datetime.utcnow() - timedelta(hours=24)

    st.info(f"Fetching tweets from the last 24 hours for {query}")
    try:
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["created_at", "author_id", "text"],
            expansions="author_id",
            user_fields=["username"],
            start_time=start_time.isoformat("T") + "Z"
        )

        users = {u["id"]: u["username"] for u in tweets.includes["users"]} if tweets.includes else {}

        data = []
        for tweet in tweets.data:
            tweet_url = f"https://twitter.com/{users.get(str(tweet.author_id), 'user')}/status/{tweet.id}"
            data.append({
                "Tweet": tweet.text,
                "Author": users.get(str(tweet.author_id), "Unknown"),
                "Posted At": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Link": tweet_url
            })

        df = pd.DataFrame(data)

        st.success(f"Fetched {len(df)} tweets.")
        st.dataframe(df)

        st.markdown("### Clickable Tweet Links")
        for row in data:
            st.markdown(f"- [{row['Author']}]({row['Link']}) — {row['Posted At']}")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "tweets.csv", "text/csv")

    except tweepy.TooManyRequests:
        st.error("rate limit of api used.")
    except Exception as e:
        st.error(f"error: {e}")
