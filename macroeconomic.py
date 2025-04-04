# -*- coding: utf-8 -*-
"""Macroeconomic.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yNw3SBCLGml1K83Eal3ZddYqdAbDmsgJ
"""

# Financial News Sentiment Analysis and Market Prediction Dashboard
# Streamlit-based AI Dashboard Code Template
import streamlit as st
st.set_page_config(page_title="Financial AI Dashboard", page_icon="📈", layout="wide")

import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
from sklearn.linear_model import LinearRegression
import shap
import datetime
import warnings

warnings.filterwarnings("ignore")

# Load your dataset
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/eruu-data29/AI-Dashboard/refs/heads/main/Finance-Analysis.csv"
    df = pd.read_csv("https://raw.githubusercontent.com/eruu-data29/AI-Dashboard/refs/heads/main/Finance-Analysis.csv", parse_dates=['Publication Date'])  # Replace with the correct path or URL
    df.sort_values('Publication Date', inplace=True)
    return df

with st.spinner("Loading data..."):
    df = load_data()
# Title
st.title("Financial News Sentiment Analysis and Market Prediction")

# Sidebar Filters
st.sidebar.header("Filters")
min_date = datetime.date(2022, 7, 6)
max_date = datetime.date(2025, 3, 31)
default_start = datetime.date(2022, 7, 13)
default_end = datetime.date(2022, 7, 28)

start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

# Sentiment Filter Options
sentiment_options = {
    "Positive Only": ["positive"],
    "Negative Only": ["negative"],
    "Both": ["positive", "negative"]
}
sentiment_choice = st.sidebar.radio("Select News Sentiment", list(sentiment_options.keys()), index=2)
sentiment_filter = sentiment_options[sentiment_choice]

# Apply Filters
filtered_df = df[
    (df['Publication Date'] >= pd.to_datetime(start_date)) &
    (df['Publication Date'] <= pd.to_datetime(end_date)) &
    (df['News Sentiment'].isin(sentiment_filter))
]
user_input = {}

# Organize UI into Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Indicators",
    "📊 Sentiment & Market",
    "🧠 Word Cloud & Correlation",
    "📉 GDP Forecasting",
    "📊 Event Studies",
    "🔍 Search & Allocation"
])
with tab1:
# 1. Time-Series Plots
    st.subheader("Time-Series of Key Financial Indicators")
    indicators = ['Bond Yield (10Y Treasury)', 'Stock Market Index', 'Crude Oil Prices (USD/Barrel)',
                  'Gold Prices (USD/Oz)', 'Interest Rate (%)', 'Consumer Confidence Index',
                  'Unemployment Rate', 'Foreign Exchange Rate', 'GDP Growth (%)']

    for indicator in indicators:
        fig = px.line(filtered_df, x='Publication Date', y=indicator, title=f"{indicator} Over Time")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
# 2. Sentiment Analysis Plots
    st.subheader("Sentiment Scores Over Time")
    sentiment_metrics = ['News Sentiment Score', 'Speech Sentiment Score']

    for metric in sentiment_metrics:
        fig = px.line(filtered_df, x='Publication Date', y=metric, title=f"{metric} Over Time")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Stock Market Return vs. Twitter Discussions")
    fig = px.bar(
        filtered_df,
        x='Twitter Discussions',
        y='Stock Market Return (%)',
        title='Stock Market Return (%) by Twitter Discussions',
        color='Stock Market Return (%)',  # Optional: adds color variation
        color_continuous_scale='Blues'    # Optional: style the color scale
    )
    st.plotly_chart(fig, use_container_width=True)


with tab3:
# 6. Stock Before vs After News
    st.subheader("Stock Market Before vs. After News")
    fig = px.scatter(filtered_df, x='Stock Market Before News (%)', y='Stock Market After News (%)', trendline='ols')
    st.plotly_chart(fig, use_container_width=True)

# 3. Trending Keywords & Hashtags Word Cloud
    st.subheader("Trending Keywords & Hashtags")
    text = ' '.join(filtered_df['Trending Keywords & Hashtags'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400).generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# 4. Correlation Heatmap
    st.subheader("Correlation Heatmap")
    corr_cols = ['Interest Rate (%)', 'Inflation Rate (%)', 'Stock Market Index', 'VIX Value',
                 'Google Search Trends', 'GDP Growth (%)', 'Consumer Confidence Index',
                 'Crude Oil Prices (USD/Barrel)', 'Gold Prices (USD/Oz)', 'S&P 500 Change (%)']
    corr = filtered_df[corr_cols].select_dtypes(include=['number']).corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

with tab4:
# Forecast Based on User Inputs
    st.subheader("Forecast Based on User Inputs")
    user_input = {}

    predictors = [
        'Consumer Confidence Index', 'Crude Oil Prices (USD/Barrel)',
        'Gold Prices (USD/Oz)', 'S&P 500 Change (%)', 'VIX Value',
        'Foreign Exchange Rate', 'Interest Rate (%)', 'Inflation Rate (%)'
    ]

    for var in predictors:
        numeric_series = pd.to_numeric(df[var], errors='coerce')
        clean_series = numeric_series.dropna()
        if not clean_series.empty:
            user_input[var] = st.slider(
                var,
                float(clean_series.min()),
                float(clean_series.max()),
                float(clean_series.mean())
            )
        else:
            st.warning(f"Variable '{var}' has no valid numeric values.")
            user_input[var] = 0.0  # Default fallback
    X = df[predictors]
    y = df['Predicted_GDP']
    data = X.copy()
    data['target'] = y
    data = data.dropna()
    X_clean = data.drop('target', axis=1)
    y_clean = data['target']
    # Ensure all expected features are in the user input
    for col in X_clean.columns:
        if col not in user_input:
            user_input[col] = 0.0
    user_input_df = pd.DataFrame([user_input])[X_clean.columns]
    model = LinearRegression().fit(X_clean, y_clean)
    predicted_gdp = model.predict(user_input_df)[0]
    st.metric("📊 Predicted GDP Growth", f"{predicted_gdp:.2f}%")

with tab5:
# Event Study Visualization
    st.subheader("📊 Event Study: Market Impact of Unexpected News")
    fig = px.box(filtered_df, x='Event Type', y='VIX Value', title="Market Volatility by Event Type")
    st.plotly_chart(fig, use_container_width=True)

    #shap.initjs()
# 10. SHAP for Interpretability
    st.subheader("SHAP Explanation for Market Forecast")
    explainer = shap.Explainer(model, X_clean)
    shap_values = explainer(X_clean[:100])
    fig, ax = plt.subplots(figsize=(12, 6))
    shap.summary_plot(shap_values, X_clean[:100], show=False)
    st.pyplot(fig, bbox_inches='tight')


# 7. Event Type Impact
    st.subheader("Impact by Event Type")
    economic_vars = ['Foreign Exchange Rate', 'GDP Growth (%)', 'Interest Rate (%)', 'Inflation Rate (%)',
                     'Sector Impact', 'Unemployment Rate', 'Consumer Confidence Index']
    selected_event = st.selectbox("Choose Event Type Variable", economic_vars)
    fig = px.box(filtered_df, x='Event Type', y=selected_event)
    st.plotly_chart(fig, use_container_width=True)

# 8. Pre and Post Event Analysis
    st.subheader("Pre and Post Event Market Analysis")
    st.bar_chart(filtered_df[['Stock Market Before News (%)', 'Stock Market After News (%)']])

# 11. Sentiment Filtering
    st.subheader("Sentiment Score")
    fig = px.histogram(filtered_df, x='News Sentiment Score', color='News Sentiment', nbins=30)
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    # Text Search
    st.subheader("🔍 Search in News")

    # User input for search
    search_query = st.text_input("Enter a keyword to search for news")

    if search_query:
    # Filter dataframe for matching news articles
       results = filtered_df[filtered_df['Full News Article Text'].str.contains(search_query, case=False, na=False)]

       if not results.empty:
           st.success(f"✅ Found {len(results)} matching articles")
           st.dataframe(results[['Publication Date', 'News Source', 'News Sentiment', 'Full News Article Text']].head(), use_container_width=True)
       else:
           st.warning("⚠️ No matching news articles found. Try a different keyword.")

# Asset Allocation Suggestion
    st.subheader("💡 Asset Allocation Suggestion")
    if user_input and 'VIX Value' in user_input:
       if user_input['VIX Value'] > df['VIX Value'].mean():
          st.info("High market uncertainty detected. Consider shifting portfolio weight to Gold.")
       else:
          st.success("Market conditions are relatively stable. Equities and diversified assets recommended.")
    else:
          st.warning("Please adjust variables in the '📉 GDP Forecasting' tab to enable allocation suggestions.")
