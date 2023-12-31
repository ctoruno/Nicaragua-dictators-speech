from dash import Dash, html

# Initializing the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='Hello World')
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)