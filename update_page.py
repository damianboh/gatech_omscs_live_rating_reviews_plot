# libraries for webscraping, parsing and getting stock data
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import yfinance as yf
import time

# for plotting and data manipulation
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.express as px

# for getting current date and time to print 'last updated'
from datetime import datetime

# Filter data with minimum review count of 5
min_review_count = 5

# Scrape the Course Reviews Data from OMS Central
url = 'https://www.omscentral.com/'

req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})

try:
    response = urlopen(req)   
except:
    time.sleep(10) # if there is an error and request is blocked, do it more slowly by waiting for 10 seconds before requesting again
    response = urlopen(req)  
        
# Read the contents of the file into 'html'
html = BeautifulSoup(response)

# Parse the Course Reviews Data into a Python List
# Find the data in between the final <script> tags in the website
raw = html.find_all("script")[-1]

json_text = raw.text

# Load the relevant part of the data into a Python List
parsed = json.loads(json_text)['props']['pageProps']['courses']

raw_df = pd.DataFrame(parsed)


# Perform Data Cleaning
# The 'codes' column of the courses consists of lists instead of strings, extract the element in the list into a list.
raw_df['code'] = raw_df['codes'].apply(lambda x: x[0])

# The first part of the course code (before the - sign) can be extracted as the department.
raw_df['dept'] = raw_df['code'].apply(lambda x: x.split('-')[0])

# Generate own tag using first letter of each capitalized word in the name as some courses are without tags
raw_df['tag'] = raw_df['name'].apply(lambda x: ''.join([word[0] for word in x.split() if word[0].isupper()]))

# Some courses already have tags stored in the form of a list, for simplicity, extract the first element of the list to as the tag
for i, row in raw_df.iterrows():
    if isinstance(row['tags'], list):
        if len(row['tags']) > 0:
            raw_df.at[i,'tag'] = row['tags'][0]  


df = raw_df[raw_df['reviewCount'] > 0]

# More data cleaning
# distributed computing has a ridiculously high amt of workload
# so it is replaced with the same amount of workload as the second highest one
df.loc[df["tag"] == "DC", 'workload'] = 0 
df.loc[df["tag"] == "DC", 'workload'] = df["workload"].max()

df = df[['name', 'tag', 'dept', 'code', 'description', 'reviewCount', 'rating', 'difficulty', 'workload']]

# Filter data with minimum review count specified above
df_plot = df[df['reviewCount'] >= min_review_count]

# Generate Scatter Plots
# OMSCS Course Rating and Difficulty Plot (size = Review Count, color = Workload)
fig_scatter1 = px.scatter(df_plot, x="difficulty", y="rating", 
                 hover_data=['name', 'reviewCount'], text='tag', size='reviewCount', color='workload')
fig_scatter1.update_traces(textposition='top center')
fig_scatter1.add_vline(x=df_plot["difficulty"].mean(), line_width=0.5, annotation_text = 'Mean Difficulty')
fig_scatter1.add_hline(y=df_plot["rating"].mean(), line_width=0.5, annotation_text = 'Mean Rating')
fig_scatter1.update_layout(
    title="OMSCS Course Rating and Difficulty (size = Review Count, color = Workload)",
    xaxis_title="Difficulty",
    yaxis_title="Rating",
    height=800,
    font=dict(
        size=10
    )
)


# OMSCS Course Workload and Difficulty Plot (size = Review Count, color = Workload)
fig_scatter2 = px.scatter(df_plot, x="difficulty", y="workload", 
                 hover_data=['name', 'reviewCount'], text='tag', size='reviewCount', color='rating')
fig_scatter2.update_traces(textposition='top center')
fig_scatter2.add_vline(x=df_plot["difficulty"].mean(), line_width=0.5, annotation_text = 'Mean Difficulty')
fig_scatter2.add_hline(y=df_plot["workload"].mean(), line_width=0.5, annotation_text = 'Mean Workload')
fig_scatter2.update_layout(
    title="OMSCS Course Workload and Difficulty (size = Review Count, color = Rating)",
    xaxis_title="Difficulty",
    yaxis_title="Workload",
    height=800,
    font=dict(
        size=10
    )
)


# Histogram Plots to Show Distributions of Workload, Rating and Difficulty
fig_hist1 = px.histogram(df_plot, x='workload', nbins=30, title='Workload Distribution')
fig_hist1.update_layout(
    width=800
)

fig_hist2 = px.histogram(df_plot, x='rating', nbins=30, title='Rating Distribution')
fig_hist2.update_layout(
    width=800
)

fig_hist3 = px.histogram(df_plot, x='difficulty', nbins=30, title='Difficulty Distribution')
fig_hist3.update_layout(
    width=800
)

# Correlation Heatmap Between Workload, Rating and Difficulty
fig_corr = px.imshow(df[['rating', 'difficulty', 'workload']].corr(), text_auto = True, title = 'Correlation')


# Generate the Treemap Plot
# group data into sectors at the highest level, breaks it down into industry, and then ticker, specified in the 'path' parameter
# the 'values' parameter uses the value of the column to determine the relative size of each box in the chart
# the color of the chart follows the sentiment score
# when the mouse is hovered over each box in the chart, the negative, neutral, positive and overall sentiment scores will all be shown
# the color is red (#ff0000) for negative sentiment scores, black (#000000) for 0 sentiment score and green (#00FF00) for positive sentiment scores
fig = px.treemap(df, path=[px.Constant("Dow Jones"), 'Sector', 'Industry', 'Symbol'], values='Market Cap',
                  color='Sentiment Score', hover_data=['Company', 'Negative', 'Neutral', 'Positive', 'Sentiment Score'],
                  color_continuous_scale=['#FF0000', "#000000", '#00FF00'],
                  color_continuous_midpoint=0)

fig.data[0].customdata = df[['Company', 'Negative', 'Neutral', 'Positive', 'Sentiment Score']].round(3) # round to 3 decimal places
fig.data[0].texttemplate = "%{label}<br>%{customdata[4]}"

fig.update_traces(textposition="middle center")
fig.update_layout(margin = dict(t=30, l=10, r=10, b=10), font_size=20)

# Get current date, time and timezone to print to the html page
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
timezone_string = datetime.now().astimezone().tzname()

# Generate HTML File with Updated Time and Treemap
with open('dow_jones_live_sentiment.html', 'a') as f:
    f.truncate(0) # clear file if something is already written on it
    title = "<h1>Dow Jones Stock Sentiment Dashboard</h1>"
    updated = "<h2>Last updated: " + dt_string + " (Timezone: " + timezone_string + ")</h2>"
    description = "This dashboard is updated every half an hour with sentiment analysis performed on latest scraped news headlines from the FinViz website.<br><br>"
    code = """<a href="https://medium.com/datadriveninvestor/use-github-actions-to-create-a-live-stock-sentiment-dashboard-online-580a08457650">Explanatory Article</a> | <a href="https://github.com/damianboh/dow_jones_live_stock_sentiment_treemap">Source Code</a>"""
    author = """ | Created by Damian Boh, check out my <a href="https://damianboh.github.io/">GitHub Page</a>"""
    f.write(title + updated + description + code + author)
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn')) # write the fig created above into the html file

