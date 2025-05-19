# app.py (modified)
import dash
from dash import dcc, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# define the page order for navigation (not using anymore but keeping anyway)
page_order = ["/home", "/page1", "/page2", "/page3", "/page4"]

# sidebar layout
sidebar = html.Div(
    [
        html.H2("Navigation", className="sidebar-header"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", active="exact"),
                dbc.NavLink("Vaccinations", href="/page1", active="exact"),
                dbc.NavLink("R0 Simulation", href="/page2", active="exact"),
                dbc.NavLink("Government Measures", href="/page3", active="exact"),
                dbc.NavLink("Health Statistics", href="/page4", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "200px",
        "padding": "20px",
        "background-color": "#181818",
    },
)

# main content layout
content = html.Div(
    [
        dcc.Location(id="url", refresh=False),  # store current pathname
        html.Div(dash.page_container, id="page-content", className="fade-enter"),  # page content
    ],
    style={"margin-left": "220px", "padding": "20px"},  # add margin to make space for the sidebar
)

# App layout
app.layout = html.Div([sidebar, content])

# Clientside Callback for Fade Animation
app.clientside_callback(
    """
    function(url) {
        var page = document.getElementById("page-content");
        if (page) {
            page.style.opacity = 0;  // Start transparent
            setTimeout(() => { page.style.opacity = 1; }, 100);  // Fade in
        }
        return url;
    }
    """,
    Output("url", "pathname"),
    Input("url", "pathname")
)

# Callback for Next button
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("next-page", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True
)
def go_to_next_page(n_clicks, current_pathname):
    if n_clicks:
        current_index = page_order.index(current_pathname)
        next_index = (current_index + 1) % len(page_order)
        return page_order[next_index]
    return dash.no_update

# Callback for Previous button
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("prev-page", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True
)
def go_to_previous_page(n_clicks, current_pathname):
    if n_clicks:
        current_index = page_order.index(current_pathname)
        prev_index = (current_index - 1) % len(page_order)
        return page_order[prev_index]
    return dash.no_update

if __name__ == '__main__':
    app.run(debug=True)