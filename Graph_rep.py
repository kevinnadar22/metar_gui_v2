import pandas as pd
import plotly.express as px

# 1. Load and process the data from the updated CSV file, skipping the first row
try:
    df = pd.read_csv('./ad_warn_data/final_warning_report.csv', skiprows=1)
except FileNotFoundError:
    print("Error: 'final_warning_report.csv' not found. Please make sure the file is in the correct directory.")
    exit()


# 2. Rename columns for easier access
df.rename(columns={
    'Warning issue Time': 'Warning_issue_Time',
    'true-1 / false-0': 'Is_Correct',
    'Warning_Type': 'Warning_Type'
}, inplace=True)

# Clean up any potential whitespace issues in column names
df.columns = df.columns.str.strip()


# 3. Perform calculations
# Ensure required columns exist before proceeding
required_cols = ['Warning_issue_Time', 'Warning_Type', 'Is_Correct']
if not all(col in df.columns for col in required_cols):
    print(f"Error: Missing one of the required columns: {required_cols}")
    print(f"Available columns: {df.columns.tolist()}")
    exit()

df['Day'] = df['Warning_issue_Time'].str.split('/').str[0].astype(int)
df_filtered = df[df['Warning_Type'].isin(['Thunderstorm', 'Wind'])]

daily_accuracy = df_filtered.groupby(['Day', 'Warning_Type'])['Is_Correct'].agg(
    correct_warnings='sum',
    total_warnings='count'
).reset_index()

daily_accuracy['Accuracy'] = (daily_accuracy['correct_warnings'] / daily_accuracy['total_warnings']) * 100

# Separate the data for each graph
df_ts = daily_accuracy[daily_accuracy['Warning_Type'] == 'Thunderstorm'].copy()
df_gust = daily_accuracy[daily_accuracy['Warning_Type'] == 'Wind'].copy()


# 4. Create the Thunderstorm accuracy graph
fig_ts = px.bar(
    df_ts,
    x="Day",
    y="Accuracy",
    text="Accuracy",
    labels={"Day": "Day", "Accuracy": "Accuracy (%)"},
    title="Thunderstorm Warning Accuracy per Day",
    color="Accuracy",
    color_continuous_scale="Blues"
)
fig_ts.update_traces(
    texttemplate="%{y:.1f}%",
    textposition="outside",
    hovertemplate="Day %{x}<br>Accuracy: %{y:.1f}%<extra></extra>"
)
fig_ts.update_layout(yaxis_range=[0, 110]) # Range extended slightly for text visibility


# 5. Create the Gust warning accuracy graph
fig_gust = px.bar(
    df_gust,
    x="Day",
    y="Accuracy",
    text="Accuracy",
    labels={"Day": "Day", "Accuracy": "Accuracy (%)"},
    title="Gust Warning Accuracy per Day",
    color="Accuracy",
    color_continuous_scale="Reds"
)
fig_gust.update_traces(
    texttemplate="%{y:.1f}%",
    textposition="outside",
    hovertemplate="Day %{x}<br>Accuracy: %{y:.1f}%<extra></extra>"
)
fig_gust.update_layout(yaxis_range=[0, 110]) # Range extended slightly for text visibility


# 6. Combine both graphs into a single HTML file
with open("accuracy_dashboard.html", "w") as f:
    f.write("<html><head><title>Warning Accuracy Dashboard</title></head><body>")
    f.write(f"<h1 style='font-family: sans-serif; text-align: center;'>Warning Accuracy Dashboard</h1>")
    f.write(fig_ts.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("<hr>") # Add a line to separate the charts
    f.write(fig_gust.to_html(full_html=False, include_plotlyjs=False)) # No need to include JS again
    f.write("</body></html>")

print("Successfully generated the HTML file: accuracy_dashboard.html")
