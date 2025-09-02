import pandas as pd
import plotly.graph_objects as go

# 1. Load and process the data from the CSV file, skipping the title row
try:
    df = pd.read_csv('./ad_warn_data/final_warning_report.csv', skiprows=1)
except FileNotFoundError:
    print("Error: 'final_warning_report.csv' not found. Please ensure the file is in the correct directory.")
    exit()

# 2. Rename columns for easier access and clean them
df.rename(columns={
    'Warning issue Time': 'Warning_issue_Time',
    'true-1 / false-0': 'Is_Correct',
    'Warning_Type': 'Warning_Type'
}, inplace=True)
df.columns = df.columns.str.strip()

# 3. Perform calculations
# Ensure required columns exist
required_cols = ['Warning_issue_Time', 'Warning_Type', 'Is_Correct']
if not all(col in df.columns for col in required_cols):
    print(f"Error: Missing one or more required columns: {required_cols}")
    exit()

df['Day'] = df['Warning_issue_Time'].str.split('/').str[0].astype(int)
df_filtered = df[df['Warning_Type'].isin(['Thunderstorm', 'Wind'])]

daily_accuracy = df_filtered.groupby(['Day', 'Warning_Type'])['Is_Correct'].agg(
    correct_warnings='sum',
    total_warnings='count'
).reset_index()

daily_accuracy['Accuracy'] = (daily_accuracy['correct_warnings'] / daily_accuracy['total_warnings']) * 100

# Separate dataframes for easier plotting
df_ts = daily_accuracy[daily_accuracy['Warning_Type'] == 'Thunderstorm']
df_gust = daily_accuracy[daily_accuracy['Warning_Type'] == 'Wind']

# 4. Create the combined bar chart using graph_objects to allow separate color scales
fig = go.Figure()

# Add Thunderstorm trace with its own color scale
fig.add_trace(go.Bar(
    x=df_ts['Day'],
    y=df_ts['Accuracy'],
    name='Thunderstorm',
    text=df_ts['Accuracy'],
    texttemplate='%{y:.1f}%',
    textposition='outside',
    hovertemplate="<b>Thunderstorm</b><br>Day %{x}<br>Accuracy: %{y:.1f}%<extra></extra>",
    marker=dict(
        color=df_ts['Accuracy'],      # Color bars by accuracy value
        colorscale='Blues',           # Use Blues color scale
        showscale=True,               # Show the color bar legend
        colorbar=dict(
            title="TS Accuracy",
            x=1.15,                   # Position color bar to the right
            thickness=15
        )
    )
))

# Add Gust trace with its own color scale
fig.add_trace(go.Bar(
    x=df_gust['Day'],
    y=df_gust['Accuracy'],
    name='Wind',
    text=df_gust['Accuracy'],
    texttemplate='%{y:.1f}%',
    textposition='outside',
    hovertemplate="<b>Wind</b><br>Day %{x}<br>Accuracy: %{y:.1f}%<extra></extra>",
    marker=dict(
        color=df_gust['Accuracy'],      # Color bars by accuracy value
        colorscale='Reds',            # Use Reds color scale
        showscale=True,               # Show the color bar legend
        colorbar=dict(
            title="Gust Accuracy",
            x=1.0,                    # Position color bar to the right
            thickness=15
        )
    )
))

# 5. Style and format the chart
fig.update_layout(
    title_text="Daily Accuracy of Thunderstorm vs. Gust Warnings",
    xaxis_title_text="Day",
    yaxis_title_text="Accuracy (%)",
    barmode='group',
    yaxis_range=[0, 115],
    legend_title_text='Warning Type',
    legend=dict(x=0.01, y=0.98), # Position legend inside the plot
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

# 6. Save the chart to a single HTML file
fig.write_html("combined_accuracy_chart.html")

print("Successfully generated the HTML file: combined_accuracy_chart.html")

