from dash import Dash, html, dash_table, dcc, callback, Output, Input, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import requests
import json

##============================##
##      DATA & Classes        ##
##============================##
master_data = pd.read_csv("https://raw.githubusercontent.com/ctoruno/Nicaragua-dictators-speech/main/Data/speech_data.csv")
master_data["date"] = pd.to_datetime(master_data["date"], format = "%Y-%m-%d")

response = requests.get("https://raw.githubusercontent.com/ctoruno/Nicaragua-dictators-speech/main/Data/tklem_speeches.json")
tklem_speeches = json.loads(response.text)

# Initializing the app
app = Dash(__name__,
           external_stylesheets = [dbc.themes.SPACELAB, "/assets/styles.css"])

# Defining the SpeechData class
class SpeechData:
    def __init__(self, df):
        self.df = df

    def barPlot_nspeeches(self):
        grouped_data = (
            self.df
            .groupby("spoke_person")
            .size()
            .reset_index(name = "count")
        )
        fig = px.bar(
            grouped_data, 
            x    = "spoke_person", 
            y    = "count", 
            labels    = {"spoke_person": "Spoke Person", 
                        "count"       : "<i>Number of speeches</i>"},
            color_discrete_sequence = ["#CBDFBD"]
        )
        fig.update_layout(
            title        = "<b>Total Number of Speeches by Spoke Person</b>",
            title_font   = dict(
                size     = 16, 
                family   = "Open Sans"
            ),
            title_x        = 0.5,
            font_color     = "#201E1F",
            plot_bgcolor   = "#FFFFFF",
            xaxis          = dict(
                title      = dict(text = None),
                fixedrange = True
            ),
            yaxis          = dict(
                dtick      = 200,
                gridcolor  = "#3F3B3D", 
                gridwidth  = 0.5, 
                griddash   = "dash", 
                fixedrange = True,
                titlefont  = dict(family = "Open Sans"),
                autorangeoptions = dict(include = 1900),
            ),
            font = dict(family = "Open Sans")
        )
        return fig

    def barPlot_speechlen(self):
        grouped_data = (
            self.df
            .groupby("spoke_person")
            .nwords
            .mean()
            .reset_index(name = "mean")
        )
        fig = px.bar(
            grouped_data, 
            x      = "spoke_person", 
            y      = "mean", 
            labels = {"spoke_person": "Spoke Person", 
                      "mean"       : "<i>Average speech length (in words)</i>"},
            color_discrete_sequence = ["#F19C79"]
        )
        fig.update_layout(
            title         = "<b>Average speech length by Spoke Person</b>",
            title_font    = dict(
                size      = 16, 
                family    = "Open Sans"
            ),
            title_x        = 0.5,
            font_color     = "#201E1F",
            plot_bgcolor   = "#FFFFFF",
            xaxis          = dict(
                title      = dict(text = None),
                fixedrange = True
            ),
            yaxis          = dict(
                dtick      = 500,
                gridcolor  = "#3F3B3D", 
                gridwidth  = 0.5, 
                griddash   = "dash", 
                fixedrange = True,
                titlefont  = dict(family = "Open Sans"),
                autorangeoptions = dict(include = 3100),
            ),
            font = dict(family = "Open Sans")
            )
        return fig
    
    def lineChart_sp(self):
        grouped_data = (
            self.df
            .groupby([self.df["date"].dt.to_period("Q"), "spoke_person"])
            .spoke_person
            .size()
            .reset_index(name = "count")
        )
        grouped_data["date4plot"] = pd.PeriodIndex(grouped_data["date"], freq = "Q").strftime('%B, %Y')
        # grouped_data = grouped_data.set_index("date4plot")
        
        fig = px.line(
            grouped_data, 
            x = "date4plot", 
            y = "count",
            color  = "spoke_person",
            labels = {"date4plot": "Yearly Quarter", 
                      "count"    : "Number of speeches"},
            color_discrete_sequence = ["#667761", "#a44a3f"]
        )
        fig.update_layout(
            title = "<b>Total number of speeches over time</b>",
            title_font    = dict(
                size      = 16, 
                family    = "Open Sans"
            ),
            title_x        = 0.5,
            font_color     = "#201E1F",
            plot_bgcolor   = "#FFFFFF",
            xaxis          = dict(
                tickangle  = 45,
                fixedrange = True
            ),
            yaxis          = dict(
                dtick      = 20,
                gridcolor  = "#3F3B3D", 
                gridwidth  = 0.5, 
                griddash   = "dash", 
                fixedrange = True,
                titlefont  = dict(family = "Open Sans"),
                autorangeoptions = dict(include = 110)
            ),
            font = dict(family = "Open Sans")
            )
        return fig
    
    def totalSpeeches(self):
        nrows = len(self.df)
        nss = f"The data explored in this app covers a total of {nrows} speeches given by President Daniel Ortega and his wife and Vice-President Rosario Murillo."
        return nss

    def datesRange(self):
        minDate = self.df.date.dt.to_period("M").min().strftime('%B, %Y')
        maxDate = self.df.date.dt.to_period("M").max().strftime('%B, %Y')
        drange = f"Data covers a period of time starting from {minDate} to {maxDate}."
        return drange

data4app = SpeechData(master_data)

##============================##
##          APP LAYOUT        ##
##============================##

removedButtons = ["zoom", "zoomIn", "zoomOut", "pan", "select", "lasso2d", "autoScale", "resetScale"]

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("A Dictator's Speech", className = "text-center mt-5 mb-3 apptitle"),
        )
    ),
    dbc.Row(
        dbc.Col(
            html.P(
                """
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                Sed ornare justo eu turpis condimentum, in dapibus sapien 
                lacinia. Fusce vitae justo ac purus fermentum ullamcorper 
                a a elit. Donec sit amet nulla eu libero dapibus lacinia. 
                Pellentesque habitant morbi tristique senectus et netus et 
                malesuada fames ac turpis egestas.
                """,
                className = "text-justify ptext"
            ),
            width = {"size": 6, "offset": 3}
        )
    ),
    dmc.Space(h = 22),
    # dbc.Row(
    #     dbc.Col(
    #         dmc.Divider(variant = "solid"),
    #         width = {"size": 8, "offset": 2}
    #     )
    # ),
    dbc.Row(
        dbc.Col(
            dbc.Tabs([
                dbc.Tab([
                    dmc.Space(h = 22),
                    dbc.Row([
                        dbc.Col(
                            dmc.Card([
                                dmc.Group(
                                    dmc.Text("Total Speeches", weight = 500),
                                    position = "apart",
                                    mt = "md",
                                    mb = "xs"
                                ),
                                dmc.Text(
                                    data4app.totalSpeeches(),
                                    size="sm",
                                    color="dimmed",
                                )
                            ],
                            id = "card-daterange1")
                        ),
                        dbc.Col(
                            dmc.Card([
                                dmc.Group(
                                    dmc.Text("Time Range", weight = 500),
                                    position = "apart",
                                    mt = "md",
                                    mb = "xs"
                                ),
                                dmc.Text(
                                    data4app.datesRange(),
                                    size="sm",
                                    color="dimmed",
                                )
                            ],
                            id = "card-daterange2")
                        ),
                        dbc.Col(
                            dmc.Card([
                                dmc.Group(
                                    dmc.Text("Data Source", weight = 500),
                                    position = "apart",
                                    mt = "md",
                                    mb = "xs"
                                ),
                                dmc.Text(
                                    "Speech transcripts were extracted from the pro-government website Canal 4.",
                                    size="sm",
                                    color="dimmed",
                                ),
                                dmc.Anchor(
                                    dmc.Button(
                                    "See extraction code",
                                    variant   = "light",
                                    color     = "orange",
                                    fullWidth = True,
                                    mt        = "md",
                                    radius    = "lg",
                                    id        = "extractButton"
                                    ),
                                    href      = "https://github.com/ctoruno/Nicaragua-dictators-speech/blob/main/Code/1_web_scrapping/C4-extraction.py",
                                    target    = "_blank"
                                )
                            ],
                            id = "card-daterange3")
                        )
                    ]),
                    dmc.Space(h = 32),
                    html.P("LOREM IPSUM DOLOR"),
                    dcc.Graph(
                        id     = "nspeeches_sp",
                        figure = data4app.barPlot_nspeeches(),
                        config = {"modeBarButtonsToRemove": removedButtons} 
                    ),
                    html.P("LOREM IPSUM DOLOR"),
                    dcc.Graph(
                        id     = "nspeeches_sp",
                        figure = data4app.lineChart_sp(),
                        config = {"modeBarButtonsToRemove": removedButtons} 
                    ),
                    html.P("LOREM IPSUM DOLOR"),
                    dcc.Graph(
                        id     = "nspeeches_sp",
                        figure = data4app.barPlot_speechlen(),
                        config = {"modeBarButtonsToRemove": removedButtons} 
                    )
                ],
                label = "Data Preview",
                labelClassName = "tablab",
                activeLabelClassName = "active-tab",
                id = "tab-data"
                ),
                dbc.Tab([
                    dmc.Space(h = 22),
                    html.P("LOREM IPSUM DOLOR")
                    ],
                    label = "Topic Modelling",
                    labelClassName = "tablab",
                    activeLabelClassName = "active-tab",
                    id = "tab-topic"
                ),
                dbc.Tab([
                    dmc.Space(h = 22),
                    html.P("LOREM IPSUM DOLOR")
                    ],
                    label = "Sentiment Analysis",
                    labelClassName = "tablab",
                    activeLabelClassName = "active-tab",
                    id = "tab-sentiment"
                ),
                dbc.Tab([
                    dmc.Space(h = 22),
                    html.P("LOREM IPSUM DOLOR")
                    ],
                    label = "About",
                    labelClassName = "tablab",
                    activeLabelClassName = "active-tab",
                    id = "tab-about"
                )
            ]),
            width = {"size": 6, "offset": 3}
        )
    )
    
        
    # dcc.Dropdown(options = ["Daniel Ortega", "Rosario Murillo"], 
    #              value   = "Daniel Ortega",
    #              id      = "spoke_person"),
    # dash_table.DataTable(page_size = 10, id = "dta_preview")
], fluid = True)

##============================##
##         CALLBACKs          ##
##============================##

# @app.callback(
#     Output("extractLink", "href"),
#     Input("extractButton", "n_clicks")
# )
# def open_url_in_new_tab(n_clicks):
#     if n_clicks:
#         return extractGH
#     return no_update

# Run the app
if __name__ == '__main__':
    app.run(debug = True)