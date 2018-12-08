import os
import dash
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from scipy import stats 
from dash.dependencies import Input, Output, State


indicators = pd.read_csv("data/indicators-hi-iie.csv",index_col=0)
indicators_not_iie = pd.read_csv("data/indicators-not-hi-iie.csv",index_col=0)
indicators_not_iie["oil_diff%_rolling_30"]*=100
sectors = pd.read_csv("data/all-sectors-vs-sp500-iie.csv",index_col=0)
sectors_not_iie = pd.read_csv("data/all-sectors-vs-sp500-not-iie.csv",index_col=0)
correlations = pd.read_csv('data/correlation-analysis-all-sectors-vs-sp500.csv',index_col=0)
correlations_not_iie = pd.read_csv('data/correlation-analysis-all-sectors-vs-sp500-not-iie.csv',index_col=0)
# graph for difference between
temp1 = (correlations-correlations_not_iie).round(2).drop("Austria")
temp1["balanced"] = ((temp1.median_return+temp1.avg_return)/2).round(2)

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,external_stylesheets=external_stylesheet)
server = app.server

app.title = "Asset Classes"
app.layout = html.Div([
    # Analysis Text and Charts
    html.Div([
        html.H1("Asset Class Analysis",style=dict(textAlign='center')),
        html.Div([
            html.H3("Asset Class Return in Periods of High Inflation, Interest, and Energy Prices")
        ],style=dict(width="60%",marginLeft="auto",marginRight="auto")),
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

The folling chart is a pretty good summary of what changes for each asset class during hi-IIE periods.

The chart represents the difference in returns vs the S&P 500 and volatility for each asset class between periods of high interest
rates, inflation, and energy prices and periods where those three conditions are not present.

**Top left**: the asset class returns more than normal with lower volatility in hi-IIE periods. These are the asset classes we are most interested in.

**Top right**: the asset class returns more than normal but with higher volatility (aligns with theory)

**Bottom left**: the asset class returns less, but volatility is lower too (aligns with theory)

**Bottom right**: the asset class returns less but returns are more volatile 


        """)
        ],style=dict(marginLeft='auto',marginRight='auto',width='75%')),
        dcc.Graph(
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
            style=dict(border="2px solid black")
        )
    ],style=dict(marginLeft='auto',marginRight='auto',width='65%')),
    html.Hr(),
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
        ],style=dict(marginLeft='auto',marginRight='auto',width="98%")),
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
    app.run_server(threaded=True,debug=True)