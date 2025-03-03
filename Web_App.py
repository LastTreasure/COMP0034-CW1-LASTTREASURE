#Import Packages
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import os

#Clean Data
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, 'MPS Borough Level Crime (Historical).csv')
df = pd.read_csv(csv_path)

df = df.drop(columns=["MajorText"])
df["BoroughName"]=pd.Series(df["BoroughName"]).str.upper()
df["MinorText"]=pd.Series(df["MinorText"]).str.lower()

date_columns = df.columns[2:]
new_date_columns = pd.to_datetime(date_columns, format='%Y%m', errors='coerce').strftime('%Y-%m')
df.columns = list(df.columns[:2]) + list(new_date_columns)

melted_df = df.melt(id_vars=["BoroughName", "MinorText"], var_name="Date", value_name="Number of Crimes")
melted_df = melted_df[["Date", "BoroughName", "MinorText", "Number of Crimes"]]
# print(melted_df)
# output_file = "Processed_Crime_Data.xlsx"
# melted_df.to_excel(output_file, index=False)

melted_df1 = melted_df.copy()
melted_df1['Year'] = pd.to_datetime(melted_df['Date'], format='%Y-%m',errors='coerce').dt.year
melted_df1 = melted_df1.drop(columns=['Date'])
cols = ['Year', 'BoroughName', 'MinorText', 'Number of Crimes']
melted_df1 = melted_df1[cols]
aggregated_df = melted_df1.groupby(['BoroughName', 'MinorText', 'Year'], as_index=False)['Number of Crimes'].sum()
#print(aggregated_df.head())
#output_file = "Processed_Crime_Data2.xlsx"
#aggregated_df.to_excel(output_file, index=False)

borough_year_df = aggregated_df.groupby(['BoroughName', 'Year'], as_index=False)['Number of Crimes'].sum()

search_df = melted_df.copy()
search_df["Date"] = search_df["Date"].astype(str)
search_df["Year"] = search_df["Date"].str.split("-").str[0]
search_df["Month"] = search_df["Date"].str.split("-").str[1]
search_cols = ['Year', 'Month', 'BoroughName', 'MinorText', 'Number of Crimes']
search_df = search_df[search_cols]
# print(search_df)
# output_file = "Processed_Crime_Data3.xlsx"
# search_df.to_excel(output_file, index=False)

#Overall Settings
MAX_YR = aggregated_df["Year"].max()
MIN_YR = aggregated_df["Year"].min()
START_YR = 2010
borough_list = sorted(aggregated_df["BoroughName"].unique())

stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME])

#Components in Tab1
introduction_text = dcc.Markdown(
    """
    > In this web app, we try to analyze the number of crimes happening in different **boroughs** at different **time**
    in three ways shown **in the rest four tabs** respectively.

    >The first one is **a line chart** depicting the change of number of a certain crime in a certain borough over time.
    Users can choose their required boroughs and crime with using the dropdown function to illustrate the data in the chart.
    Please notice that, users can choose many boroughs, but only one crime at the same time. This design is to ensure the
    graph presented is clear enough. With this line chart, users can easily view the change of number of a certain crime
    over time, with making comparison among different boroughs.

    >The second one is **a pie chart** demonstrating the proportion of different crimes occupying in a certain borough in a
    certain year. Users can use the two sliders to choose the borough and year which they are interested in respectively.
    As the boroughs' names are too long to be displayed under each choice point in the slider, we number each borough name and
    use the serial number instead. The table below shows the borough corresponding to each serial number. With this pie chart,
    users can easily view what kind of crime happened most in this borough, with seeing their ratios clearly.
    
    >The third one is **a bar chart** illustrating the total number of all crimes happening in different boroughs in a 
    certain year. By selecting the year the user wants to go through, boroughs will be automatically sorted from most crimes to 
    least crimes. Users can easily and conveniently identify which borough has good public security and which one does not, as well
    as making comparison among them. 

    >The fourth one is **a search tool**. Although graphs in the previous two tabs have already been able to reflect many practical
    outcomes, users may still be willing to find very specific data to do further customized analysis. In this tab, users
    can enter the year they want to go through, the month the want to go through, the borough they want to go through, and
    the crime they want to go through until they filter out the data they really want.
    """,
    id="introduction-text",
    style={
        "fontSize": "22px",
        "marginTop": "25px",
        "textAlign": "left",
        "width": "95%",
        "marginLeft": "2.5%"
    }
)

#Components in Tab2
fig = px.line(data_frame=melted_df, x="Date", y="Number of Crimes", color="BoroughName", log_y=True)

line_chart_content = html.Div(
    [
        html.Div(
                    html.H1(
                        "Time-Dependent Number of Certain Crimes in Certain Boroughs",
                        style={
                            "textAlign": "center",
                            "marginTop": "15px"
                        }
                    ),
                    className="row",
        ),

        html.Div(dcc.Graph(id="line-chart", figure=fig), className="row",
                 style={
                     "width":"90%",
                     "marginLeft":"5%"
                }
        ),

        html.Div(
            dcc.Markdown(
                        """
                        **Crime Change in Time** is the analysis towards the time-dependent variation of number of a certain crime happening
                        in different boroughs. Please select the certain crime and corresponding boroughs you are interested in.
                        """
            ),
            style = {
                    "marginTop": "20px",
                    "textAlign": "left",
                    "width": "90%",
                    "marginLeft": "6%"
                },
        ),

        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="Location",
                            multi=True,
                            options=[
                                {"label":x, "value":x}
                                for x in sorted(df["BoroughName"].unique())
                            ],
                            value=None,
                            placeholder="Select Boroughs",
                            clearable=True,
                            style={"color":"blue","backgroundColor":"lightyellow", "fontSize":"20px","lineHeight":"25px",
                                   "padding":"5px"}
                        ),
                        width=7
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="Crime-Types",
                            multi=False,
                            options=[
                                {"label":x, "value":x}
                                for x in sorted(df["MinorText"].unique())
                            ],
                            value=None,
                            placeholder="Select a Crime",
                            clearable=True,
                            style={"color":"blue","backgroundColor":"lightyellow", "fontSize":"20px","lineHeight":"25px","padding":"5px"}
                        ),
                        width=4
                    ),
                ],
            ),
            className="row",
            style={
                "marginLeft": "5%",
                "width": "90%",
            },
        ),
    ]
)

#Components in Tab3
slider_card = dbc.Card(
    [
        html.H4("Year Selection:", className="card-title",),
        html.Div(
            dcc.Slider(
                id="year-slider",
                marks={i:f"{i}" for i in range(MIN_YR, MAX_YR+1)},
                min=MIN_YR,
                max=MAX_YR,
                step=1,
                value=START_YR,
                included=False,
            ),
            style={"width": "90%", "margin": "auto"},
        ),

        html.H4("Borough Selection:", className="card-title mt-3",),
        html.Div(
            dcc.Slider(
                id="borough-slider",
                marks={i: str(i+1) for i in range(len(borough_list))},
                min=0,
                max=len(borough_list) - 1,
                step=1,
                value=0,
                included=False,
            ),
            style={"width": "90%", "margin": "auto"},
        ),
    ],
    body=True,
    className="mt-4",
    style={"width": "90%", "margin": "auto"},
)

crime_distribution_content = html.Div(
    [
        html.H2(
            "The Proportion of Crimes in a Certain Borough at a Certain Time",
            className="text-center bg-primary text-white p-2"
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id="allocation_pie_chart",
                    style={"height":"600px", "width":"90%"},
                ),
                width=12,
                className="d-flex justify-content-center"
            )
        ),
        dbc.Row(
            dbc.Col(
                slider_card,
                width=12,
                className="d-flex justify-content-center"
            )
        ),
    ]
)

borough_serial_table = html.Div(
            dbc.Table(
                [
                    html.Thead(
                        html.Tr([html.Th("Serial Number"), html.Th("Borough")])
                    ),
                    html.Tbody(
                        [html.Tr([html.Td(str(i+1)), html.Td(borough)]) for i, borough in enumerate(borough_list)]
                    )
                ],
                bordered=True,
                striped=True,
                hover=True,
                size="sm",
                style={"margin": "auto", "width": "90%"},
                id="serial-table"
            ),
            style={"margin-top": "10px"}
)

crime_distribution_text = dcc.Markdown(
    """
    > ** Crime Distribution ** is the analysis towards the proportion of different types of crimes being commited in a certain
    city at a certain year. Choose the selection you want to look through.
    """,
    style = {
        "marginTop": "20px",
        "textAlign": "left",
        "width": "90%",
        "marginLeft": "5%"
    },
)

#Components in Tab4
year_options = [{'label': str(year), 'value': year} for year in range(MIN_YR, MAX_YR+1)]

borough_bar_chart = dcc.Graph(id="borough-bar-chart",style={"height": "600px", "width":"100%",  "margin":"auto", "padding":"40px"})

borough_tab_content = html.Div(
    [
        html.H2("Total Crimes per Borough by Year", style={"padding": "10px", "textAlign": "center"}),
        html.Div(
            [
                html.Label("Select Year:"),
                html.Div(
                    dcc.Dropdown(
                        id="year-bar-dropdown",
                        options=year_options,
                        value=START_YR,
                        clearable=False,
                        style={"width": "30%", "leftMargin": "1000px"}
                    )
                )
            ],
            style={
                                    "textAlign": "left",
                                    "display": "block",
                                    "marginBottom": "5px",
                                    "marginLeft": "40px"
            }

        ),
        borough_bar_chart
    ]
)

#Components in Tab5
input_year = dbc.InputGroup(
    [
        dbc.InputGroupText("Year"),
        dbc.Input(
            id="year-input",
            placeholder=f"min {MIN_YR} max {MAX_YR}",
            type="number",
            min=MIN_YR,
            max=MAX_YR
        )
    ],
    className="mb-3",
)

input_month = dbc.InputGroup(
    [
        dbc.InputGroupText("Month"),
        dbc.Input(
            id="month-input",
            placeholder=f"min 1 max 12",
            type="number",
            min=1,
            max=12
        )
    ],
    className="mb-3",
)

input_borough = dbc.InputGroup(
    [
        dbc.InputGroupText("Borough"),
        dbc.Input(
            id="borough-input",
            type="text",
        )
    ],
    className="mb-3",
)

input_crime = dbc.InputGroup(
    [
        dbc.InputGroupText("Crime"),
        dbc.Input(
            id="crime-input",
            type="text",
        )
    ],
    className="mb-3",
)

input_groups = html.Div(
    [
        input_year, input_month, input_borough, input_crime
    ],
    style={
        "marginTop": "0px",
        "textAlign": "left",
        "width": "94%",
        "marginLeft": "3%"
    },
)

search_text = dcc.Markdown(
    """
        The search function is aiming at help users find the data efficiently and accurately.
        Please fill in the information you require to get more specific customized data.
    """,
    style={
        "marginTop": "15px",
        "textAlign": "left",
        "marginLeft": "2%"
    }
)

search_results = html.Div(
    id="search-results",
    style={"marginTop": "30px"}
)

#Tabs Structure
tabs = dbc.Tabs(
    [
        dbc.Tab(
            introduction_text,
            tab_id="tab1",
            label="Introduction"
        ),

        dbc.Tab(
            [
                line_chart_content
            ],
            tab_id="tab2",
            label="Crime Change in Time"
        ),

        dbc.Tab(
            [
                crime_distribution_content,
                crime_distribution_text,
                borough_serial_table
            ],
            tab_id="tab3",
            label="Crime Distribution",
        ),

        dbc.Tab(
                    [borough_tab_content],
                    tab_id="tab4",
                    label="Boroughs Comparison",
                ),

        dbc.Tab(
            [
                search_text,
                input_groups,
                search_results
            ],
            tab_id="tab5",
            label="Search",
        ),
    ],
    id="tabs",
    active_tab="tab1",
)

#Layout and Style
app.layout = dbc.Container(
    [
        dbc.Row(
            html.H1("Crimes in Boroughs Data Analysis", className="d-flex justify-content-center",
                    style={"font-size": "3.5rem", "margin": "1.2rem"}
            ),
        ),
        dbc.Row(
            dbc.Col(tabs, width=12)
        ),
    ],
    fluid=True,
)

#Define Pie Chart
def make_pie(slider_input, title):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=aggregated_df.MinorText(),
                values=slider_input,
                textinfo="label+percentage",
                textposition="inside",
                sort=False,
                hoverinfo="none",
            )
        ]
    )

#Tab2 Return
@app.callback(
    Output(component_id="line-chart", component_property="figure"),
    [Input("Location", "value"), Input("Crime-Types", "value")]
)

def update_line_chart(chosen_value1, chosen_value2):
    print(f"Values chosen by user:{chosen_value1,chosen_value2}")

    if not chosen_value1 or not chosen_value2:
        return px.line(title="No Data Selected")
    else:
        df_filtered = melted_df[
            (melted_df["BoroughName"].isin(chosen_value1)) &
            (melted_df["MinorText"] == chosen_value2)
            ]
        fig=px.line(
            data_frame=df_filtered,
            x="Date",
            y="Number of Crimes",
            color="BoroughName",
            log_y=True,
            labels={
                "Number of Crimes":"Amount",
                "BoroughName":"Borough",
                "Date":"Date",
                "MinorText":"Crime",
            },
        )
        return fig

#Tab3 Return
@app.callback(
    Output(component_id="allocation_pie_chart", component_property="figure"),
    Input(component_id="year-slider", component_property="value"),
    Input(component_id="borough-slider", component_property="value"),
)

def update_pie(selected_year, borough_index):
    borough_index = int(borough_index)
    selected_borough = borough_list[borough_index]
    filtered_df = aggregated_df[(aggregated_df["Year"] == selected_year) &
                                (aggregated_df["BoroughName"] == selected_borough)]
    if filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(title=f"No data available for {selected_borough} in {selected_year}")
    else:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=filtered_df["MinorText"],
                    values=filtered_df["Number of Crimes"],
                    textinfo="label+percent",
                    textposition="inside",
                    sort=False,
                    hoverinfo="none",
                )
            ]
        )
        fig.update_layout(title=f"Crime Distribution in {selected_borough} for {selected_year}")
    return fig

#Tab4 Return
@app.callback(
    Output("borough-bar-chart", "figure"),
    [Input("year-bar-dropdown", "value")]
)
def update_borough_bar_chart(selected_year):
    df_year = borough_year_df[borough_year_df["Year"] == selected_year]
    df_year = df_year.sort_values(by="Number of Crimes", ascending=False)
    fig = go.Figure(
        data=[go.Bar(
            x=df_year["BoroughName"],
            y=df_year["Number of Crimes"],
            marker_color='lightsalmon'
        )]
    )
    fig.update_layout(
        title=f"Total Crimes per Borough in {selected_year}",
        xaxis_title="Boroughs   ",
        yaxis_title="Total Crimes",
        xaxis={'categoryorder': 'total descending'}
    )
    return fig

#Tab5 Return
@app.callback(
    Output("search-results", "children"),
    [Input("year-input", "value"),
     Input("month-input", "value"),
     Input("borough-input", "value"),
     Input("crime-input", "value")]
)

def update_search(year, month, borough, crime):
    filtered = search_df.copy()
    filtered["Type of Crimes"]=filtered["MinorText"]
    filtered.drop(columns=["MinorText"], inplace=True)
    if year:
        filtered = filtered[filtered["Year"] == str(year)]
    if month:
        month_str = f"{int(month):02d}"
        filtered = filtered[filtered["Month"] == month_str]
    if borough:
        filtered = filtered[filtered["BoroughName"] == borough.upper()]
    if crime:
        filtered = filtered[filtered["Type of Crimes"] == crime.lower()]
    if filtered.empty:
        return "No data found."

    result_df = filtered[["Year", "Month", "BoroughName", "Type of Crimes", "Number of Crimes"]]

    search_table = dash_table.DataTable(
        data=result_df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in result_df.columns],
        page_size=10,
        style_table={
            "overflowX": "auto",
            "width": "97%",
            "margin": "auto"
        }
    )
    return search_table



#App Run
if __name__ == "__main__":
    app.run_server(debug=True, port=8052)