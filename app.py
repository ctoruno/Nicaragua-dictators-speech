from dash import Dash, html, dash_table, dcc, callback, Output, Input, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import requests
import json

##============================##
##      DATA & Classes        ##
##============================##

# Reading data
master_data = pd.read_csv("https://raw.githubusercontent.com/ctoruno/Nicaragua-dictators-speech/main/Data/speech_data.csv")
master_data["date"] = pd.to_datetime(master_data["date"], format = "%Y-%m-%d")

response = requests.get("https://raw.githubusercontent.com/ctoruno/Nicaragua-dictators-speech/main/Data/tklem_speeches.json")
tklem_speeches = json.loads(response.text)

with open("assets/LDAvis_daniel.html", 'r') as file:
    Daniel_LDA = file.read()
with open("assets/LDAvis_rosario.html", 'r') as file:
    Rosario_LDA = file.read()

# Initializing the app
app = Dash(__name__,
           external_stylesheets = [dbc.themes.SPACELAB, "/assets/styles.css"])
server = app.server

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
            x = grouped_data.index, 
            y = "count",
            color  = "spoke_person",
            labels = {"date4plot"    : "Yearly Quarter", 
                      "count"        : "Number of speeches",
                      "spoke_person" : "Spoke Person"},
            custom_data   = ["date4plot", "spoke_person"],
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
                fixedrange = True,
                title      = dict(text = "Yearly Quarter", font = dict(family = "Open Sans"), standoff = 40),
                showticklabels = False
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
        fig.update_traces(
            hovertemplate = "Date: %{customdata[0]}<br>Total speeches: %{y}"
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

class Tokenized:
    def __init__(self, ls):
        self.ls = ls

    def WCplot(self):
        all_tokens = [token for speech in self.ls for token in speech]
        combined_tokens = " ".join(all_tokens)
        wcloud = WordCloud(
            width    = 1000, 
            height   = 500, 
            colormap = "twilight",
            relative_scaling = 0.45,
            background_color = "white"
        ).generate(combined_tokens)
        return wcloud

# Initializing classes
data4app   = SpeechData(master_data)
daniel_wc  = Tokenized(tklem_speeches["Daniel"]).WCplot()
daniel_wc.to_file('assets/daniel_wc.png')
rosario_wc = Tokenized(tklem_speeches["Rosario"]).WCplot()
rosario_wc.to_file('assets/rosario_wc.png')

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
            dcc.Markdown(
                """
                Welcome to *A Dictator's Speech* - a collection of speeches delivered by Nicaragua's President and Vice-President. 
                We've compiled this data from official transcripts found in pro-government media. Our goal is to provide 
                accessible data for future research. In the tabs below, you can find a **_data preview_**, a basic **_topic modeling_**, 
                and a simple **_sentiment analysis_**. Feel free to download the data by clicking on the button at the bottom of this 
                page.

                The python code for this project is publicly available on [this GitHub repository](https://github.com/ctoruno/Nicaragua-dictators-speech).
                """,
                className = "text-justify ptext"
            ),
            width = {"size": 6, "offset": 3}
        )
    ),
    dmc.Space(h = 22),
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
                    # dmc.Divider(variant = "solid"),
                    # dmc.Space(h = 15),
                    dcc.Markdown(
                        """
                        From September 2015 to December 2023, we extracted 1,742 speech transcripts. Surprisingly, 93% of these speeches were delivered by 
                        Vice-President Rosario Murillo. In contrast, President Daniel Ortega contributed only 112 speeches. This significant disparity arises 
                        from the Vice-President's regular weekday messages to the nation, while the President reserves speeches only for special events.
                        """,
                        className = "text-justify ptext"
                    ),
                    dcc.Graph(
                        id     = "nspeeches_sp",
                        figure = data4app.barPlot_nspeeches(),
                        config = {"modeBarButtonsToRemove": removedButtons} 
                    ),
                    dcc.Markdown(
                        """
                        The amount of speeches given by the presidential couple has been stable over time since 2016. There was a brief significant decrease
                        of messages to the nation given by the Vice-President Rosario Murillo between the first quarter (March) of 2019 and the fourth quarter (December)
                        of 2020. This decrease might have been due to the first months of the global COVID-19 pandemic.
                        """,
                        className = "text-justify ptext"
                    ),
                    dcc.Graph(
                        id     = "nspeeches_sp",
                        figure = data4app.lineChart_sp(),
                        config = {"modeBarButtonsToRemove": removedButtons} 
                    ),
                    dmc.Space(h = 26),
                    dcc.Markdown(
                        """
                        Typically, President Daniel Ortega's speeches surpass the length of those given by the Vice-President. Daniel Ortega's speeches 
                        can extend to nearly 2,800 words, while Rosario Murillo's messages average less than 2,200 words in length.
                        """,
                        className = "text-justify ptext"
                    ),
                    dcc.Graph(
                        id     = "nspeeches_sp",
                        figure = data4app.barPlot_speechlen(),
                        config = {"modeBarButtonsToRemove": removedButtons} 
                    ),
                    dcc.Markdown(
                        """
                        When examining their choice of words, distinctive sets of phrases emerge. President Daniel Ortega often employs direct and populist 
                        language, such as "People United", "People's Power", "War and Peace", "Yankee". In contrast, the Vice-President adopts a more religious 
                        and passive tone, utilizing phrases like "Thanks God", "Nicaraguan Families", and "Blessed Nicaragua".

                        _Click the tabs below to see a word cloud of the most frequent bigrams used by the Presidential couple_.
                        """,
                        className = "text-justify ptext"
                    ),
                    dmc.Tabs([
                        dmc.TabsList([
                            dmc.Tab("Daniel Ortega", value = "DOwc"),
                            dmc.Tab("Rosario Murillo", value = "RMwc")
                        ]),
                        dmc.TabsPanel(
                            html.Div([
                                html.Img(src = "assets/daniel_wc.png", width = "90%")
                            ]), 
                            value = "DOwc"
                        ),
                        dmc.TabsPanel(
                            html.Div([
                                html.Img(src = "assets/rosario_wc.png", width = "90%")
                            ]), 
                            value = "RMwc"
                        )
                        ],
                        color = "orange",
                        orientation = "vertical",
                    )
                ],
                label = "Data Preview",
                labelClassName = "tablab",
                activeLabelClassName = "active-tab",
                id = "tab-data"
                ),
                dbc.Tab([
                    dmc.Space(h = 22),
                     dcc.Markdown(
                        """
                        Below, you can find a basic Topic Modelling using a Latent Dirichlet Allocation (LDA) algorithm. Topic modeling is a technique 
                        to discover underlying themes in a collection of text documents (such as our speech transcripts) by identifying common patterns 
                        and grouping words into topics.

                        The LDA model was configured to identify four overarching topics in the President's speeches while only three broad topics in 
                        the Vice President's. This adjustment aimed to mitigate topic overlap, as depicted in the graph below. However, it should be 
                        noted that the likelihood of overlap in their speeches remains considerable. As such, these findings should be interpreted 
                        with caution. Additionally, we suggest using a medium grade relevance metric (λ = 0.6). 

                        Under these assumptions, the following highlights arise:

                        - Daniel Ortega has four broad topics:
                            - The first (and main) topic has a high prevalence of the old latin american left-wing governments (Hugo Chavez in Venezuela,  
                            Fidel Castro in Cuba) as well as terms usually related to this political group: Yankee, Sandino, among others.
                            - The second biggest topic is highly random and white noise.
                            - The third topic in prevalence, is very related to the first one. However, it has a high prevalence of topics and 
                            institutions prominent in Authoritarian figures (such as the Police and the Army) but also topics common in left-wing
                            speeches such as education.
                            - A fourth topic comprising less than 10% of the analyzed tokens has a high prevalence of private firms and institutions
                            (such as LAFISE, Cargill, AmCham) as well as mentions to local opposition figures such as the Bishop.

                            
                        - Rosario Murillo has two main topics:
                            - The first (and main) topic has a high prevalence of social issues such as poverty, hospitals, justice, agriculture, equality
                            and rights.
                            - The second most important topic has a high prevalence of topics related to a national reconciliation, hope, national 
                            sovereignty, motherland, dignity.
                        """,
                        className = "text-justify ptext"
                    ),
                    dmc.Space(h = 32),
                    dbc.Tabs([
                        dbc.Tab(
                            [
                                html.Div(
                                    html.Iframe(
                                        srcDoc = Daniel_LDA,
                                        width  = "800vw",
                                        height = "900px",
                                        style = {                                        
                                            "transform"       : "scale(0.95)",
                                            "transform-origin": "0 0",
                                            "overflow"        : "hidden"
                                        }
                                    ),
                                    style = {"width": "100%"}
                                )
                            ],
                            style = {"width": "100%", "overflow": "hidden", "textAlign": "center"},
                            label = "Daniel Ortega",
                            id = "tab-LDA-Daniel",
                            labelClassName = "tablab-topic",
                            activeLabelClassName = "active-tab-topic"
                        ),
                        dbc.Tab(
                            [
                                html.Div(
                                    html.Iframe(
                                        srcDoc = Rosario_LDA,
                                        width  = "800vw",
                                        height = "900px",
                                        style = {                                        
                                            "transform"       : "scale(0.95)",
                                            "transform-origin": "0 0",
                                            "overflow"        : "hidden"
                                        }
                                    ),
                                    style = {"width": "100%"}
                                )
                            ],
                            style = {"width": "100%", "overflow": "hidden", "textAlign": "center"},
                            label = "Rosario Murillo",
                            id = "tab-LDA-Rosario",
                            labelClassName = "tablab-topic",
                            activeLabelClassName = "active-tab-topic"
                        )
                    ]),
                    ],
                    label = "Topic Modelling",
                    labelClassName = "tablab",
                    activeLabelClassName = "active-tab",
                    id = "tab-topic"
                ),
                dbc.Tab([
                    dmc.Space(h = 22),
                    html.P("UNDER DEVELOPMENT.")
                    ],
                    label = "Sentiment Analysis",
                    labelClassName = "tablab",
                    activeLabelClassName = "active-tab",
                    id = "tab-sentiment"
                ),
                dbc.Tab([
                    dmc.Space(h = 22),
                    dcc.Markdown(
                        """
                        ### Licence

                        Copyright (c) 2023

                        _Permission is hereby granted, free of charge, to any person obtaining a copy
                        of this software and associated documentation files (the "Software"), to deal
                        in the Software without restriction, including without limitation the rights
                        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
                        copies of the Software, and to permit persons to whom the Software is
                        furnished to do so, subject to the following conditions_:

                        _The above copyright notice and this permission notice shall be included in all
                        copies or substantial portions of the Software._

                        _THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
                        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
                        SOFTWARE._

                        ### Disclaimer

                        This application ("App") is provided for informational purposes only. The content 
                        within the App is not intended to be a substitute for professional advice. While 
                        efforts have been made to ensure the accuracy and reliability of the information 
                        provided, the creators make no representations or warranties of any kind, express 
                        or implied, about the completeness, accuracy, reliability, suitability, or 
                        availability with respect to the App or the information, products, services, or 
                        related graphics contained within the App for any purpose. 

                        The use of this App is at your own risk. The creators shall not be liable for 
                        any loss or damage arising from the use of this page.

                        Please note that the App may contain links to external websites or resources. 
                        The inclusion of any links does not necessarily imply a recommendation or 
                        endorsement of the views expressed within them.

                        """,
                        className = "text-justify ptext"
                    )
                    ],
                    label = "About",
                    labelClassName = "tablab",
                    activeLabelClassName = "active-tab",
                    id = "tab-about"
                )
            ]),
            width = {"size": 6, "offset": 3}
        )
    ),
    dmc.Space(h = 40),
    dbc.Row(
        dbc.Col([
            html.Div([
                html.Button(
                    "Download Data",
                    # color = "success",
                    id = "download-data-bttn"
                ),
                dcc.Download(id = "download-data")
            ])
        ], width = {"size": 4}
        ),
        justify = "end" 
    ),
    dmc.Space(h = 150)
], fluid = True)

##============================##
##         CALLBACKs          ##
##============================##

@callback(
    Output("download-data", "data"),
    Input("download-data-bttn", "n_clicks"),
    prevent_initial_call = True,
)
def func(n_clicks):
    return dcc.send_data_frame(master_data.to_csv, "speech_data.csv")

# Run the app
if __name__ == '__main__':
    app.run(debug = True)