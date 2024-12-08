import streamlit as st
import pandas as pd
import feedparser
from textblob import TextBlob

# Function to fetch news
def fetch_news():
    categories = ["Forbes", "TheGuardian", "CBSSports", "YahooSports", "TheMotleyFool", "YahooFinance", "TMZ", "CNBC", "Technology"]
    news_list = []

    for category in categories:
        rss_url = f"https://news.google.com/rss/search?q={category}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            news_list.append({
                'Title': entry.title.strip(),
                'URL': entry.link.strip(),
                'Category': category
            })

    df = pd.DataFrame(news_list)
    df.drop_duplicates(subset=['Title'], inplace=True)
    return df

# Function for sentiment analysis
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.5:
        return 'Positive'
    elif polarity < -0.3:
        return 'Negative'
    else:
        return 'Neutral'

# Streamlit app layout
st.title("Positive News Finder")
st.write("Get the latest news based on your mood. Let's keep it positive! 🌟")

# Mood input
user_mood = st.text_input("How are you feeling today?")
if user_mood:
    user_sentiment = analyze_sentiment(user_mood)
    st.write(f"Your sentiment is: **{user_sentiment}**")

    # Fetch news
    st.write("Fetching the latest news...")
    news_df = fetch_news()

    # Perform sentiment analysis on news titles
    news_df['Sentiment'] = news_df['Title'].apply(analyze_sentiment)

    # News category selection
    categories = news_df['Category'].unique().tolist()
    selected_category = st.selectbox("Choose a news category:", categories)

    if selected_category:
        filtered_news = news_df[news_df['Category'] == selected_category]

        # Apply mood-based filtering
        if user_sentiment == 'Positive':
            st.write(f"Here's the latest {selected_category} news for you:")
        elif user_sentiment in ['Negative', 'Neutral']:
            filtered_news = filtered_news[filtered_news['Sentiment'] == 'Positive']
            st.write(f"Here's some positive {selected_category} news to brighten your day:")

        # Format the table with hyperlinks
        def create_hyperlink(row):
            return f'<a href="{row["URL"]}" target="_blank">Link</a>'

        filtered_news['Link'] = filtered_news.apply(create_hyperlink, axis=1)
        filtered_news = filtered_news[['Title', 'Link']]

        st.markdown(
            filtered_news.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
else:
    st.write("Enter how you're feeling to get started!")
