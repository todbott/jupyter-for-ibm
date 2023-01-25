# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'ALL'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                ],
                                value='ALL',
                                placeholder="Select a launch site",
                                searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        10000: '10,000'},
                                    value=[0, 10000], id='payload-slider'),
                                
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
                Input(component_id='site-dropdown', component_property='value'),
               # REVIEW4: Holding output state till user enters all the form information. In this case, it will be chart type and year
               State("success-pie-chart", 'figure'))
def go(dropdown_val, chil):

    d = {}

    for i, row in spacex_df.iterrows():
        if dropdown_val == "ALL":
            if row['Launch Site'] not in d:
                d[row['Launch Site']] = {"success": 0, "failure": 0}
            if row['class'] == 1:
                d[row['Launch Site']]["success"] += 1
            else:
                d[row['Launch Site']]["failure"] += 1
        else:
            if row['Launch Site'] == dropdown_val:
                if row['Launch Site'] not in d:
                    d[row['Launch Site']] = {"success": 0, "failure": 0}
                if row['class'] == 1:
                    d[row['Launch Site']]["success"] += 1
                else:
                    d[row['Launch Site']]["failure"] += 1           
    if dropdown_val == "ALL":
        for k in d.keys():
            p = (d[k]['success'] / (d[k]['success'] + d[k]['failure'])) * 100
            d[k] = p


        final = {"Site": [], "Success": [], "Failure": []}
        for dd in d.keys():
            final["Site"].append(dd)
            final["Success"].append(d[dd])
            final["Failure"].append(100-d[dd])

        ddf = pd.DataFrame(final)
        pie_fig = px.pie(ddf, values='Success', names='Site', title='Successful and Failed Launch by Launch Site')

    else:
        final = {"Sucess And Failure": ["Success", "Failure"],
                 "Data": []}
        final["Data"].append(d[dropdown_val]["success"])
        final["Data"].append(d[dropdown_val]["failure"])

        ddf = pd.DataFrame(final)
        pie_fig = px.pie(ddf, values='Data', names='Sucess And Failure', title=f'Successful and Failed for {dropdown_val}')

    print(pie_fig)
    return pie_fig

               
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
               [Input(component_id='site-dropdown', component_property='value'),
                Input(component_id='payload-slider', component_property='value')],
               # REVIEW4: Holding output state till user enters all the form information. In this case, it will be chart type and year
               State("success-payload-scatter-chart", 'figure'))
def gop(dropdown_val, slider_val, chil):

    if dropdown_val == "ALL":
        newdf = spacex_df[(spacex_df['Payload Mass (kg)'] >= slider_val[0]) & (spacex_df['Payload Mass (kg)'] <= slider_val[1])]
    else:
        newdf = spacex_df[(spacex_df['Launch Site'] == dropdown_val) & (spacex_df['Payload Mass (kg)'] >= slider_val[0]) & (spacex_df['Payload Mass (kg)'] <= slider_val[1])]
    scat = px.scatter(newdf, x="Payload Mass (kg)", y="class", color="Booster Version Category")
    return scat
# Run the app
if __name__ == '__main__':
    app.run_server()
