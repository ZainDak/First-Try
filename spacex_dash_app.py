# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    html.Br(),

    # Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # Slider for payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: str(i) for i in range(min_payload, max_payload + 1, 5000)},
        value=[min_payload, max_payload]
    ),
    
    # Scatter chart for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df['class'].value_counts()
        values = [success_counts.get(0, 0), success_counts.get(1, 0)]
        title = "Total Launch Success"
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts()
        values = [success_counts.get(0, 0), success_counts.get(1, 0)]
        title = f"Success vs Failure for {entered_site}"

    names = ['Failure', 'Success']
    
    # Create the pie chart
    fig = px.pie(
        names=names,
        values=values,
        title=title
    )
    
    return fig

# Callback for scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    # Check if filtered_df is empty
    if filtered_df.empty:
        return px.scatter(title="No Data Available for Selected Filters")

    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f"Payload vs. Launch Outcome for {entered_site}" if entered_site != 'ALL' else "Payload vs. Launch Outcome for All Sites",
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
    )
    
    # Update layout for better readability
    fig.update_layout(yaxis=dict(tickvals=[0, 1], ticktext=['Failure', 'Success']))

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
