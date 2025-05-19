import dash
from dash import html, dcc, Input, Output, callback, dash_table
import pandas as pd
import numpy as np
import plotly.express as px

dash.register_page(__name__, path="/page4")

df = pd.read_csv("data/health_stats_countries_final_actual.csv")
metrics = [
    "life_expectancy", "smoking_prevalence", "diabetes_prevalence",
    "infant_mortality_rate", "adult_male_mortality_rate", "adult_female_mortality_rate",
    "pollution_mortality_rate", "comorbidity_mortality_rate",
    "nurses_per_1000", "physicians_per_1000",
    "health_expenditure_usd", "out_of_pocket_health_expenditure_usd"
]
df[metrics] = df[metrics].apply(lambda col: pd.to_numeric(col, errors='coerce'))



# Layout with chart + two separate tables
def layout():
    return html.Div([
        html.H1("Global Health Statistics"),
        
        html.Div([
            html.Label("Select a Health Metric:"),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[{"label": m.replace('_', ' ').title(), "value": m} for m in metrics],
                value="life_expectancy",
                clearable=False
            ),
        ], style={"width": "50%", "padding": "10px"}),

        # Row 1: Choropleth + Distribution
        html.Div([
            html.Div([
                dcc.Graph(id="choropleth-map", config={"displayModeBar": False}, style={"height": "70vh"})
            ], style={"width": "70%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                dcc.Graph(id="distribution-chart", config={"displayModeBar": False}, style={"height": "40vh"})
            ], style={"width": "28%", "paddingLeft": "10px", "display": "inline-block", "verticalAlign": "top"})
        ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

        # Row 2: Top 5 / Bottom 5 and Stats Panel
        html.Div([
            html.Div([
                html.H3("Top 5 Countries"),
                dash_table.DataTable(
                    id="top-5-table",
                    columns=[{"name": "Country", "id": "country"}, {"name": "Value", "id": "value"}],
                    style_table={"overflowX": "auto", "borderRadius": "10px", "border": "1px solid #444"},
                    style_cell={"textAlign": "left", "padding": "10px", "backgroundColor": "#222", "color": "#ddd", "border": "1px solid #444"},
                    style_header={"backgroundColor": "#333", "color": "white", "fontWeight": "bold", "border": "1px solid #444"},
                    style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#2c2c2c"}]
                ),
                html.Br(),
                html.H3("Bottom 5 Countries"),
                dash_table.DataTable(
                    id="bottom-5-table",
                    columns=[{"name": "Country", "id": "country"}, {"name": "Value", "id": "value"}],
                    style_table={"overflowX": "auto", "borderRadius": "10px", "border": "1px solid #444"},
                    style_cell={"textAlign": "left", "padding": "10px", "backgroundColor": "#222", "color": "#ddd", "border": "1px solid #444"},
                    style_header={"backgroundColor": "#333", "color": "white", "fontWeight": "bold", "border": "1px solid #444"},
                    style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#2c2c2c"}]
                )
            ], style={"width": "68%", "padding": "10px", "display": "inline-block", "verticalAlign": "top"}),

            html.Div(id="metric-stats-panel", style={
                "width": "30%",
                "backgroundColor": "#1e1e1e",
                "color": "#fff",
                "padding": "15px",
                "margin": "10px",
                "borderRadius": "10px",
                "border": "1px solid #444",
                "display": "inline-block",
                "verticalAlign": "top"
            })
        ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"})
    ])


# Callback for choropleth + both tables
@callback(
    Output("choropleth-map", "figure"),
    Output("top-5-table", "data"),
    Output("bottom-5-table", "data"),
    Output("metric-stats-panel", "children"),
    Output("distribution-chart", "figure"),
    Input("metric-dropdown", "value")
)
def update_choropleth(selected_metric):
    df_plot = df.copy()
    df_plot[selected_metric] = df_plot[selected_metric].replace(77777, np.nan)

    # Choropleth
    fig = px.choropleth(
        df_plot,
        locations="country_name",
        locationmode="country names",
        color=selected_metric,
        hover_name="country_name",
        projection="natural earth",
        title=f"Global {selected_metric.replace('_', ' ').title()}",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(marker_line_color='white')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            bgcolor='rgba(0,0,0,0)'
        ),
        coloraxis_colorbar=dict(title=selected_metric.replace('_', ' ').title()),
        title_font=dict(color='white')
    )

    # Top and Bottom 5
    sorted_df = df_plot[["country_name", selected_metric]].dropna().sort_values(by=selected_metric)
    bottom5_df = sorted_df.head(5)
    top5_df = sorted_df.tail(5).sort_values(by=selected_metric, ascending=False)

    top5_data = [{
        "country": f"{row['country_name']}",
        "value": f"{row[selected_metric]:,.2f}"
    } for _, row in top5_df.iterrows()]

    bottom5_data = [{
        "country": f"{row['country_name']}",
        "value": f"{row[selected_metric]:,.2f}"
    } for _, row in bottom5_df.iterrows()]

    valid_data = df_plot[["country_name", selected_metric]].dropna()
    mean_val = valid_data[selected_metric].mean()
    median_val = valid_data[selected_metric].median()
    count_val = valid_data[selected_metric].count()
    max_row = valid_data.loc[valid_data[selected_metric].idxmax()]
    min_row = valid_data.loc[valid_data[selected_metric].idxmin()]

    stats_panel = html.Div([
        html.H4(f"Global Statistics for {selected_metric.replace('_', ' ').title()}"),
        html.P(f"Mean: {mean_val:,.2f}"),
        html.P(f"Median: {median_val:,.2f}"),
        html.P(f"Countries with Data: {count_val}"),
        html.P(f"Maximum: {max_row['country_name']} ({max_row[selected_metric]:,.2f})"),
        html.P(f"Minimum: {min_row['country_name']} ({min_row[selected_metric]:,.2f})"),
    ])

        # Distribution chart (Histogram)
    dist_fig = px.histogram(
        valid_data,
        x=selected_metric,
        nbins=30,
        title=f"Distribution of {selected_metric.replace('_', ' ').title()}",
        marginal="box",
        opacity=0.75
    )
    dist_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font=dict(color='white'),
        xaxis_title=selected_metric.replace('_', ' ').title(),
        yaxis_title="Count"
    )

    return fig, top5_data, bottom5_data, stats_panel, dist_fig
