import dash
from dash import dcc, html, Input, Output
from dash import dash_table
import plotly.express as px
import pandas as pd
import numpy as np

dash.register_page(__name__, path="/page1")

df = pd.read_csv('data/vaccination_continent.csv')

df['date'] = pd.to_datetime(df['date'])
df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
df = df.sort_values('date')

# remove countries with less than 100k population, also only show data once every 10 days
df = df[df['population'] >= 100_000]
df = df[df['date'].dt.day % 10 == 0]

# use top 100 countries by population
top_countries = (
    df.groupby('location_key')['population']
    .max()
    .nlargest(100)
    .index
)
df = df[df['location_key'].isin(top_countries)]

# get unique continents and dates
continents = df['continent'].unique()
date_options = sorted(df['date_str'].unique())

# Layout
layout = html.Div([
    html.H2("Vaccination Percentage vs. GDP per Capita", style={"color": "white"}),

    # Continent Checklist
    dcc.Checklist(
        id='continent-checklist',
        options=[{'label': c, 'value': c} for c in continents],
        value=continents.tolist(),
        labelStyle={'display': 'block', 'color': 'white'},
        style={'marginBottom': '20px'}
    ),

    # Bubble Chart (animated)
    dcc.Graph(
        id='bubble-chart',
        figure=px.scatter(
            df,
            x='gdp_per_capita_usd',
            y='percent_vaccinated',
            size='population',
            color='location_key',
            hover_name='country_name',
            size_max=70,
            animation_frame='date_str',
            template='plotly_dark',
            title='COVID-19 Vaccination vs GDP per Capita Over Time',
            height=700,
            labels={
                'gdp_per_capita_usd': 'GDP per Capita (USD)',
                'percent_vaccinated': 'Percent of Population Vaccinated'
            }
        ).update_layout(
            xaxis_type='log',
            xaxis_title='GDP per Capita (USD)',
            yaxis_title='% Fully Vaccinated',
            yaxis=dict(range=[0, 100]),
            showlegend=False
        )
    ),

    # Date dropdown to update the table
    html.Label("Select Date for Table", style={"color": "white", "marginTop": "20px"}),
    dcc.Dropdown(
        id='table-date-dropdown',
        options=[{'label': d, 'value': d} for d in date_options],
        value=date_options[-1],
        style={'width': '300px', 'marginBottom': '20px'}
    ),

    # Data Table (separate from animation)
    dash_table.DataTable(
        id='top-10-table',
        columns=[
            {'name': 'Country', 'id': 'country_name'},
            {'name': '% Vaccinated', 'id': 'percent_vaccinated', 'type': 'numeric', 'format': {'specifier': '.2f'}, 'editable': False},
            {'name': 'Population', 'id': 'population', 'type': 'numeric', 'format': {'specifier': ',.0f'}, 'editable': False},
            {'name': 'Fully Vaccinated', 'id': 'cumulative_persons_fully_vaccinated', 'type': 'numeric', 'format': {'specifier': ',.0f'}, 'editable': False},
            {'name': 'GDP per Capita (USD)', 'id': 'gdp_per_capita_usd', 'type': 'numeric', 'format': {'specifier': '$,.0f'}, 'editable': False},
        ],
        style_table={'overflowX': 'auto', 'marginTop': '10px'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'minWidth': '100px', 'maxWidth': '250px', 'whiteSpace': 'normal'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
        sort_action='native',
        filter_action='native',
        page_size=100,
        style_data_conditional=[
            # Gradient for 'percent_vaccinated' (0% red, 100% green)
            {
                'if': {
                    'column_id': 'percent_vaccinated'
                },
                'backgroundColor': 'white',  # default fallback color
                'color': 'black'
            }
        ] + [
            {
                'if': {
                    'filter_query': f'{{percent_vaccinated}} >= {i} && {{percent_vaccinated}} < {i + 5}',
                    'column_id': 'percent_vaccinated'
                },
                # Fix: Red to Green (0% = red, 100% = green)
                'backgroundColor': f'rgba({255 - int(i * 2.55)}, {int(i * 2.55)}, 0, 0.8)',  # Red to green gradient
                'color': 'white'
            }
            for i in range(0, 101, 5)
        ] + [
            # Apply a gradient to 'gdp_per_capita_usd' based on log-transformed values
            {
                'if': {
                    'filter_query': f'{{gdp_per_capita_usd}} >= {i * 1000} && {{gdp_per_capita_usd}} < {(i + 5) * 1000}',
                    'column_id': 'gdp_per_capita_usd'
                },
                # Fix: Red to Green (low GDP = red, high GDP = green)
                'backgroundColor': f'rgba({255 - int(i * 2.55)}, {int(i * 2.55)}, 0, 0.8)',  # Red to green gradient
                'color': 'white'
            }
            for i in range(0, 101, 5)  # Adjust for intervals of 5, since GDP can vary greatly
        ]
    )
])

# Callback to update DataTable only
@dash.callback(
    Output('top-10-table', 'data'),
    Input('continent-checklist', 'value'),
    Input('table-date-dropdown', 'value')
)
def update_table(selected_continents, selected_date):
    filtered_df = df[df['continent'].isin(selected_continents)]
    filtered_df = filtered_df[filtered_df['date_str'] == selected_date]

    # Ensure we use the logarithmic transformation for GDP
    filtered_df['gdp_per_capita_usd_log'] = np.log10(filtered_df['gdp_per_capita_usd'] + 1)  # Adding 1 to avoid log(0)

    return filtered_df[[  # Return data with log-transformed GDP values
        'country_name',
        'percent_vaccinated',
        'population',
        'cumulative_persons_fully_vaccinated',
        'gdp_per_capita_usd'
    ]].to_dict('records')

