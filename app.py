import os
import dash
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from scipy import stats 
from dash.dependencies import Input, Output, State
import dash_table
from plotly import tools


indicators = pd.read_csv("data/indicators-hi-iie.csv",index_col=0).round(2)
indicators_not_iie = pd.read_csv("data/indicators-not-hi-iie.csv",index_col=0).round(2)
indicators_not_iie["oil_diff%_rolling_30"]*=100
sectors = pd.read_csv("data/all-sectors-vs-sp500-iie.csv",index_col=0).round(2)
sectors_not_iie = pd.read_csv("data/all-sectors-vs-sp500-not-iie.csv",index_col=0).round(2)
correlations = pd.read_csv('data/correlation-analysis-all-sectors-vs-sp500.csv',index_col=0).round(2)
correlations_not_iie = pd.read_csv('data/correlation-analysis-all-sectors-vs-sp500-not-iie.csv',index_col=0).round(2)

# graph for difference between
temp1 = (correlations-correlations_not_iie).round(2).drop("Austria")
temp1["balanced"] = ((temp1.median_return+temp1.avg_return)/2).round(2)
# graph for frontier in hi-IIE years
temp2 = correlations.round(2)
temp2["balanced"] = ((temp2.median_return+temp2.avg_return)/2).round(2)
# graph for frontier in low-IIE years
temp3 = correlations_not_iie.drop(['Austria',"Indonesia","Mexico"]).round(2)
temp3["balanced"] = ((temp3.median_return+temp3.avg_return)/2).round(2)
# table 1
table_correlations = pd.read_csv("data/correlation-analysis-all-sectors-vs-sp500.csv").round(2)
table_correlations.columns = ["asset-class","energy","inflation","interest","stdev","avg-return","median-return"]
# table 2
table_correlations_not_iie = pd.read_csv("data/correlation-analysis-all-sectors-vs-sp500-not-iie.csv").round(2)
table_correlations_not_iie.columns = ["asset-class","energy","inflation","interest","stdev","avg-return","median-return"]
# subplots graph - selecting indicators
from recessions import recessions
indicators_all = pd.read_csv('data/indicators - oil, rollingdiff%, prime, inflation.csv',index_col=0)
recessions_fig = tools.make_subplots(rows=3,cols=1,shared_xaxes=False)
trace1 = go.Scatter(x = indicators_all.index,
                    y = indicators_all.inflation,
                    name="inflation",
                    yaxis="y1")
trace2 = go.Scatter(x = indicators_all.index,
                    y = indicators_all.prime,
                    name = 'interest',
                    yaxis="y2")
trace3 = go.Scatter(x=indicators_all.index,
                    y=indicators_all['oil_diff%_rolling_30'],
                    name='energy % of rolling avg',
                    yaxis="y3")
recessions_fig.append_trace(trace1,1,1)
recessions_fig.append_trace(trace2,2,1)
recessions_fig.append_trace(trace3,3,1)
recessions_fig['layout'].update(
    height=675,
    title = "Periods of High Interest, Inflation, & Energy",
    yaxis = dict(title = 'Inflation'),
    yaxis2 = dict(title = "Interest Rate"),
    yaxis3 = dict(title = "Energy Price"),
    legend = dict(orientation="h"),
    shapes = recessions
)

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,external_stylesheets=external_stylesheet)
server = app.server

app.title = "Asset Classes"
app.layout = html.Div([
    # Analysis Text and Charts
    html.Div([
        html.H1("Asset Class Analysis",style=dict(textAlign='center')),
        html.Div([
            html.H3("Asset Class Returns in Periods of High Inflation, Interest, and Energy Prices")
        ],style=dict(width="60%",marginLeft="auto",marginRight="auto",textAlign='center')),
        html.Div([
            dcc.Markdown("""Built with ❤️ by [Russell](https://github.com/russellromney)""")
        ],style=dict(width="60%",marginLeft="auto",marginRight="auto",textAlign='center')),
        html.Div([
            dcc.Markdown("""
---

This analysis compared asset class returns during periods of high inflation, interest, and 
energy **("hi-IIE periods")** prices with the goal of finding asset classes that do better when 
those economic conditions are present. Hi-IIE periods are defined as periods where energy costs 
(electricity and oil) exceed the 30-month rolling average by 10% or more and inflation and 
interest were higher than the preceding trend.

> **NOTE:**
> These findings' validity are limited by the small scope of the analysis -- there have only been thirteen years of hi-IIE 
> conditions -- and by the imperfect correlations due to unmeasured factors. In the regression segment, 
> the findings are useful only if the p-value is lower than about .10 (10%). The small number of data points
> is a limiting factor to tools designed for data of n > 40 for statistical significance, a threshold this
> data does not exceed in hi-IIE periods.

---

### Scroll to the bottom to see asset class correlations & charts

---

### Key Findings

1️⃣ Energy and energy-related asset classes (Chile, South Africa) outperform the market during hi-IIE periods.

2️⃣ Asset classes that can adjust to inflation outperform the market during hi-IIE periods.

3️⃣ Small-cap US stocks and some emerging markets tend to outperform the market during hi-IIE periods.

4️⃣ Defensive commodities -- e.g. gold, etc. -- outperform the market as a concrete hedge against rising prices; gold's correlation is stronger during hi-IIE periods than during lo-IIE periods.

5️⃣ Stock returns vs the S&P 500 during hi-IIE periods are very volatile, potentially negating (in increased risk) any advantage gained from selecting asset classes with higher returns.

---

#### Selecting High-IIE Periods

This chart shows how I selected high-IIE periods - selected the periods that are high in all three.
High-IIE periods are shown with shading boxes.

        """)
        ],style=dict(marginLeft='auto',marginRight='auto',width='75%')),
        html.Div([
            dcc.Graph(
                id='selecting-iie-periods-graph',
                figure = recessions_fig
            )# end of dcc.Graph
        ]),
        dcc.Markdown(
"""
---

#### Differences in Asset Class Returns vs S&P 500 in High- and Non-High-IIE Periods

The following chart is a pretty good summary of what changes for each asset class during hi-IIE periods.

The chart represents the difference in returns vs the S&P 500 and volatility for each asset class between periods of high interest
rates, inflation, and energy prices and periods where those three conditions are not present.

**Top left**: the asset class returns more than normal with lower volatility in hi-IIE periods. These are the asset classes we are most interested in.

**Top right**: the asset class returns more than normal but with higher volatility (aligns with theory)

**Bottom left**: the asset class returns less, but volatility is lower too (aligns with theory)

**Bottom right**: the asset class returns less but returns are more volatile 

"""            
        ),
        html.Div([
            dcc.Graph(
                id='differences graph',
                figure = go.Figure(
                    data = [
                        go.Scatter(
                            x=temp1.clip(-20,20,axis=0).stdev_,
                            y=temp1.clip(-20,20,axis=0).avg_return,
                            mode="markers",
                            text=["{}, {}, {}".format(col,temp1.loc[col,"stdev_"],temp1.loc[col,"avg_return"]) for col in temp1.index],
                            marker=dict(size=15),
                            hoverinfo='text'
                        )
                    ],
                    layout = go.Layout(
                        title="Return vs S&P500 and Risk: Difference Between Hi-IIE & Non-Hi-IIE Periods",
                        titlefont=dict(size=15),
                        hovermode="closest",
                        xaxis=dict(title="Difference in Volatility of Returns"),
                        yaxis=dict(title="Difference in Avg Returns vs S&P 500"),
                        height=600,
                        shapes=[        
                            {
                                'type': 'rect',
                                'xref': 'x',
                                'yref': 'y',
                                'x0': -20,
                                'y0': 0,
                                'x1': 0,
                                'y1': 20,
                                'fillcolor': 'green',
                                'opacity': .3,
                                'line': {
                                    'width': 0,
                                }
                            },
                            {
                                'type': 'rect',
                                'xref': 'x',
                                'yref': 'y',
                                'x0': 0,
                                'y0': 0,
                                'x1': 20,
                                'y1': 20,
                                'fillcolor': 'green',
                                'opacity': .085,
                                'line': {
                                    'width': 0,
                                }
                            },
                            {
                                'type': 'rect',
                                'xref': 'x',
                                'yref': 'y',
                                'x0': 0,
                                'y0': -13.5,
                                'x1': 20,
                                'y1': 0,
                                'fillcolor': 'red',
                                'opacity': .3,
                                'line': {
                                    'width': 0,
                                }
                            },
                            {
                                'type': 'rect',
                                'xref': 'x',
                                'yref': 'y',
                                'x0': -20,
                                'y0': -13.5,
                                'x1': 0,
                                'y1': 0,
                                'fillcolor': 'red',
                                'opacity': .085,
                                'line': {
                                    'width': 0,
                                }
                            }
                        ]
                    )
                ),
            )
        ]),
        html.Div([
            dcc.Markdown(
"""
---

#### Risk - Return Frontier During High-IIE Periods

This chart is shows the risk - return frontier for each sector during periods where High-IIE conditions
are present. Outlier values are capped on the edges to preserve reasonable perspective; 
hovering over a data point shows its true value. **Returns are shown relative to the S&P 500**.

High-IIE periods display high volatility for many asset classes, especially positive. Many asset classes 
perform well, but positive outliers perform very well.

**Returns** : 
* Median-Balanced Average: **{}** 
* Average: {}
* Median: {}

**Volatility**
* Median-Balanced Average: **{}** 
* Average: {}
* Median: {}
""".format( 
        round(temp2.balanced.mean(),2),
        round(correlations.avg_return.mean(),2),
        round(correlations.avg_return.median(),2),
        round((correlations.stdev_.mean()+correlations.stdev_.median())/2,2),        
        round(correlations.stdev_.mean(),2),
        round(correlations.stdev_.median(),2),


    ))
        ],style=dict(marginLeft='auto',marginRight='auto',width='75%')),
        html.Div([
            dcc.Graph(
                id='high-iie-returns-graph',
                figure = go.Figure(
                    data = [
                        go.Scatter(
                            x=temp2.stdev_.clip_upper(30,axis=0),
                            y=temp2.balanced.clip_upper(30,axis=0),
                            mode="markers",
                            text=["{}, {}, {}".format(col,temp2.loc[col,"stdev_"],temp2.loc[col,"balanced"]) for col in temp2.index],
                            marker=dict(size=15),
                            hoverinfo='text'
                        )
                    ],
                    layout = go.Layout(
                        title="Return vs Volatility - Frontier During High-IIE Periods",
                        hovermode="closest",
                        xaxis=dict(title="Volatility"),
                        yaxis=dict(title="Return vs S&P 500"),
                        height=600,
                        shapes=[
                            {
                                'type': 'rect',
                                'xref': 'paper',
                                'yref': 'y',
                                'x0': 0,
                                'y0': 0,
                                'x1': 1,
                                'y1': 30,
                                'fillcolor': 'green',
                                'opacity': .085,
                                'line': {
                                    'width': 0,
                                }
                            },
                            {
                                'type': 'rect',
                                'xref': 'paper',
                                'yref': 'y',
                                'x0': 0,
                                'y0': -12,
                                'x1': 1,
                                'y1': 0,
                                'fillcolor': 'red',
                                'opacity': .085,
                                'line': {
                                    'width': 0,
                                }
                            },
                        ] # end of shapes
                    ), # end of go.Layout            
                ) # end of go.Figure
            )# end of dcc.Graph
        ]),
        html.Div([
            dcc.Markdown(
"""
---

#### Risk - Return Frontier During Non-High-IIE Periods

It's useful to compare the frontier both with and without the High-IIE conditions. Here is the same
chart, but **excluding** periods in which High-IIE conditions were present. Again, outlier values are
capped on the edges to preserve reasonable perspective; hovering over a data point shows
its true value. 

This chart shows notably less positive volatility.

**Returns** : 
* Median-Balanced Average: **{}** 
* Average: {}
* Median: {}

**Volatility**
* Median-Balanced Average: **{}** 
* Average: {}
* Median: {}
""".format( 
        round(temp3.balanced.mean(),2),
        round(correlations_not_iie.avg_return.mean(),2),
        round(correlations_not_iie.avg_return.median(),2),
        round((correlations_not_iie.stdev_.mean()+correlations_not_iie.stdev_.median())/2,2),
        round(correlations_not_iie.stdev_.mean(),2),
        round(correlations_not_iie.stdev_.median(),2),

    ))
        ],style=dict(width="75%",marginLeft='auto',marginRight='auto')),

        html.Div([
            dcc.Graph(
                id='not-high-iie-returns-graph',
                figure = go.Figure(
                    data = [
                        go.Scatter(
                            x=temp3.stdev_.clip_upper(30,axis=0),
                            y=temp3.balanced.clip_upper(30,axis=0),
                            mode="markers",
                            text=["{}, {}, {}".format(col,temp3.loc[col,"stdev_"],temp3.loc[col,"balanced"]) for col in temp3.index],
                            marker=dict(size=15),
                            hoverinfo='text'
                        )
                    ],
                    layout = go.Layout(
                        title="Return and Risk - Frontier During Non-High-IIE Periods",
                        hovermode="closest",
                        xaxis=dict(title="Volatility"),
                        yaxis=dict(title="Return vs S&P 500"),
                        height=600,
                        shapes=[
                            {
                                'type': 'rect',
                                'xref': 'paper',
                                'yref': 'y',
                                'x0': 0,
                                'y0': 0,
                                'x1': 1,
                                'y1': 30,
                                'fillcolor': 'green',
                                'opacity': .085,
                                'line': {
                                    'width': 0,
                                }
                            },
                            {
                                'type': 'rect',
                                'xref': 'paper',
                                'yref': 'y',
                                'x0': 0,
                                'y0': -12,
                                'x1': 1,
                                'y1': 0,
                                'fillcolor': 'red',
                                'opacity': .085,
                                'line': {
                                    'width': 0,
                                }
                            },
                        ] # end of shapes
                    ), # end of go.Layout            
                ) # end of go.Figure
            )# end of dcc.Graph
        ]),
    ],style=dict(marginLeft='auto',marginRight='auto',width='65%')), # end of analysis div
    html.Hr(),
    # data tables
    html.Div([
        html.H2("Correlation Data Tables",style=dict(textAlign='center')),
        html.Div([
            dcc.Markdown(
"""
Play around with the correlation data yourself! Scroll down or sideways in the table, sort values, 
or filter. There is a filtering row at the top of each table. There is a special filtering langauge
for this.

Example filter input: 
* Greater than 0.5: `> num(.5)`
* Equal to 0.5: `eq num(.5)`
* Equal to "Australia": `eq "Australia"`
""")
        ],style=dict(width="48.75%",marginLeft='auto',marginRight='auto')),
        # first table
        html.Div([
            html.H4("Asset Class correlations in High-IEE periods"),
            dash_table.DataTable(
                id='iie-correlations-table',
                columns=[{"name":i,"id":i,"deletable":False} for i in table_correlations],
                data = table_correlations.to_dict("rows"),
                filtering=True,
                editable=False,
                sorting=True,
                sorting_type="multi",
                #row_selectable='multi',
                row_deletable=False,
                selected_rows=[] ,
                style_table=dict(
                    overflowY="auto",overflowX='auto',height='500px'
                ),
                style_cell=dict(maxWidth='175px')
            ),
            html.Div(id='iie-datatable-interactivity-container')
        ],style=dict(width="49%",marginLeft="auto",marginRight='auto',display='inline-block',padding=".5%")),
        # second table
        html.Div([
            html.H4("Asset Class correlations in non-High-IEE periods"),
            dash_table.DataTable(
                id='not-iie-correlations-table',
                columns=[{"name":i,"id":i,"deletable":False} for i in table_correlations_not_iie],
                data = table_correlations_not_iie.to_dict("rows"),
                filtering=True,
                editable=False,
                sorting=True,
                sorting_type="multi",
                #row_selectable='multi',
                row_deletable=False,
                selected_rows=[],
                style_table=dict(
                    overflowY="auto",overflowX='auto',height="500px"
                ),
                style_cell=dict(maxWidth='175px')      
            ),
            html.Div(id='not-iie-datatable-interactivity-container')
        ],style=dict(width="49%",marginLeft="auto",marginRight='auto',display='inline-block',padding=".5%")),
    ],style=dict(paddingBottom='100px')),
    html.Hr(),
    # interactive regression
    html.Div([
        # dropdown
        html.Div([
            html.H2(
                "Interactive Asset Class Regression in hi-IIE and non-hi-IIE periods",
                style=dict(textAlign="center")
            ),
            html.Div([
                dcc.Dropdown(
                    id = 'sector-dropdown',
                    options = [dict(label=col,value=col) for col in list(sectors.columns)],
                    value = "Total US",
                    style=dict(fontSize="20px")
                )
            ],style=dict(width="400px",marginLeft="auto",marginRight="auto"))
        ],style=dict(marginLeft='auto',marginRight='auto',width="100%")),
        # graph in hi-IIE periods
        html.Div([
            html.Div(
                children="",
                id = 'correlation-div',
                style=dict(marginLeft='auto',marginRight='auto',textAlign='center')),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id = 'sector-vs-interest'
                    )
                ],style=dict(display='inline-block',width="33%")),
                html.Div([
                    dcc.Graph(
                        id = 'sector-vs-inflation'
                    )
                ],style=dict(display='inline-block',width="33%")),
                html.Div([
                    dcc.Graph(
                        id = 'sector-vs-oil'
                    )
                ],style=dict(display='inline-block',width="33%")),
            ]),
            # graph in non-hi-IIE periods?
            html.Div([
                html.Div([
                    dcc.Graph(
                        id = 'sector-vs-interest-other'
                    )
                ],style=dict(display='inline-block',width="33%")),
                html.Div([
                    dcc.Graph(
                        id = 'sector-vs-inflation-other'
                    )
                ],style=dict(display='inline-block',width="33%")),
                html.Div([
                    dcc.Graph(
                        id = 'sector-vs-oil-other'
                    )
                ],style=dict(display='inline-block',width="33%")),
            ])
        ],style=dict(width="100%",marginLeft='auto',marginRight='auto'))
    ],style=dict(width="100%",marginLeft='auto',marginRight='auto')),
    html.Div([""
    ])
])









@app.callback(
    Output('correlation-div','children'),
    [Input('sector-dropdown','value')])
def update_correlation_div(sector):
    return dcc.Markdown(
"""**Correlations in Hi-IIE Periods**: Energy: {} {} | Inflation: {} {} | Interest: {} {}
""".format(
            round(correlations.oil[sector],2), "**HIGH**" if abs(correlations.oil[sector])>.35 else "",
            round(correlations.inflation[sector],2), "**HIGH**" if abs(correlations.inflation[sector])>.35 else "",
            round(correlations.interest[sector],2), "**HIGH**" if abs(correlations.interest[sector])>.35 else ""
        )
    )


@app.callback(
    Output('sector-vs-oil','figure'),
    [Input('sector-dropdown','value')])
def sector_vs_oil_not_iie(sector):
    xi = indicators["oil_diff%_rolling_30"]
    y = sectors[sector]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    dots = go.Scatter(
        x = xi,
        y = y,
        mode = 'markers',
        name = "Data",
        text = [x[:4] for x in y.index],
    )
    line = go.Scatter(
        x = xi,
        y = slope*xi+intercept,
        mode = 'lines',
        name = "Fit"
    )
    data = [dots,line]
    layout = go.Layout(
        title="Hi-IIE: "+sector+" vs Relative Energy Price",
        titlefont=dict(size=14),
        height=350,
        xaxis=dict(
            title="Energy Price as % of 30-month Rolling Avg",
            titlefont=dict(size=12),
            automargin=True),
        yaxis=dict(
            title="Return vs S%P 500",
            titlefont=dict(size=12)),
        annotations=[
            dict(
                x=55,
                showarrow=False,
                y=-1,
                xref='x',
                yref='y',
                text='p-val: {} slope: {}'.format(round(p_value,2),round(slope,2)),
            ),
        ],
        margin=go.layout.Margin(
            l=30,
            b=30,
            t=30,
            r=60,
            pad=4
        ),
        hovermode='closest'
    )
    return go.Figure(data,layout)
@app.callback(
    Output('sector-vs-interest','figure'),
    [Input('sector-dropdown','value')])
def sector_vs_interest_not_iie(sector):
    xi = indicators["prime"]
    y = sectors[sector]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    dots = go.Scatter(
        x = xi,
        y = y,
        mode = 'markers',
        name = "Data",
        text = [x[:4] for x in y.index]
    )
    line = go.Scatter(
        x = xi,
        y = slope*xi+intercept,
        mode = 'lines',
        name = "Fit"
    )
    data = [dots,line]
    layout = go.Layout(
        title="Hi-IIE: "+sector+" vs Interest Rate",
        titlefont=dict(size=14),
        height=350,
        xaxis=dict(
            title="Interest Rate",
            titlefont=dict(size=12),
            automargin=True),
        yaxis=dict(
            title="Return vs S%P 500",
            titlefont=dict(size=12),
            automargin=True),
        annotations=[
            dict(
                x=20,
                showarrow=False,
                y=-1,
                xref='x',
                yref='y',
                text='p-val: {} slope: {}'.format(round(p_value,2),round(slope,2)),
            )
        ],
        hovermode="closest",
        margin=go.layout.Margin(
            l=30,
            b=30,
            t=30,
            r=60,
            pad=4
        ),

    )
    return go.Figure(data,layout)
@app.callback(
    Output('sector-vs-inflation','figure'),
    [Input('sector-dropdown','value')])
def sector_vs_inflation_not_iie(sector):
    xi = indicators["inflation"]
    y = sectors[sector]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    dots = go.Scatter(
        x = xi,
        y = y,
        mode = 'markers',
        name = "Data",
        text = [x[:4] for x in y.index]
    )
    line = go.Scatter(
        x = xi,
        y = slope*xi+intercept,
        mode = 'lines',
        name = "Fit"
    )
    data = [dots,line]
    layout = go.Layout(
        title="Hi-IIE: "+sector+" vs Inflation Rate",
        titlefont=dict(size=14),
        height=350,
        xaxis=dict(
            title="Inflation Rate",
            titlefont=dict(size=12),
            automargin=True),
        yaxis=dict(
            title="Return vs S%P 500",
            titlefont=dict(size=12),
            automargin=True),
        annotations=[
            dict(
                x=12,
                showarrow=False,
                y=-1,
                xref='x',
                yref='y',
                text='p-val: {} slope: {}'.format(round(p_value,2),round(slope,2)),
            )
        ],
        hovermode="closest",
        margin=go.layout.Margin(
            l=30,
            b=30,
            t=30,
            r=60,
            pad=4
        ),
    )
    return go.Figure(data,layout)














@app.callback(
    Output('sector-vs-oil-other','figure'),
    [Input('sector-dropdown','value')])
def sector_vs_oil(sector):
    xi = indicators_not_iie["oil_diff%_rolling_30"]
    y = sectors_not_iie[sector]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    dots = go.Scatter(
        x = xi,
        y = y,
        mode = 'markers',
        name = "Data",
        text = [x[:4] for x in y.index],
    )
    line = go.Scatter(
        x = xi,
        y = slope*xi+intercept,
        mode = 'lines',
        name = "Fit"
    )
    data = [dots,line]
    layout = go.Layout(
        title="Not-Hi-IIE: "+sector+" vs Relative Energy Price",
        titlefont=dict(size=14),
        height=350,
        xaxis=dict(
            title="Energy Price as % of 30-month Rolling Avg",
            titlefont=dict(size=12),
            automargin=True),
        yaxis=dict(
            title="Return vs S%P 500",
            titlefont=dict(size=12),
            automargin=True),
        annotations=[
            dict(
                x=55,
                showarrow=False,
                y=-1,
                xref='x',
                yref='y',
                text='p-val: {} slope: {}'.format(round(p_value,2),round(slope,2)),
            ),
        ],
        hovermode='closest',
        margin=go.layout.Margin(
            l=30,
            b=30,
            t=30,
            r=60,
            pad=4
        ),
    )
    return go.Figure(data,layout)
@app.callback(
    Output('sector-vs-interest-other','figure'),
    [Input('sector-dropdown','value')])
def sector_vs_interest(sector):
    xi = indicators_not_iie["prime"]
    y = sectors_not_iie[sector]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    dots = go.Scatter(
        x = xi,
        y = y,
        mode = 'markers',
        name = "Data",
        text = [x[:4] for x in y.index]
    )
    line = go.Scatter(
        x = xi,
        y = slope*xi+intercept,
        mode = 'lines',
        name = "Fit"
    )
    data = [dots,line]
    layout = go.Layout(
        title="Not-Hi-IIE: "+sector+" vs Interest Rate",
        titlefont=dict(size=14),
        height=350,
        xaxis=dict(
            title="Interest Rate",
            titlefont=dict(size=12),
            automargin=True),
        yaxis=dict(
            title="Return vs S%P 500",
            titlefont=dict(size=12),
            automargin=True),
        annotations=[
            dict(
                x=12,
                showarrow=False,
                y=-1,
                xref='x',
                yref='y',
                text='p-val: {} slope: {}'.format(round(p_value,2),round(slope,2)),
            )
        ],
        hovermode="closest",
        margin=go.layout.Margin(
            l=30,
            b=30,
            t=30,
            r=60,
            pad=4
        ),

    )
    return go.Figure(data,layout)
@app.callback(
    Output('sector-vs-inflation-other','figure'),
    [Input('sector-dropdown','value')])
def sector_vs_inflation(sector):
    xi = indicators_not_iie["inflation"]
    y = sectors_not_iie[sector]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    dots = go.Scatter(
        x = xi,
        y = y,
        mode = 'markers',
        name = "Data",
        text = [x[:4] for x in y.index]
    )
    line = go.Scatter(
        x = xi,
        y = slope*xi+intercept,
        mode = 'lines',
        name = "Fit"
    )
    data = [dots,line]
    layout = go.Layout(
        title="Not-Hi-IIE: "+sector+" vs Inflation Rate",
        titlefont=dict(size=14),
        height=350,
        xaxis=dict(
            title="Inflation Rate",
            titlefont=dict(size=12),
            automargin=True),
        yaxis=dict(
            title="Return vs S%P 500",
            titlefont=dict(size=12),
            automargin=True),
        annotations=[
            dict(
                x=5,
                showarrow=False,
                y=-1,
                xref='x',
                yref='y',
                text='p-val: {} slope: {}'.format(round(p_value,2),round(slope,2)),
            )
        ],
        hovermode="closest",
        margin=go.layout.Margin(
            l=30,
            b=30,
            t=30,
            r=60,
            pad=4
        ),
    )
    return go.Figure(data,layout)

















if __name__ == '__main__':
    app.run_server(threaded=True,debug=False)