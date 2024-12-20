#!/usr/bin/env python
# coding: utf-8

# # Public Transport

# ## Import Libaries 

# In[ ]:


import numpy as np
import pandas as pd


# ## Data

# ### Create DataFrames 

# In[ ]:


tram="https://raw.githubusercontent.com/mttaherpoor/Transit-Dashboard/f41253c68590cca836c1e2e79015f657fe4cccb2/Datasets/Tramway.xlsx"
metro="https://raw.githubusercontent.com/mttaherpoor/Transit-Dashboard/f41253c68590cca836c1e2e79015f657fe4cccb2/Datasets/Metro.xlsx"
brt="https://raw.githubusercontent.com/mttaherpoor/Transit-Dashboard/6c25ba1c7a0090634cb90d8c248c1f7cbad7991e/Datasets/BRT.xlsx"

df_DataBase=pd.read_excel(tram,sheet_name="DataBase")
df_Current=pd.read_excel(tram,sheet_name="Current")
df_Metro=pd.read_excel(metro,sheet_name="List")
df_Develop=pd.read_excel(tram,sheet_name="Developing")
df_Counries=pd.read_excel(tram,sheet_name="Countries")
df_Continents=pd.read_excel(tram,sheet_name="Continents")
df_BRT=pd.read_excel(brt,sheet_name="List")


# ### Prepare df_Sure

# In[ ]:


df_Sure=df_DataBase[df_DataBase["code"]=="Sure"].copy()
df_Sure.loc[:,"Data from Final"] = df_Sure[["Date From 1", "Date From 2"]].max(axis=1)
df_Sure.loc[:,"Data to Final"] = df_Sure[["Date to 1", "Date to 2"]].max(axis=1)


# #### Prepare df_Sure_elec

# In[ ]:


system_types=list(df_Sure["Traction type"].unique())
elec={}
for system in system_types:
    elec[system]=str(system).lower().find("electric")
    
df_Sure_elec=df_Sure[df_Sure["Traction type"].map(elec)!=-1]


# ### Prepare df_Current

# In[ ]:


df_Current["After 2000_Tram"]=(df_Current["Year opened"]>=2000)
df_Current["After 2000_Tram"]=df_Current["After 2000_Tram"].apply(lambda x:"After 2000" if x == True else "Before 2000")

df_Current=df_Current[df_Current["Calculate"]!="Don't Calculate"]

df_Current=df_Current[df_Current["Operation code "]<5]


# ### Prepare df_Metro

# In[ ]:


df_Metro["After 2000_Metro"]=(df_Metro['Service opened']>=2000)
df_Metro["After 2000_Metro"]=df_Metro["After 2000_Metro"].apply(lambda x:"After 2000" if x == True else "Before 2000")


# ### Prepare df_BRT

# In[ ]:


df_BRT=df_BRT[df_BRT["Calculate"]!="Don't Calculate"]

df_BRT=df_BRT[df_BRT["Operation code "]==0]


# ### Prepare df of cities

# In[ ]:


# Your existing code for tramways
tram_cols=["City","Country", "Population","Continent","Class","Start Operation","lon","lat","After 2000_Tram"]
city_Tramway = df_Current.groupby(tram_cols)["length (km)"].sum().reset_index()
city_Tramway.rename(columns={"length (km)":"length_Tramway"}, inplace=True)
city_Tramway["length_per_capita_Tramway"] = city_Tramway["length_Tramway"] / city_Tramway["Population"] * 100000

# Calculate minimum "Year opened" for tramways for each city
min_year_tramway = df_Current.groupby("City")["Year opened"].min().reset_index()
city_Tramway = city_Tramway.merge(min_year_tramway, how="left", on="City")

# Your existing code for metros
metro_cols=["City","Country", "Population","Continent","lon","lat","Class","After 2000_Metro"]
city_metro = df_Metro.groupby(metro_cols)["length(km)"].sum().reset_index()
city_metro.rename(columns={"length(km)":"length_Metro"}, inplace=True)
city_metro["length_per_capita_Metro"] = city_metro["length_Metro"] / city_metro["Population"] * 100000

# Calculate minimum "Service opened" for metros for each city
min_service_opened_metro = df_Metro.groupby("City")["Service opened"].min().reset_index()
city_metro = city_metro.merge(min_service_opened_metro, how="left", on="City")

# Your existing code for BRT
BRT_cols=["City","Country", "Population","Continent","lon","lat","Class"]
city_BRT = df_BRT.groupby(BRT_cols)["length (km)"].sum().reset_index()
city_BRT.rename(columns={"length (km)":"length_BRT"}, inplace=True)
city_BRT["length_per_capita_BRT"] = city_BRT["length_BRT"] / city_BRT["Population"] * 100000

# Calculate minimum "Year open" for BRT for each city
min_year_open_brt = df_BRT.groupby("City")["Year open"].min().reset_index()
city_BRT = city_BRT.merge(min_year_open_brt, how="left", on="City")

# Merge tram, metro, and BRT data
df_city = city_Tramway.merge(city_metro, how="outer", on=["City","Country","Population","Continent","lat","lon","Class"])
df_city = pd.merge(df_city, city_BRT, how="outer", on=["City","Country","Population","Continent","lat","lon","Class"])

# Combine lengths and calculate per capita values
df_city["length_Tramway"].fillna(0, inplace=True)
df_city["length_Metro"].fillna(0, inplace=True)
df_city["length_BRT"].fillna(0, inplace=True)
df_city["length_per_capita"] = df_city["length_per_capita_Tramway"].fillna(0) + df_city["length_per_capita_Metro"].fillna(0) + df_city["length_per_capita_BRT"].fillna(0)
df_city["Total Length"] = df_city["length_Tramway"] + df_city["length_Metro"] + df_city["length_BRT"]

# Fill missing values
for col in df_city.columns:
    if col in ["length_Tramway", "length_Metro", "length_BRT", "Start Operation", "Service opened", "Year opened", "Year open"]:
        df_city[col].fillna(0, inplace=True)
    else:
        df_city[col].fillna("")

# Define function to determine transport type
def type_transport(row, col1, col2, col3):
    if row[col1] and row[col2] and row[col3]:
        return "Tram/Metro/BRT"
    elif row[col1] and row[col2] and row[col3] == 0:
        return "Tram/Metro"
    elif row[col1] and row[col3] and row[col2] == 0:
        return "Tram/BRT"
    elif row[col1] and row[col2] == 0 and row[col3] == 0:
        return "Tram"
    elif row[col2] and row[col3] and row[col1] == 0:
        return "Metro/BRT"
    elif row[col2] and row[col3] == 0 and row[col1] == 0:
        return "Metro"
    elif row[col2] == 0 and row[col3] and row[col1] == 0:
        return "BRT"
    else:
        return 1

# Apply transport type function
df_city["type"] = df_city.apply(lambda row: type_transport(row, "length_Tramway", "length_Metro", "length_BRT"), axis=1)

# Merge with additional data
df_city = df_city.merge(df_Counries, on="Country", how="left")
df_city = df_city.merge(df_Continents, on="Continent", how="left")
df_city.rename(columns={"Population_x": "Population", "Population_y": "Population_Country", "Population": "Population_Continent"}, inplace=True)
df_city.drop(columns=["row_x", "row_y"], inplace=True)
df_city['length_Tramway'] = pd.to_numeric(df_city['length_Tramway'], errors='coerce')
df_city['length_Metro'] = pd.to_numeric(df_city['length_Metro'], errors='coerce')

df_city["Service opened"] = df_city["Service opened"].astype(int)
df_city["Year opened"] = df_city["Year opened"].astype(int)
df_city["Start Operation"] = df_city["Start Operation"].astype(int)
df_city["Year open"] = df_city["Year open"].astype(int)


df_city["length_per_capita"] = pd.to_numeric(df_city["length_per_capita"], errors="coerce")


# ### Timeline

# ####  Prepare  def Timeline

# In[ ]:


def Timeline(df,args):
    len_time=len(args)
    data=[]
    
    from1=args[0]
    to1=args[1]
    if len_time==4:
        
        from2=args[2]
        to2  =args[3]

        for _, row in df.iterrows():

            if pd.notnull(row[from1]) and pd.notnull(row[from2]) and pd.notnull(row[to1]) and pd.notnull(row[to2]):
                start1=int(row[from1])//10*10
                finish1=int(row[to1])//10*10
                for decade in range(start1,finish1+1,10):
                    data.append({'Country': row['Country'],"Continent":row["Continent"],'Decade': decade, 'Count': 1})
                start2=int(row[from2])//10*10
                finish2=int(row[to2])//10*10
                for decade in range(start2,finish2+1,10):
                    data.append({'Country': row['Country'],"Continent":row["Continent"],'Decade': decade, 'Count': 1})

            elif pd.notnull(row[from1]) and pd.notnull(row[to1]):
                start1=int(row[from1])//10*10
                finish1=int(row[to1])//10*10
                for decade in range(start1,finish1+1,10):
                    data.append({'Country': row['Country'],"Continent":row["Continent"],'Decade': decade, 'Count': 1})
                    
        data = [entry for entry in data if entry['Count'] > 0]                      
        new_df = pd.DataFrame(data)
        return new_df.groupby(['Country',"Continent", 'Decade'])['Count'].sum().reset_index()
    else :
        for _, row in df.iterrows():
            if pd.notnull(row[from1]) and pd.notnull(row[to1]):
                start1=int(row[from1])//10*10
                finish1=int(row[to1])//10*10
                for decade in range(start1,finish1+1,10):
                    data.append({'Country': row['Country'],"Continent":row["Continent"],'Decade': decade, 'Count': 1})
                    
        data = [entry for entry in data if entry['Count'] > 0]                      
        new_df = pd.DataFrame(data)
        return new_df.groupby(['Country',"Continent", 'Decade'])['Count'].sum().reset_index()


col_sure_elec=['Date From 1','Date to 1','Date From 2','Date to 2']
col_current=["Year opened","Date to"]
df_Timeline_Tram_Sure_elec=Timeline(df_Sure_elec,col_sure_elec)
df_Current["Date to"]=2024
df_Timeline_Tram_Current=Timeline(df_Current,col_current)

df_Metro.loc[:,"Date to"]=2024

col_metro=["Service opened","Date to"]
df_Timeline_Metro=Timeline(df_Metro,col_metro)

df_BRT.loc[:,"Date to"]=2024
col_BRT=["Year open","Date to"]
df_Timeline_BRT=Timeline(df_BRT,col_BRT)


# ####  Prepare Timeline Total

# In[ ]:


df_Timeline_Tram=df_Timeline_Tram_Sure_elec.merge(df_Timeline_Tram_Current,on=["Country","Decade","Continent"],how="outer")
df_Timeline_Tram["Count"]=df_Timeline_Tram["Count_x"].fillna(0)+df_Timeline_Tram["Count_y"].fillna(0)
col_to_drop=["Count_x","Count_y"]
df_Timeline_Tram.drop(columns=col_to_drop,inplace=True)


df_Timeline_Tram_Continent=df_Timeline_Tram.groupby(["Continent", 'Decade'])['Count'].sum().reset_index()
df_Timeline_Tram=df_Timeline_Tram.merge(df_Counries,on="Country")

df_Timeline_Metro_Continent=df_Timeline_Metro.groupby(["Continent", 'Decade'])['Count'].sum().reset_index()
df_Timeline_Metro=df_Timeline_Metro.merge(df_Counries,on="Country")

df_Timeline_BRT_Continent=df_Timeline_BRT.groupby(["Continent", 'Decade'])['Count'].sum().reset_index()
df_Timeline_BRT=df_Timeline_BRT.merge(df_Counries,on="Country")

col_to_merge=["Country","Continent","Country code"]
#df_Timeline=pd.merge(df_Timeline_Tram,df_Timeline_Metro,on=col_to_merge,suffixes=(" Tram"," Metro"),how="left")

df_Timeline_Tram=df_Timeline_Tram.sort_values(by=["Country","Continent","Decade"])
df_Timeline_Metro=df_Timeline_Metro.sort_values(by=["Country","Continent","Decade"])
df_Timeline_BRT=df_Timeline_BRT.sort_values(by=["Country","Continent","Decade"])

df_Timeline_Metro.loc[:,"type"]="Metro"

df_Timeline_Tram.loc[:,"type"]="Tramway"

df_Timeline_BRT.loc[:,"type"]="BRT"

df_Timeline_Total_Continent=df_Timeline_Tram_Continent.merge(df_Timeline_Metro_Continent
                                                             ,on=["Continent","Decade"],how="outer")


df_Timeline_Total_Continent["Count"]=df_Timeline_Total_Continent["Count_x"].fillna(0)+df_Timeline_Total_Continent["Count_y"].fillna(0)
col_to_drop=["Count_x","Count_y"]
df_Timeline_Total_Continent.drop(columns=col_to_drop,inplace=True)

df_Timeline_Total_Continent=df_Timeline_Total_Continent.merge(df_Timeline_BRT_Continent
                                                             ,on=["Continent","Decade"],how="outer")

df_Timeline_Total_Continent["Count"]=df_Timeline_Total_Continent["Count_x"].fillna(0)+df_Timeline_Total_Continent["Count_y"].fillna(0)
col_to_drop=["Count_x","Count_y"]
df_Timeline_Total_Continent.drop(columns=col_to_drop,inplace=True)


# ## Dashborad

# # New dash

# In[ ]:


import dash
from dash import html,dcc,dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import re
import random
import requests
import os

app = dash.Dash(__name__, 
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.SOLAR],
               meta_tags=[{"name":"viewport",
                         "content":"width=device-width ,initail-scale:1.0"}])

##add parameters :
min_year=df_Timeline_Tram["Decade"].min()
max_year=df_Timeline_Tram["Decade"].max()

github_repo="mttaherpoor/Transit-Dashboard"
github_branch="1efcf286843fdc798cbffef45274aded7fca3f12"
github_folder_path="assets/slideshow/"

github_api_url=f"https://api.github.com/repos/{github_repo}/git/trees/{github_branch}?recursive=1"
response=requests.get(github_api_url)
image_paths=[]
if response.status_code==200:
    json_data=response.json()
    img=[item['path'] for item in json_data["tree"] if github_folder_path in item['path']]
    for im in img:
        image_url=f"https://raw.githubusercontent.com/{github_repo}/{github_branch}/{im}"
        image_paths.append(image_url)

random.shuffle(image_paths)
image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]

## If Tram/Metro then Tram and others type
def isolate_transit(row, transit_type):
    if transit_type in row["type"]:
        return transit_type
    else:
        return None


#### nav top
navbar=dbc.NavbarSimple(
    brand='Public Transportation in The World',
    children=[
        html.Img(src="/assets/bg_dashboard2_image.jpg",height=20),
        html.A("Urban Rail",
               href="https://urbanrail.net",
               target="_blank",
               style={"color":"black"})        
    ],
    color="success",
    fluid=True
)

#####side bar

sidebar=dbc.Card([
    dbc.CardBody([
        html.H3("Menu"),
        html.Hr(),
        #html.P("Show The Information Public Transport",className="lead"),
        dbc.Nav([
            dbc.NavLink("Home Page",href="/",active="excat"),
            dbc.NavLink("City Info",href="/city-info",active="excat"),
            dbc.NavLink("Timeline",href="/timeline",active="excat"),
            dbc.NavLink("Global Charts",href="/global-charts",active="excat"),
            dbc.NavLink("Global Maps",href="/global-maps",active="excat"),
            dbc.NavLink("About",href="/about",active="excat"),
        ],
        vertical=True,
        pills=True
        ),
    ]),
],color="light",style={"height":"100vh",
                        "width":"10rem",
                       "position":"fixed"})

######chrats

def create_plotly_stripplot(df, x, y, color, title, xaxis, yaxis):
    fig = px.strip(df,
                   x=x,
                   y=y,
                   color=color,
                   category_orders={y: sorted(df[y].unique())},
                   color_discrete_map={True: 'darkorange', False: 'royalblue'},
                   template="plotly_dark",
                   hover_data=["Country","City","Population"],
                   facet_col_spacing=0.1,
                   width=1200,  # Adjust width as needed
                   height=800,
                   )
    fig.update_layout(
        legend=dict(title=color),
        xaxis=dict(title=xaxis),
        yaxis=dict(title=yaxis),
        title=dict(text=title, font=dict(family='Times New Roman', size=20, color='#008080'), x=0.5)
    )

    return fig

def create_plotly_lineplot(df, x_col, y_col, hue_col, title, x_axis, y_axis):
    fig = px.line(df,
                  x=x_col,
                  y=y_col,
                  color=hue_col,
                  line_group=hue_col,
                  markers=True,
                  labels={y_col: y_axis},
                  category_orders={hue_col: list(df[hue_col].unique())},
                  color_discrete_map={True: 'darkorange', False: 'royalblue'},
                  template="plotly_dark",
                  width=1200,  # Adjust width as needed
                  height=800,
                  )

    fig.update_layout(
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        font=dict(family='Times New Roman', size=14),
        legend=dict(title=hue_col, x=1.02, y=1),
        title=dict(text=title,  font=dict(family='Times New Roman', size=20, color='#008080'), x=0.5)
    )

    return fig


def barplot_combined(df, x_col, y_col, color_col, facet_col, xaxis_title, yaxis_title, title, hover_data):
    # Create a bar plot using Plotly Express
    fig = px.bar(df,
                 x=x_col,
                 y=y_col,
                 color=color_col,
                 facet_col=facet_col,
                 labels={y_col: yaxis_title},
                 template="plotly_dark",
                 facet_col_spacing=0, 
                 hover_data=hover_data,
                 width=1200,
                 height=800,)

    # Customize the layout
    fig.update_layout(
        #xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        font=dict(family='Times New Roman', size=14),
        legend=dict(title=color_col, x=0.5, y=1),
        title=dict(text=title,  font=dict(family='Times New Roman', size=20, color='#008080'), x=0.5)
        
    )

    return fig

def plot_city_map(df):
    # Create a scattermapbox plot
    fig = px.scatter_mapbox(df,
                            lat='lat',
                            lon='lon',
                            color='type',
                            color_discrete_map={
                                'Tram': 'red', 
                                'Metro': 'blue',
                                'Tram/Metro': 'purple',
                                'BRT':"green",
                                'Metro/BRT':'cyan ',
                                'Tram/BRT':'yellow',
                                'Tram/Metro/BRT':'white'                                                             
                            },
                            size_max=15,
                            zoom=1.5,
                            mapbox_style='carto-darkmatter',
                            hover_data=["Country","City","Population","Total Length"],
                            width=1200,
                            height=800,
                            
                           )

    # Update layout settings
    fig.update_layout(
        legend_title='Transport Type',
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        title=dict(text='Transit Types in Cities',font=dict(family='Times New Roman', size=20, color='#008080'), x=0.5)
        
    )

    return fig


########@########################layout#######################################
dashboard1_layout = html.Div([
    html.H1("Global Transit Statistics",className="text-primary"),
    html.Div(id="slideshow-container",
             children=[
                 html.Img(id="image",src=image_paths[0], style={"width": "100%"}),
                 dcc.Interval(id="interval", interval=5000),
                 html.Div(image_name,
                     id="text-image",
                     className="font-weight-bold text-secondary",
                     style={"font-size": "2em", "text-align": "center", "margin-top": "20px"}
)
             ]
    )
])
dashboard2_layout = dbc.Container([
    html.H1("City Info", className="text-primary"),
    dcc.Link(html.Button("Back",style={'background-color': '#002B36',
                                       'color': '#A4782D',"border":'none'}), href='/'),
    html.Button("Refresh", id="refresh-btn",style={'background-color': '#002B36',
                                       'color': 'red',"border":'none'}),
    html.Br(),
    html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id=f'continent-dropdown-{position}',
                    options=[{'label': continent, 'value': continent}
                             for continent in sorted(df_city['Continent'].unique())],
                    placeholder='Select Continent',
                    clearable=True
                ),
                dcc.Dropdown(id=f'country-dropdown-{position}', placeholder='Select Country', clearable=True),
                dcc.Dropdown(id=f'city-dropdown-{position}', placeholder='Select City', clearable=True),
                html.Br(),
                html.Br(),
                html.Div(id=f'tram-metro-info-{position}')
            ]) for position in ["left", "right"]
        ]),
        html.Br(),
        #html.Button('Show Chart', id='show-chart-button', n_clicks=0),
       # html.Div(id='chart-bar')  # Corrected indentation
    ])
])

line_chart_container = dbc.Container([
    html.H4("Line Chart", className="text-primary"),
    dcc.Graph(id="line-chart", figure={}),
], id="line-chart-container", style={'display': 'none'})  # Initially hidden

# Update the layout to include the line chart container
dashboard3_layout = html.Div([
    html.H1("Timeline", className="text-primary"),
    dcc.Link(html.Button("Back",style={'background-color': '#002B36',
                                       'color': '#A4782D',"border":'none'}), href='/'),
    html.Br(),
    dbc.Row([
        dcc.Dropdown(id='transport-dropdown',
                      placeholder='Select Type Transport', 
                      clearable=True,
                      options=[{'label': transport, 'value': transport} for transport in ["Tramway", "Metro", "BRT"]]        
    ,)]),
    html.H2(id="transport-title", className="text-secondary"),
    html.Div([
        dcc.RangeSlider(id="timeline-slider",
                        min=min_year,
                        max=max_year,
                        value=[min_year,max_year],
                        marks={i:str(i) for i in range(min_year,max_year+1,10)}),

        dcc.Graph(id="timeline-graph"),
        html.Br(),
        dash_table.DataTable(id="tramway-info")
    ], id="slider-container", style={'display': 'none'}),
    
    # Include the line chart container
    line_chart_container
])

 
dashboard4_layout = html.Div([
    html.H1("Global Charts", className="text-primary"),
    dcc.Link(html.Button("Back",style={'background-color': '#002B36',
                                       'color': '#A4782D',"border":'none'}), href='/'),
    html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='chart-dropdown',
                      placeholder='Select Type Transport', 
                      clearable=True,
                      options=[{'label': transport, 'value': transport} for transport in ["Tramway", "Metro", "BRT","Total"]]        
                ,)
            ]),
        ], className="text-center")
    ]),
        html.Br(),
        html.Div(id="global-charts")
    ])


dashboard5_layout = html.Div([
    html.H1("Global Maps", className="text-primary"),
    dcc.Link(html.Button("Back",style={'background-color': '#002B36',
                                       'color': '#A4782D',"border":'none'}), href='/'),
    html.Br(),
    dcc.Graph(
        id='city-map',
        figure=plot_city_map(df_city)
    )
])
dashboard6_layout = html.Div([
    html.H1("About", className="text-primary"),
    dcc.Link(html.Button("Back",style={'background-color': '#002B36',
                                       'color': '#A4782D',"border":'none'}), href='/'),
    html.Div(
            [
            html.H2("Info",className="text-success"),
            dbc.Row([
                dbc.Col([
                    html.H3("Mohamad Taher Taherpoor",className="text-info"),
                    html.Img(src="https://raw.githubusercontent.com/mttaherpoor/Transit-Dashboard/1efcf286843fdc798cbffef45274aded7fca3f12/assets/about/taher-prof.jpg",height=200,width=200),
                    html.P("Data Scientist"),
                    html.P("MSc in urban management"),
                    html.A("Visit GitHub", href=f"https://github.com/mttaherpoor", target="_blank"),
            
                ]),
                dbc.Col([
                    html.H3("Dr.Shahabeddin Kermanshahi",className="text-info"),
                    html.Img(src="https://raw.githubusercontent.com/mttaherpoor/Transit-Dashboard/1efcf286843fdc798cbffef45274aded7fca3f12/assets/about/dr Kermanshahi-prof.jpg",height=200,width=200),
                    html.P("Ph.D. inTransportation Planning"),
                    html.P("faculty member of urban planning department,  University of Tehran"),
                    html.A("contact with Email",href="https://rtis2.ut.ac.ir/cv/shkermanshahi/?lang=en-gb",target="_blank"),
                ]), 
            ]),
            html.Br(),html.Br(),    
            html.Hr(),
            
            html.H2("References",className="text-success"),
            dbc.Row([
                dbc.Col([
                    html.P("list of cities that have current tram/streetcar"),
                    html.A("Current Tramway",href="https://en.wikipedia.org/wiki/List_of_tram_and_light_rail_transit_systems",target="_blank"),
                ]),
                dbc.Col([
                    html.P("list of cities that have, or once had, town tramway"),
                    html.A("History of Tramway",href="https://en.m.wikipedia.org/wiki/List_of_town_tramway_systems",target="_blank"),
                ]),
                dbc.Col([
                    html.P(" list of cities that have metro systems"),
                    html.A("Metro",href="https://en.m.wikipedia.org/wiki/List_of_metro_systems",target="_blank"),
                ]),                
                dbc.Col([
                    html.P("list of bus rapid transit (BRT)"),
                    html.A("BRT",href="https://en.wikipedia.org/wiki/List_of_bus_rapid_transit_systems",target="_blank"),
                ]),
                dbc.Col([
                    html.P("Data from Mass Transit by Robert Schwandl"),
                    html.A("urban rail",href="http://www.urbanrail.net/",target="_blank"),
                ]),                
                dbc.Col([
                    html.P("The International Association of PT"),
                    html.A("UITP",href="https://uitp.org/",target="_blank"),
                ]),                
            ]),
            html.Br(),html.Br(),    
            html.Hr(),
            
            html.H2("Special Thanks",className="text-success"),
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.A("Dr. Morteza Jaberi", href="https://rtis2.ut.ac.ir/cv/hjaberi/?lang=en-gb", target="_blank"),
                        ", ",
                        html.A("Dr. Nahid Nemati", href="https://github.com/GISwithTisa", target="_blank"),
                        ", ",                      
                        html.A("Eng. Keinaz Nourizadeh", href="https://www.linkedin.com/in/keinaznourizadeh/",target="_blank"),
                        ", ",
                        html.A("Eng. Alireza Fallah", href="https://www.linkedin.com/in/alireza-fallahsoltani/", target="_blank"),
                        ", ",
                        html.A("Eng. Farahnaz Zarrin Nam", href="https://www.linkedin.com/in/farahnaz-zarrinnam/",target="_blank"),
                    ])
            ])
                
        ])
    ])
])
#####################################################Home Page##############################################################
@app.callback(
    [Output("image", "src"),
    Output("text-image","children")], 
    [Input("interval", "n_intervals")]
)
def update_image(n):
    if n is not None:
        image_index = n % len(image_paths)
        image_name = os.path.splitext(os.path.basename(image_paths[image_index]))[0]
        #print(image_name)
        return image_paths[image_index],image_name
    else:
        raise PreventUpdate



#####################################################City Info##############################################################
  
########left,right 
    
for position in ["left","right"]:
    @app.callback(
        Output(f'country-dropdown-{position}', 'options'),
        [Input(f'continent-dropdown-{position}', 'value')]
    )
    def update_country_options(selected_continent):
        if selected_continent is None:
            return []
        countries = sorted(df_city[df_city['Continent'] == selected_continent]['Country'].unique())
        return [{'label': country, 'value': country} for country in countries]

    @app.callback(
        Output(f'city-dropdown-{position}', 'options'),
        [Input(f'country-dropdown-{position}', 'value')]
    )

    def update_city_options(selected_country):
        if selected_country is None:
            return []
        cities = sorted(df_city[df_city['Country'] == selected_country]['City'].unique())
        return [{'label': city, 'value': city} for city in cities]


    @app.callback(
        Output(f'tram-metro-info-{position}', 'children'),
        [Input(f'continent-dropdown-{position}', 'value'),
         Input(f'country-dropdown-{position}', 'value'),
         Input(f'city-dropdown-{position}', 'value')]
    )
    def update_tram_metro_info(selected_continent, selected_country, selected_city):
        if selected_city:
            filter_data  = df_city[df_city['City'] == selected_city]
            tram_length = (
                filter_data[filter_data['type'] == "Tram"]['length_Tramway'].iloc[0]
                if not filter_data[filter_data['type'] == "Tram"].empty else 0
            )
            metro_length = (
                filter_data[filter_data['type'] == "Metro"]['length_Metro'].iloc[0]
                if not filter_data[filter_data['type'] == "Metro"].empty else 0
            )
             
            brt_length   = (
                filter_data[filter_data['type'] == "BRT"]['length_BRT'].iloc[0] 
                if not filter_data[filter_data['type'] == "BRT"].empty else 0
            )
            
            population   = filter_data["Population"].iloc[0]
            developed    = filter_data["Class"].iloc[0]

            if (filter_data['length_Tramway'] == 0).all():
                start_tram, start_operat = "Not Started", "Not Started"
            else:
                start_tram = filter_data.loc[filter_data['length_Tramway'] != 0, 'Year opened'].min()
                start_operat = filter_data.loc[filter_data['length_Tramway'] != 0, 'Start Operation'].min()
            if (filter_data['length_Metro'] == 0).all():
                start_metro = "Not Started"
            else:
                start_metro = filter_data.loc[filter_data['length_Metro'] != 0, 'Service opened'].min()
            if (filter_data['length_BRT'] == 0).all():
                start_BRT = "Not Started"
            else:
                start_BRT = filter_data.loc[filter_data['length_BRT'] != 0, 'Year open'].min()
                
                
            select = selected_city

            return dbc.Card([
                dbc.CardHeader(f"{select} :", className="text-success", style={'font-size': '30px'}),
                dbc.CardBody([
                    html.P(f"in {developed} Country"),
                    html.P(f"Population is: {int(population):,}"),
                    html.H3("Tramway:"),
                    html.P(f"Year of Tram Start: {start_operat}"),
                    html.P(f"Total Tram Length: {tram_length:.2f} km"),
                    html.H3("Metro:"),
                    html.P(f"Year of Metro Start: {start_metro}"),
                    html.P(f"Total Metro Length: {metro_length:.2f} km"),
                    html.H3("BRT:"),
                    html.P(f"Year of BRT Start: {start_BRT}"),
                    html.P(f"Total BRT Length: {brt_length:.2f} km"),
                ])
            ])
        elif selected_country:
            filter_data  = df_city[df_city['Country'] == selected_country]
            tram_length  = filter_data['length_Tramway'].sum()
            metro_length = filter_data['length_Metro'].sum()
            brt_length   = filter_data['length_BRT'].sum()
            
            population   = filter_data["Population_Country"].iloc[0]
            developed    = filter_data["Class"].iloc[0]
 
            if (filter_data['length_Tramway'] == 0).all():
                start_tram, start_operat = "Not Started", "Not Started"
            else:
                start_tram = filter_data.loc[filter_data['length_Tramway'] != 0, 'Year opened'].min()
                start_operat = filter_data.loc[filter_data['length_Tramway'] != 0, 'Start Operation'].min()
            if (filter_data['length_Metro'] == 0).all():
                start_metro = "Not Started"
            else:
                start_metro = filter_data.loc[filter_data['length_Metro'] != 0, 'Service opened'].min()
            if (filter_data['length_BRT'] == 0).all():
                start_BRT = "Not Started"
            else:
                start_BRT = filter_data.loc[filter_data['length_BRT'] != 0, 'Year open'].min()
            
            select = selected_country
            return dbc.Card([
                dbc.CardHeader(f"{select} :", className="text-success", style={'font-size': '30px'}),
                dbc.CardBody([
                    html.P(f"{developed} Country"),
                    html.P(f"Population is: {int(population):,}"),
                    html.H3("Tramway:"),
                    html.P(f"Year of Tram Start: {start_operat}"),
                    html.P(f"Total Tram Length: {tram_length:.2f} km"),
                    html.H3("Metro:"),
                    html.P(f"Year of Metro Start: {start_metro}"),
                    html.P(f"Total Metro Length: {metro_length:.2f} km"),
                    html.H3("BRT:"),
                    html.P(f"Year of BRT Start: {start_BRT}"),
                    html.P(f"Total BRT Length: {brt_length:.2f} km"),
                ])
            ])
        elif selected_continent:
            filter_data  = df_city[df_city['Continent'] == selected_continent]
            tram_length  = filter_data['length_Tramway'].sum()
            metro_length = filter_data['length_Metro'].sum()
            brt_length   = filter_data['length_BRT'].sum()
            
            population   = filter_data["Population_Continent"].iloc[0]

            developed_count = filter_data[filter_data['Class'] == 'Developed']['Country'].nunique()
            developing_count = filter_data[filter_data['Class'] == 'Developing']['Country'].nunique()

            if (filter_data['length_Tramway'] == 0).all():
                start_tram, start_operat = "Not Started", "Not Started"
            else:
                start_tram = filter_data.loc[filter_data['length_Tramway'] != 0, 'Year opened'].min()
                start_operat = filter_data.loc[filter_data['length_Tramway'] != 0, 'Start Operation'].min()
            if (filter_data['length_Metro'] == 0).all():
                start_metro = "Not Started"
            else:
                start_metro = filter_data.loc[filter_data['length_Metro'] != 0, 'Service opened'].min()
            if (filter_data['length_BRT'] == 0).all():
                start_BRT = "Not Started"
            else:
                start_BRT = filter_data.loc[filter_data['length_BRT'] != 0, 'Year open'].min()
            select = selected_continent

            return dbc.Card([
                dbc.CardHeader(f"{select} :", className="text-success", style={'font-size': '30px'}),
                dbc.CardBody([
                    html.P(f"Total Developed Countries: {developed_count} ,Total Developing Countries: {developing_count} "),
                    html.P(f"Population is: {int(population):,}"),
                    html.H3("Tramway:"),
                    html.P(f"Year of Tram Start: {start_operat}"),
                    html.P(f"Total Tram Length: {tram_length:.2f} km"),
                    html.H3("Metro:"),
                    html.P(f"Year of Metro Start: {start_metro}"),
                    html.P(f"Total Metro Length: {metro_length:.2f} km"),
                    html.H3("BRT:"),
                    html.P(f"Year of BRT Start: {start_BRT}"),
                    html.P(f"Total BRT Length: {brt_length:.2f} km"),
                ])
            ])
        else:
            return ""

# Assuming you have functions extract_population, extract_tram_length, extract_metro_length


def get_card_details(selected):
    card_str = str(update_tram_metro_info(selected_continent, selected_country, selected_city))
    match_header = re.search(r"CardHeader\(children='([^']+)", card_str)
    match_population = re.search(r"Population is: ([^']+)", card_str)
    match_tram_length = re.search(r"Total Tram Length: ([^']+)", card_str)
    match_metro_length = re.search(r"Total Metro Length: ([^']+)", card_str)

    if selected_city:
        selected = match_header.group(1).split(":")[0] if match_header else None
        population = int(match_population.group(1).replace(",", "")) / 10**6 if match_population else None
        tram_length = float(match_tram_length.group(1).split()[0]) if match_tram_length else None
        metro_length = float(match_metro_length.group(1).split()[0]) if match_metro_length else None

        # Do something specific for selected_city

    elif selected_country:
        selected = match_header.group(1).split(":")[0] if match_header else None
        population = int(match_population.group(1).replace(",", "")) / 10**6 if match_population else None
        tram_length = float(match_tram_length.group(1).split()[0]) if match_tram_length else None
        metro_length = float(match_metro_length.group(1).split()[0]) if match_metro_length else None

        # Do something specific for selected_country

    elif selected_continent:
        selected = match_header.group(1).split(":")[0] if match_header else None
        population = int(match_population.group(1).replace(",", "")) / 10**6 if match_population else None
        tram_length = float(match_tram_length.group(1).split()[0]) if match_tram_length else None
        metro_length = float(match_metro_length.group(1).split()[0]) if match_metro_length else None

        # Do something specific for selected_continent

    else:
        selected, population, tram_length, metro_length = None, None, None, None

    return selected, population, tram_length, metro_length

# Callback to update bar chart
#@app.callback(
#   Output("chart-bar", "children"),
#    [Input(f'tram-metro-info-{position}', 'value') for position in ['left', 'right']],
  #  [Input(f'country-dropdown-{position}', 'value') for position in ['left', 'right']],
  #  [Input(f'city-dropdown-{position}', 'value') for position in ['left', 'right']],
 #   [Input('show-chart-button', 'n_clicks')],
#    prevent_initial_call=True
#)
def generate_comparison_plot(left,right):

    selected_left, population_left, tram_length_left, metro_length_left = get_card_details(left,)
    selected_right, population_right, tram_length_right, metro_length_right = get_card_details(right)

# The rest of the function remains the same...
# Create a list of categories
    categories = ['Population', 'Tram Length', 'Metro Length']

# Create a list of values for left and right cities
    left_values = [population_left, tram_length_left, metro_length_left]
    right_values = [population_right, tram_length_right, metro_length_right]
    print(left_values,right_values)
# Create a list of ages for the y-axis
    y = list(range(len(categories)))

    layout = go.Layout(
        yaxis=go.layout.YAxis(title='Category'),
        xaxis=go.layout.XAxis(
            range=[-1200, 1200],
            tickvals=[-1000, -700, -300, 0, 300, 700, 1000],
            ticktext=[1000, 700, 300, 0, 300, 700, 1000],
            title='Comparison'
        ),
        barmode='stack',
        bargap=0.1
    )

    data = [
        go.Bar(
            y=y,
            x=left_values,
            orientation='h',
            name=selected_left,
            hoverinfo='x',
            marker=dict(color='powderblue')
        ),
        go.Bar(
            y=y,
            x=[-val for val in right_values],  # Reverse the values for the right side
            orientation='h',
            name=selected_right,
            text=[-val for val in right_values],  # Reverse the values for hover text
            hoverinfo='text',
            marker=dict(color='seagreen')
        )
    ]

    fig = go.Figure(data=data, layout=layout)
    return dcc.Graph(figure=fig)
#pyo.iplot(fig, filename='population_pyramid')
        
##########left,right both
@app.callback(
    [Output('continent-dropdown-left', 'value'),
     Output('continent-dropdown-right', 'value'),
     Output('country-dropdown-left', 'value'),
     Output('country-dropdown-right', 'value'),
     Output('city-dropdown-left', 'value'),
     Output('city-dropdown-right', 'value')],
    [Input('refresh-btn', 'n_clicks')]
)
def reset_dropdowns(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    return None, None, None, None, None, None



#####################################################Timeline##############################################################
@app.callback(
    [Output("timeline-slider", prop) for prop in ["min", "max", "value", "marks"]],
    [Output("transport-title", "children"),
     Output("slider-container", "style")],
    [Input('transport-dropdown', 'value')],
    prevent_initial_call=True
)
def update_timeline_slider(transport_type):
    if transport_type == "Tramway":
        min_year = df_Timeline_Tram["Decade"].min()
        max_year = df_Timeline_Tram["Decade"].max()
    elif transport_type == "Metro":
        min_year = df_Timeline_Metro["Decade"].min()
        max_year = df_Timeline_Metro["Decade"].max()
    elif transport_type == "BRT":
        min_year = df_Timeline_BRT["Decade"].min()
        max_year = df_Timeline_BRT["Decade"].max()
    else:
        min_year, max_year = 0, 0

    marks = {i: str(i) for i in range(min_year, max_year + 1, 10)}
    value = [min_year, max_year]

    display_style = {'display': 'block' if transport_type else 'none'}
    title_text = f"Timeline of System {transport_type}"
    return min_year, max_year, value, marks, title_text, display_style

@app.callback(
    Output("timeline-graph", "figure"),
    Input("timeline-slider", "value"),
    Input('transport-dropdown', 'value'),
)
def update_timeline_graph(selected_years, transport_type):
    if transport_type == "Tramway":
        df_filtered = df_Timeline_Tram
    elif transport_type == "Metro":
        df_filtered = df_Timeline_Metro
    elif transport_type == "BRT":
        df_filtered = df_Timeline_BRT
    else:
        df_filtered = df_Timeline_Tram

    filtered_Timeline = df_filtered[
        (df_filtered["Decade"] == selected_years[1])
    ]
    max_count = filtered_Timeline.loc[filtered_Timeline['Decade'] == selected_years[1], 'Count'].max()

    fig = px.choropleth(
        filtered_Timeline,
        locations='Country code',
        range_color=[0, max_count],
        color='Count',
        color_continuous_scale='reds',
        template="plotly_dark",
        basemap_visible=True,
        hover_data=['Country', 'Decade', 'Count']
    )
    fig.update_layout(height=800)

    return fig

@app.callback(
    Output("tramway-info", "data"),
    [Input("timeline-graph", "clickData"),
     Input("timeline-slider", "value"),
     Input('transport-dropdown', 'value')],
    prevent_initial_call=True
)
def update_datatable(clicked_data, selected_years, transport_type):
    if clicked_data is None:
        raise PreventUpdate

    if transport_type == "Tramway":
        df_filtered = df_Timeline_Tram
    elif transport_type == "Metro":
        df_filtered = df_Timeline_Metro
    elif transport_type == "BRT":
        df_filtered = df_Timeline_BRT
    else:
        df_filtered = df_Timeline_Tram

    country = clicked_data["points"][0]["customdata"][0]
    filtered_country = df_filtered[
        (df_filtered["Decade"] >= selected_years[0]) &
        (df_filtered["Decade"] <= selected_years[1]) &
        (df_filtered["Country"] == country)
    ]
    
    selected_columns=["Country","Continent","Decade","Count","Population","type"]
    filtered_data = filtered_country[selected_columns]

    return filtered_data.to_dict("records")

@app.callback(
    Output("line-chart-container", "style"),
    [Input("timeline-graph", "clickData")],
)
def update_line_chart_visibility(clicked_data):
    if clicked_data is None:
        return {'display': 'none'}
    else:
        return {'display': 'block'}

# Update the existing line chart callback
@app.callback(
    Output("line-chart", "figure"),
    [Input("timeline-graph", "clickData"),
     Input("timeline-slider", "value"),
     Input('transport-dropdown', 'value')],
    prevent_initial_call=True
)
def update_line_chart(clicked_data, selected_years, transport_type):
    if clicked_data is None:
        raise PreventUpdate

    if transport_type == "Tramway":
        df_filtered = df_Timeline_Tram
        transit='Tramway'
    elif transport_type == "Metro":
        df_filtered = df_Timeline_Metro
        transit='Metro'
    elif transport_type == "BRT":
        df_filtered = df_Timeline_BRT
        transit='BRT'
    else:
        df_filtered = df_Timeline_Tram
        transit='Tramway'

    country = clicked_data["points"][0]["customdata"][0]
    filtered_country = df_filtered[
        (df_filtered["Decade"] >= selected_years[0]) &
        (df_filtered["Decade"] <= selected_years[1]) &
        (df_filtered["Country"] == country) &
        (df_filtered["Count"].notnull())
    ]
    fig = px.line(filtered_country, x='Decade', y='Count', template="plotly_dark")
    fig.update_layout(title=dict(text=f"{transit} Sysyems in {country}", x=0.5, font=dict(color='#008080')))
    return fig    
        
#####################################################Global Charts##############################################################
@app.callback(
    Output("global-charts", "children"),
    [Input('chart-dropdown', 'value')]
)
def update_global_charts(transport_type):
    charts = []  

    if transport_type == "Tramway":
        
        
        charts.append(dcc.Graph(figure=create_plotly_lineplot(df_Timeline_Tram_Continent, 'Decade', 'Count', 'Continent',
                                             'Number of Systems in Decades Trams',
                                             "Decade", 'Number of Systems')))
        charts.append(html.Br())  # Line break

        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_Tramway', "Continent",
                                              'Class', "Global Length of Tram",
                                              "Length (km)", "Continent")))
        charts.append(html.Br())  # Line break
        
        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_per_capita_Tramway', "Continent",
                                              'Class', "Global Length per capita of Trams",
                                              "Length Per Capita (x10^5)", "Continent")))
        charts.append(html.Br())
        df_Temp=df_city
        df_Temp["Transit"]=df_Temp.apply(isolate_transit, axis=1, transit_type="Tram")
        df_barchart= df_Temp[df_Temp["Transit"]=="Tram"]
        print()
        
        charts.append(dcc.Graph(figure= barplot_combined(df_barchart, 'Transit', 'length_Tramway', 'Continent', 'Class',
                              'Transit', 'Length', 
                              'Length of Tram Systems', ['Country','City',"Population"]) ))


    elif transport_type == "Metro":
        
        charts.append(dcc.Graph(figure=create_plotly_lineplot(df_Timeline_Metro_Continent, 'Decade', 'Count', 'Continent',
                                             'Number of Systems in Decades Metro',
                                             "Decade", 'Number of Systems')))
        charts.append(html.Br())  # Line break

        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_Metro', "Continent",
                                              'Class', "Global Length of Metro",
                                              "Length (km)", "Continent")))
        charts.append(html.Br())
        # Line break
        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_per_capita_Metro', "Continent",
                                              'Class', "Global Length per capita of Metro",
                                              "Length Per Capita (x10^5)", "Continent")))
        charts.append(html.Br())
        df_Temp=df_city
        df_Temp["Transit"]=df_Temp.apply(isolate_transit, axis=1, transit_type="Metro")
        df_barchart= df_Temp[df_Temp["Transit"]=="Metro"]
        
        charts.append(dcc.Graph(figure= barplot_combined(df_barchart, 'Transit', 'length_Metro', 'Continent', 'Class',
                              'Transit', 'Length', 
                              'Length of Mertro Systems', ['Country','City',"Population"]) ))

    # Add similar logic for BRT and Total charts here
    elif transport_type == "BRT":
               
        charts.append(dcc.Graph(figure=create_plotly_lineplot(df_Timeline_BRT_Continent, 'Decade', 'Count', 'Continent',
                                             'Number of Systems in Decades BRT',
                                             "Decade", 'Number of Systems')))
        charts.append(html.Br())  # Line break

        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_BRT', "Continent",
                                             'Class', "Global Length of BRT",
                                             "Length (km)", "Continent")))
        charts.append(html.Br())
      #  Line break
        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_per_capita_BRT', "Continent",
                                             'Class', "Global Length per capita of BRT",
                                             "Length Per Capita (x10^5)", "Continent")))
        charts.append(html.Br())
        df_Temp=df_city
        df_Temp["Transit"]=df_Temp.apply(isolate_transit, axis=1, transit_type="BRT")
        df_barchart= df_Temp[df_Temp["Transit"]=="BRT"]
        
        charts.append(dcc.Graph(figure= barplot_combined(df_barchart, 'Transit', 'length_BRT', 'Continent', 'Class',
                             'Transit', 'Length', 
                             'Length of BRT Systems', ['Country','City',"Population"]) ))
    
    elif transport_type == "Total":
        charts.append(dcc.Graph(figure=create_plotly_lineplot(df_Timeline_Total_Continent, 'Decade', 'Count', 'Continent',
                                             'Number of Systems in Decades Tram+Metro+BRT',
                                             "Decade", 'Number of Systems')))
      
        charts.append(html.Br())  # Line break

        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'Total Length', "Continent",
                                              'Class', "Global Length of Tram+Metro+BRT",
                                              "Total Length (km)", "Continent")))
        charts.append(html.Br())
        
        charts.append(dcc.Graph(figure=create_plotly_stripplot(df_city, 'length_per_capita', "Continent",
                                              'Class', "Global Length per capita of Tram+Metro+BRT",
                                              "Length Per Capita (x10^5)", "Continent")))

        charts.append(html.Br())
        
    return charts
#####################################################app.layout##############################################################

content=html.Div(id='page-content',style={"padding":"2rem"})

app.layout = dbc.Container([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(sidebar,width=2),
        dbc.Col(content,width={"size":10,"offset":0})
    ])
],fluid=True)
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)

def display_page(pathname):
    if pathname == '/':
        return dashboard1_layout
    elif pathname == '/city-info':
        return dashboard2_layout
    elif pathname == '/timeline':
        return dashboard3_layout
    elif pathname == '/global-charts':
        return dashboard4_layout
    elif pathname == '/global-maps':
        return dashboard5_layout    
    elif pathname == '/about':
        return dashboard6_layout
    #return dbc.Jumbotron([
     #   html.H1("404: Not found",className="text-danger"),
      #  html.Hr(),
      #  html.P(f"The pathname {pathname} was not recognised...")
   # ])

if __name__ == '__main__':
    app.run_server(debug=True,port=2000)

