import dash
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np
import random
from dash.dependencies import Input, Output, State

# this registers the page in a multi-page dash app
dash.register_page(__name__, path="/page2")

history = []

# some constants for the simulation setup
num_people = 100
width, height = 300, 300
infection_radius = 8
duration = 150  # how long someone stays infected before recovering

# function to set up everyone at the start of the simulation
def initialize_simulation(infected_count=1, vaccination_percentage=0):
    people = []
    for _ in range(num_people):
        people.append({
            "x": random.uniform(0, width),  # random starting x position
            "y": random.uniform(0, height),  # random starting y position
            "vx": random.uniform(-1, 1),  # random x direction/speed
            "vy": random.uniform(-1, 1),  # random y direction/speed
            "infected": False,
            "recovered": False,
            "vaccinated": False, 
            "time_infected": 0  # track how long someone has been infected
        })
    
    # figure out how many people should be vaccinated
    vaccinated_count = int(num_people * (vaccination_percentage / 100))
    for i in range(vaccinated_count):
        people[i]["vaccinated"] = True

    # infect the first few who aren't vaccinated
    non_vaccinated = [p for p in people if not p["vaccinated"]]
    for i in range(min(infected_count, len(non_vaccinated))):
        non_vaccinated[i]["infected"] = True
    
    return people

# function to update positions and spread infection each tick
def update_simulation(people, R0):
    grid_size = infection_radius * 2
    grid = {}

    # divide the space into grid cells for faster neighbor lookup
    for i, person in enumerate(people):
        grid_x = int(person["x"] // grid_size)
        grid_y = int(person["y"] // grid_size)
        grid.setdefault((grid_x, grid_y), []).append(i)

    new_people = []
    for person in people:
        # move each person
        person["x"] += person["vx"] * 2
        person["y"] += person["vy"] * 2

        # bounce off the walls if they hit the edges
        if person["x"] < 0 or person["x"] > width:
            person["vx"] *= -1
        if person["y"] < 0 or person["y"] > height:
            person["vy"] *= -1

        # check if infected person has recovered
        if person["infected"]:
            person["time_infected"] += 1
            if person["time_infected"] > duration:
                person["infected"] = False
                person["recovered"] = True

        new_people.append(person)

    # go through neighbors and try to spread the infection
    for i, p1 in enumerate(new_people):
        if p1["infected"]:
            grid_x = int(p1["x"] // grid_size)
            grid_y = int(p1["y"] // grid_size)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    neighbors = grid.get((grid_x + dx, grid_y + dy), [])
                    for j in neighbors:
                        if i != j:
                            p2 = new_people[j]
                            # only infect if they're not immune and close enough
                            if not p2["infected"] and not p2["recovered"] and not p2["vaccinated"]:
                                distance = np.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)
                                # infection probability based off of R0 set by user
                                if distance < infection_radius and random.random() < R0 / 10:
                                    p2["infected"] = True

    return new_people

# create the plotly figure with different color dots for each group
def create_figure(people, r0):
    infected_x, infected_y = [], []
    recovered_x, recovered_y = [], []
    healthy_x, healthy_y = [], []
    vaccinated_x, vaccinated_y = [], []

    for person in people:
        if person["vaccinated"]:
            vaccinated_x.append(person["x"])
            vaccinated_y.append(person["y"])
        elif person["infected"]:
            infected_x.append(person["x"])
            infected_y.append(person["y"])
        elif person["recovered"]:
            recovered_x.append(person["x"])
            recovered_y.append(person["y"])
        else:
            healthy_x.append(person["x"])
            healthy_y.append(person["y"])

    fig = go.Figure(layout=dict(template="plotly_dark"))
    fig.add_trace(go.Scattergl(x=vaccinated_x, y=vaccinated_y, mode='markers',
                               marker=dict(color='blue', size=5), name='Vaccinated'))
    fig.add_trace(go.Scattergl(x=infected_x, y=infected_y, mode='markers',
                               marker=dict(color='red', size=5), name='Infected'))
    fig.add_trace(go.Scattergl(x=recovered_x, y=recovered_y, mode='markers',
                               marker=dict(color='green', size=5), name='Recovered'))
    fig.add_trace(go.Scattergl(x=healthy_x, y=healthy_y, mode='markers',
                               marker=dict(color='white', size=5), name='Healthy'))

    # set up layout and axis settings
    fig.update_layout(
        title=f"R0 = {r0:.1f}, Population = {num_people}",
        xaxis=dict(
            range=[0, width],
            scaleanchor="y",
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[0, height],
            showticklabels=False,
            zeroline=False
        ),
        showlegend=True,
        width=800,
        height=800
    )
    return fig


def create_time_series(history):
    steps = [h["step"] for h in history]
    infected = [h["infected"] for h in history]
    recovered = [h["recovered"] for h in history]
    vaccinated = [h["vaccinated"] for h in history]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=steps, y=infected, mode='lines', name='Infected', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=steps, y=recovered, mode='lines', name='Recovered', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=steps, y=vaccinated, mode='lines', name='Vaccinated', line=dict(color='blue')))

    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=20, b=20),
        height=300,
        xaxis_title="Time Step",
        yaxis_title="Count",
        title="Epidemic Progress Over Time",
        legend=dict(orientation="h", y=-0.3)
    )
    return fig

# set up initial simulation
people = initialize_simulation()

# layout for the page
layout = html.Div([
    html.H2("R0 value simulation"),
    html.Div([
        # left side shows the graph
        dcc.Graph(id='pandemic-graph-page2', style={"flex": "3"}),

        # right side has the controls
        html.Div([
            html.P("R0 value:"),
            dcc.Slider(
                id='r0-slider',
                min=0.5,
                max=3.0,
                step=0.1,
                value=1.5,
                marks={i: str(i) for i in np.arange(0.5, 3.1, 0.5)}
            ),
            html.P("Population"),
            dcc.Slider(
                id='num-people-slider',
                min=10,
                max=250,
                step=10,
                value=num_people,
                marks={i: str(i) for i in range(10, 251, 40)}
            ),
            html.P("Percentage vaccinated"),
            dcc.Slider(
                id='vaccination-slider',
                min=0,
                max=90,
                step=10,
                value=0,
                marks={i: f"{i}%" for i in range(0, 91, 10)}
            ),
            html.Div(id='counter-display-page2', style={"margin-top": "10px", "font-size": "16px"}),
            html.Button('Restart Simulation', id='restart-button', n_clicks=0),
        ], style={"flex": "1", "padding": "10px"}),
    ], style={"display": "flex", "flex-direction": "row"}),

    # this handles the frame updates
    dcc.Interval(
        id='interval-page2',
        interval=100,
        n_intervals=0
    ),
    dcc.Graph(id='time-series-graph', style={"margin-top": "20px"})

])

# keep track of the restart state
last_restart_clicks = 0

# this updates the graph and the counters as time passes or when settings change
@dash.callback(
    [Output("pandemic-graph-page2", "figure"), Output("counter-display-page2", "children"), Output("time-series-graph", "figure")],
    [Input("r0-slider", "value"), Input("interval-page2", "n_intervals"), Input("restart-button", "n_clicks")],
    [State("num-people-slider", "value"), State("vaccination-slider", "value")],
    prevent_initial_call=True
)
def update_graph(r0, n_intervals, restart_clicks, num_people_value, vaccination_percentage):
    global people, last_restart_clicks, num_people, history

    # reinitialize simulation if restart was clicked or population changed
    if restart_clicks != last_restart_clicks or num_people != num_people_value:
        num_people = num_people_value
        people = initialize_simulation(vaccination_percentage=vaccination_percentage)
        last_restart_clicks = restart_clicks
        
        # Reset the history and time step when the simulation restarts
        history.clear()
        history.append({
            "step": 0,
            "infected": 0,
            "recovered": 0,
            "vaccinated": 0
        })
        n_intervals = 0  # reset the time step to 0

    # update people's positions and infection state
    people = update_simulation(people, r0)

    # count how many are in each category
    infected_count = sum(1 for person in people if person["infected"])
    recovered_count = sum(1 for person in people if person["recovered"])
    vaccinated_count = sum(1 for person in people if person["vaccinated"])

    # append to history
    if n_intervals == 0 or (restart_clicks != last_restart_clicks or num_people != num_people_value):
        history.clear()  # reset history if restarting
        history.append({
            "step": 0,
            "infected": infected_count,
            "recovered": recovered_count,
            "vaccinated": vaccinated_count
        })
    else:
        history.append({
            "step": n_intervals,
            "infected": infected_count,
            "recovered": recovered_count,
            "vaccinated": vaccinated_count
        })

    counter_text = f"Infected: {infected_count}, Recovered: {recovered_count}, Vaccinated: {vaccinated_count}"

    return create_figure(people, r0), counter_text, create_time_series(history)