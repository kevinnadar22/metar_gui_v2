import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
df = pd.read_csv('ad_warn_data/final_warning_report.csv')

# Data Cleaning and Preparation
# Rename columns for easier access
df.rename(columns={
    'Elements (Thunderstorm/Surface wind & Gust)': 'Elements',
    'Warning issue Time': 'Warning_issue_Time',
    'true-1 / false-0': 'Is_Correct',
    'Accuracy_Percentage': 'Accuracy_Percentage',
    'Warning_Type': 'Warning_Type'
}, inplace=True)

# Extract the day from the 'Warning_issue_Time' column
df['Day'] = df['Warning_issue_Time'].str.split('/').str[0].astype(int)

# Filter for Thunderstorm and Gust warnings (using the 'Warning_Type' column)
df_filtered = df[df['Warning_Type'].isin(['Thunderstorm', 'Wind'])]

# Calculate the daily accuracy for each warning type
daily_accuracy = df_filtered.groupby(['Day', 'Warning_Type'])['Is_Correct'].agg(
    correct_warnings='sum',
    total_warnings='count'
).reset_index()

daily_accuracy['Accuracy'] = (daily_accuracy['correct_warnings'] / daily_accuracy['total_warnings']) * 100

# Pivot the table to have separate columns for Thunderstorm and Gust accuracy
df_pivot = daily_accuracy.pivot(index='Day', columns='Warning_Type', values='Accuracy').reset_index()
df_pivot.rename(columns={'Wind': 'Gust'}, inplace=True)
df_pivot = df_pivot.fillna(0)


# Create the line graph
fig_line = px.line(
    df_pivot,
    x='Day',
    y=['Thunderstorm', 'Gust'],
    title='Daily Accuracy of Thunderstorm and Gust Warnings',
    labels={'Day': 'Day of the Month', 'value': 'Accuracy (%)', 'Warning_Type': 'Warning Type'},
    markers=True
)
fig_line.update_layout(
    legend_title_text='Warning Type'
)
fig_line.write_html("line_graph.html")


# Create the bar chart (histogram)
fig_bar = px.bar(
    daily_accuracy.rename(columns={'Warning_Type': 'Warning Type', 'Accuracy':'Accuracy (%)'}),
    x='Day',
    y='Accuracy (%)',
    color='Warning Type',
    barmode='group',
    title='Daily Accuracy of Thunderstorm and Gust Warnings',
    labels={'Day': 'Day of the Month', 'Accuracy (%)': 'Accuracy (%)'}
)

fig_bar.write_html("bar_chart.html")

print(df_pivot)