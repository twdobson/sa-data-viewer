# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from app.models import db
from app.models.geospatial import Province
from app.views.components import sidebar
from plotly.offline import iplot
from shapely.geometry import LineString, MultiLineString
from sqlalchemy import select

pd.options.display.max_rows = 500
pd.options.display.max_columns = 5100
pd.options.display.width = 2000
pd.options.display.max_colwidth = 1000

# from choropleth_colors import *   #my colorscales for choropleths

mapboxt = open(".mapbox_token").read().rstrip()  # my mapbox_access_token

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


def shapefile_to_geojson(gdf, index_list, geo_names_col, tolerance=0.01):
    # gdf - geopandas dataframe containing the geometry column and values to be mapped to a colorscale
    # index_list - a sublist of list(gdf.index)  or gdf.index  for all data
    # level - int that gives the level in the shapefile
    # tolerance - float parameter to set the Polygon/MultiPolygon degree of simplification

    # returns a geojson type dict

    geo_names = list(gdf[geo_names_col])
    geojson = {'type': 'FeatureCollection', 'features': []}
    for index in index_list:
        geo = gdf['geometry'][index].simplify(tolerance)

        if isinstance(geo.boundary, LineString):
            gtype = 'Polygon'
            bcoords = np.dstack(geo.boundary.coords.xy).tolist()

        elif isinstance(geo.boundary, MultiLineString):
            gtype = 'MultiPolygon'
            bcoords = []
            for b in geo.boundary:
                x, y = b.coords.xy
                coords = np.dstack((x, y)).tolist()
                bcoords.append(coords)
        else:
            pass

        feature = {'type': 'Feature',
                   'id': index,
                   'properties': {'name': geo_names[index]},
                   'geometry': {'type': gtype,
                                'coordinates': bcoords},
                   }

        geojson['features'].append(feature)
    return geojson


def get_layout():
    # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    import dash

    gdf = gpd.GeoDataFrame.from_postgis(
        sql=select([Province]),
        geom_col='geometry',
        con=db.session.bind
    )
    gdf.head(10)
    geojsdata = shapefile_to_geojson(gdf, list(gdf.index), geo_names_col='label')

    lats = gdf['geometry'].centroid.apply(lambda x: x.y).tolist()
    lons = gdf['geometry'].centroid.apply(lambda x: x.x).tolist()
    text = gdf['label'].tolist()

    bluecart = [[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]

    choro = go.Choroplethmapbox(
        z=gdf['area'].tolist(),
        locations=gdf.index.tolist(),
        colorscale=bluecart,  # carto
        colorbar=dict(thickness=20, ticklen=3),
        geojson=geojsdata,
        text=gdf['label'],
        # below=True,
        hovertemplate='<b>Province</b>: <b>%{text}</b>' +
        '<br><b>Val </b>: %{z}<br>',
        marker_line_width=0.1, marker_opacity=0.7)
    scatt = go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers+text',
        text=text,
        # hoverinfo='none',
        below='',
        marker=dict(size=12, color='rgb(235, 0, 100)'))
    layout = go.Layout(
        title_text='Netherlands mapbox choropleth', title_x=0.5, width=750, height=700,
        mapbox=dict(
            center=dict(lat=-28, lon=26),
            accesstoken=mapboxt,
            zoom=4,
            style="light"

        ))

    fig = go.Figure(data=[choro, scatt], layout=layout)
    # iplot(fig)
    layout = [
        sidebar,
        html.Div(
            id='div-map-pane',
            children=[
                dcc.Graph(figure=fig)
            ],
            style=CONTENT_STYLE
        )
    ]

    return layout
