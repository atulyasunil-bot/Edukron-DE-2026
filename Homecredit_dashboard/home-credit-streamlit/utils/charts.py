"""
charts.py
----------
Thin wrappers around Plotly Express / Graph Objects so pages stay short and
every chart shares consistent styling.
"""

import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_white"
COLOR_SEQ = px.colors.qualitative.Set2


def bar(df, x, y=None, title="", horizontal=False, color=None, text_auto=True):
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", title=title, color=color,
                     color_discrete_sequence=COLOR_SEQ, text_auto=text_auto)
    else:
        fig = px.bar(df, x=x, y=y, title=title, color=color,
                     color_discrete_sequence=COLOR_SEQ, text_auto=text_auto)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def histogram(df, x, title="", nbins=40, color=None):
    fig = px.histogram(df, x=x, nbins=nbins, title=title, color=color, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def box(df, x=None, y=None, title="", color=None):
    fig = px.box(df, x=x, y=y, title=title, color=color, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def donut(df, names, values, title=""):
    fig = px.pie(df, names=names, values=values, hole=0.55, title=title, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def scatter(df, x, y, title="", color=None, trendline=None):
    fig = px.scatter(df, x=x, y=y, title=title, color=color, opacity=0.5,
                      color_discrete_sequence=COLOR_SEQ, trendline=trendline)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def line(df, x, y, title="", color=None):
    fig = px.line(df, x=x, y=y, title=title, color=color, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def treemap(df, path, values, title=""):
    fig = px.treemap(df, path=path, values=values, title=title, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def heatmap(matrix, title="", x_labels=None, y_labels=None):
    fig = go.Figure(data=go.Heatmap(z=matrix, x=x_labels, y=y_labels, colorscale="RdBu_r", zmid=0))
    fig.update_layout(title=title, template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def gauge(value, title="", max_value=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={"axis": {"range": [0, max_value]}, "bar": {"color": "#2E7D32"}},
    ))
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10, l=20, r=20), height=280)
    return fig


def grouped_bar(df, x, y, color, title=""):
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", title=title, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig


def stacked_bar(df, x, y, color, title=""):
    fig = px.bar(df, x=x, y=y, color=color, barmode="stack", title=title, color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(template=TEMPLATE, margin=dict(t=50, b=10))
    return fig
