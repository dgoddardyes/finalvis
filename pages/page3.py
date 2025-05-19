# page3.py
import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import plotly.express as px
import pandas as pd
import json
import os

dash.register_page(__name__, path="/page3")

# Ensure JSON file exists
json_path = os.path.join("data", "government_measures.json")
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Error: {json_path} not found!")

with open(json_path, "r") as file:
    data = json.load(file)

df = pd.DataFrame(data)
df["date"] = pd.to_datetime(df["date"])
unique_dates = sorted(df["date"].dt.strftime("%Y-%m-%d").unique())

TEXT_COLOR = "#00FFC6"  # override CSS

# initial map
def create_map(date_selected):
    df_filtered = df[df["date"] == date_selected]
    fig = px.choropleth(
        df_filtered,
        locations="iso_a3",
        color="normalized_measures",
        hover_name="iso_a3",
        color_continuous_scale="Reds",
        projection="natural earth",
        title=f"Level of COVID-19 measures, circa {date_selected}",
    )
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        geo=dict(showcoastlines=True, showland=True),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Ensure transparency
        title=dict(font=dict(color=TEXT_COLOR)),
        coloraxis_colorbar=dict(
            title="Level of Measures",
            title_font=dict(color=TEXT_COLOR),
            tickfont=dict(color="#A9A9A9"),
            bgcolor="rgba(0, 0, 0, 0)",
            outlinecolor="#333333",
        ),
        width=1400,
        height=700,
    )
    return fig

# layout
layout = html.Div([
    html.H2("COVID-19 Government Measures", style={"color": TEXT_COLOR, "textAlign": "center"}),  # Center the title
    html.P("Press play to start or use the slider to navigate", style={"color": "#A9A9A9", "textAlign": "center"}),  # Center the subtitle

    # date slider
    html.Div([
        dcc.Slider(
            id="date-slider-page3",
            min=0,
            max=len(unique_dates) - 1,
            value=0,
            marks={i: unique_dates[i] for i in range(0, len(unique_dates), max(1, len(unique_dates) // 10))},
            step=1,
            tooltip={"placement": "bottom", "always_visible": True}
        ),
    ], style={"width": "80%", "margin": "0 auto"}),  # Wrapper div for slider styling

    # Play/pause and speed Control
    html.Div([
        html.Button("Play", id="play-pause-button-page3", n_clicks=0, style={"marginRight": "20px"}),
        html.Label("Playback Speed:", style={"color": TEXT_COLOR}),
        html.Div([
            dcc.Slider(
                id="playback-speed-page3",
                min=0.5,
                max=3,
                step=0.5,
                value=1,
                marks={0.5: "0.5x", 1: "1x", 2: "2x", 3: "3x"},
                tooltip={"placement": "bottom", "always_visible": False},
            )
        ], style={"width": "300px", "display": "inline-block", "marginLeft": "10px", "background": "transparent"}),
    ], style={"marginTop": "20px", "background": "transparent", "textAlign": "center"}),  # Center the controls

    # interval for auto-play
    dcc.Interval(
        id="interval-component-page3",
        interval=500,
        n_intervals=0,
        disabled=True,
    ),

    # Graph to display the map
    dcc.Graph(
        id="covid-map-page3",
        figure=create_map(unique_dates[0]),
        style={"width": "100%", "height": "80vh", "margin": "0 auto", "background": "transparent"}  # Full-width and transparent background
    )
], style={
    "height": "100vh",  # Make layout take up most of the page
    "background": "transparent",  # Transparent background
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "center",  # Center elements vertically
    "alignItems": "center"  # Center elements horizontally
})

# Update Map when Slider changes
@dash.callback(
    Output("covid-map-page3", "figure"),
    Input("date-slider-page3", "value"),
    State("covid-map-page3", "relayoutData")
)
def update_map(selected_index, relayout_data):
    selected_date = unique_dates[selected_index]
    fig = create_map(selected_date)

    if relayout_data:
        fig.update_layout(**relayout_data)

    return fig

# Unified Callback: Play/Pause Toggle AND Speed Change
@callback(
    Output("play-pause-button-page3", "children", allow_duplicate=True),
    Output("interval-component-page3", "disabled", allow_duplicate=True),
    Output("interval-component-page3", "interval", allow_duplicate=True),
    Input("play-pause-button-page3", "n_clicks"),
    Input("playback-speed-page3", "value"),
    State("interval-component-page3", "disabled"),
    prevent_initial_call=True
)
def toggle_play_pause_and_speed(n_clicks, playback_speed, interval_disabled):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "play-pause-button-page3":
        if n_clicks % 2 == 1:  # Play
            return "Pause", False, 500 / playback_speed
        else:  # Pause
            return "Play", True, 500 / playback_speed

    elif trigger_id == "playback-speed-page3":
        return no_update, no_update, 500 / playback_speed

# Update Slider Automatically with Interval
@dash.callback(
    Output("date-slider-page3", "value"),
    Input("interval-component-page3", "n_intervals"),
    State("date-slider-page3", "value"),
    prevent_initial_call=True
)
def update_slider(n_intervals, current_value):
    next_index = current_value + 1
    if next_index >= len(unique_dates):
        next_index = 0
    return next_index
