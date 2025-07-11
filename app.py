import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
from openai import OpenAI
import datetime
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download("vader_lexicon")
nltk.download("stopwords")
st.set_page_config(page_title="Live Salesforce Call Note Viewer", page_icon="🔗")

st.title("🔗 Live Salesforce Call Note Viewer")

# Connect to Salesforce
try:
    sf = Salesforce(
        username=st.secrets["salesforce"]["username"],
        password=st.secrets["salesforce"]["password"],
        security_token=st.secrets["salesforce"]["token"],
        domain=st.secrets["salesforce"]["domain"]
    )
except Exception as e:
    st.error("❌ Salesforce connection failed: " + str(e))
    st.stop()

# Run SOQL Query
today = datetime.date.today().isoformat()
query = f"""
SELECT Id, Account_vod__r.Name, Next_Call_Notes_vod__c
FROM Call2_vod__c
WHERE CreatedDate = THIS_MONTH AND Next_Call_Notes_vod__c != null
LIMIT 10
"""

try:
    result = sf.query(query)
    records = result["records"]
    df = pd.json_normalize(records)
    df.rename(columns={"Account_vod__r.Name": "HCP Name", "Next_Call_Notes_vod__c": "Call Note"}, inplace=True)
    st.success(f"✅ Pulled {len(df)} records from Salesforce.")
    st.dataframe(df)
except Exception as e:
    st.error("❌ Error fetching Salesforce data: " + str(e))
    st.stop()

# OpenAI setup
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Add button to summarize
if st.button("🔍 Summarize Call Notes"):
    summaries = []
    keywords_list = []
    sentiments = []

    sia = SentimentIntensityAnalyzer()

    for note in df["Call Note"]:
        # 1. Summarize
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Summarize this medical call note: {note}"}]
            )
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            summary = f"Error: {e}"

        summaries.append(summary)

        # 2. Keywords (3 most frequent non-stopwords)
        words = re.findall(r"\b\w+\b", note.lower())
        stopwords = set(nltk.corpus.stopwords.words("english"))
        filtered = [w for w in words if w not in stopwords]
        freq = nltk.FreqDist(filtered)
        top3 = [kw for kw, _ in freq.most_common(3)]
        keywords_list.append(", ".join(top3))

        # 3. Sentiment
        sentiment_score = sia.polarity_scores(note)
        compound = sentiment_score["compound"]
        if compound > 0.2:
            sentiments.append("Positive")
        elif compound < -0.2:
            sentiments.append("Negative")
        else:
            sentiments.append("Neutral")

    df["Summary"] = summaries
    df["Keywords"] = keywords_list
    df["Sentiment"] = sentiments

    st.success("✅ Summarized successfully.")
    st.dataframe(df)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Summary CSV", data=csv, file_name="summarized_calls.csv", mime="text/csv")
