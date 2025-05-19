import dash
from dash import html, dcc

# Register the page
dash.register_page(__name__, path="/home")

layout = html.Div([

    html.Div([
        html.Div([
            html.Div([
                html.H3("Vaccinations"),
                html.P("COVID-19 vaccination rate vs. GDP per capita."),
                dcc.Link(html.Button("Go to Vaccinations"), href="/page1")
            ], className="nav-card"),

            html.Div([
                html.H3("R0 Simulation"),
                html.P("Simulate different R0 values and vaccination rates in a population"),
                dcc.Link(html.Button("Go to R0 Simulation"), href="/page2")
            ], className="nav-card"),

            html.Div([
                html.H3("Government Measures"),
                html.P("Explore how different countries responded to COVID-19 with policy measures."),
                dcc.Link(html.Button("Go to Government Measures"), href="/page3")
            ], className="nav-card"),

            html.Div([
                html.H3("Health Statistics"),
                html.P("Access a variety of health statistics from around the world"),
                dcc.Link(html.Button("Go to Health Statistics"), href="/page4")
            ], className="nav-card"),
        ], className="grid-container")

    ], className="navigation-section")
])
