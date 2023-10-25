import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, ClientsideFunction, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime as dt
from babel.numbers import format_currency

path = 'database' #r'Z:\Clientes\WPC\PROJETO BI PREVIDENCIA\PROVISÕES MATEMÁTICAS'
balancete_pivot_test = pd.read_csv(path+'/balancete_pivot.csv',encoding='latin-1')
balancete_pivot_test.competencia = pd.to_datetime(
    balancete_pivot_test.competencia, dayfirst=False, errors="coerce", format="%Y-%m-%d"
)

#anos = list(balancete_pivot_test.ANO.unique())
anos = balancete_pivot_test.competencia.drop_duplicates().sort_values(ascending=False).dt.strftime('%m-%Y').drop_duplicates().tolist()
#anos.sort(reverse=True)

planos = list(balancete_pivot_test.PLANO.unique())
planos.sort(reverse=False)

#===============
ativo_total = '1'
exigivel_operacional = '2.01'
exigivel_contingencial = '2.02'
patrimonio_social =  '2.03'
patrimonio_cobertura =  '2.03.01'
provisoes_matematicas = '2.03.01.01'
provisoes_constituir =  '2.03.01.01.03'

for i in [exigivel_operacional,
exigivel_contingencial,
patrimonio_social,
patrimonio_cobertura,
provisoes_matematicas]:
    balancete_pivot_test[i] = balancete_pivot_test[i] * -1

colunas = [
    'solvencia_seca',
    'solvencia_gerencial',
    'solvencia_liquida',
    'resultado_operacional',
    'maturiade_atuarial',
    'solvencia_financeira',
    'risco_legal',
    'provisoes_cd',
    'passivo_integralizar',
    'provisoes_bd',
    ativo_total,
    exigivel_operacional,
    exigivel_contingencial,
    patrimonio_social,
    patrimonio_cobertura,
    provisoes_matematicas,
    'resultado',
]

colunas_indicadores = [
    'Solvência Seca',
    'Solvência Gerencial',
    'Solvência Líquida',
    'Resultado Operacional',
    'Maturiade Atuarial',
    'Solvência Financeira',
    'Risco Legal',
    'Provisões CD',
    'Passivo a Integralizar',
    'Provisões BD',
    'Ativo Total',
    'Exigível Operacional',
    'Exigível Contingencial',
    'Patrimônio Social',
    'Patrimônio Cobertura',
    'Provisões Matemáticas',
    'Resultado',
]

contabil = [
    ativo_total,
    exigivel_operacional,
    exigivel_contingencial,
    patrimonio_social,
    patrimonio_cobertura,
    provisoes_matematicas,
    'resultado',]

porcentagem = [
    'risco_legal',
    'provisoes_cd',
    'passivo_integralizar',
    'provisoes_bd',
]

ipca = pd.json_normalize(requests.get("http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='PRECOS12_IPCAG12')").json()['value'])
ipca.VALDATA = pd.to_datetime(ipca.VALDATA.str[:10])

# =======================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server
# ========================

def variacao(coluna,mes,plano):
    mes_anterior = pd.to_datetime(mes) - relativedelta(months = 1)
    variacao = balancete_pivot_test[(balancete_pivot_test.PLANO == plano)&(balancete_pivot_test.competencia == mes)][coluna].values / balancete_pivot_test[(balancete_pivot_test.PLANO == plano)&(balancete_pivot_test.competencia == mes_anterior)][coluna].values - 1
    if np.isnan(variacao):
        return "-"
    else:
        return "{:.2%}".format(variacao[0]).replace(".",",")

def grafico(visualizacao,col,title,tickformat = 'n'):

    fig1 = go.Figure(layout={"template": "plotly_white"})
    x = visualizacao.competencia
    y = round(visualizacao[col],2)

    hover = "%{x|%b, %Y} <br>" + title + ": %{y}"

    fig1.add_trace(
        go.Scatter(
            x=x, 
            y=y,
            name="",
            hovertemplate=hover,
            line = dict(color='#003e4c', width=4)))

    fig1.update_layout(
        height=360,
        width=560,
        margin=dict(l=10, r=10, b=10, t=60),
        title={
            "text": title,
            "font": dict(size=17),
            "y": 0.9,
            'x':1,
            'xanchor': 'right',
            "yanchor": "top",
        },
        legend=dict(
            yanchor="bottom", y=-0.25, xanchor="right", x=0.85, orientation="h"
        ),

        xaxis=dict(
            rangeselector=dict(
                buttons=list([

                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="12m",
                        step="year",
                        stepmode="backward"),
                    dict(count=1,
                        label="Ano atual",
                        step="year",
                        stepmode="todate"),
                    dict(label='Completo',
                         step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),

        yaxis=dict(
            side="left",
#            range=[0,max(y) * 1.3],
            #autorange=True,
        ),
    )

    if tickformat == 's':
        fig1.update_layout(yaxis=dict(tickformat = 'p'))

    fig1.update_yaxes(mirror=True, showline=True, linewidth=2, rangemode="tozero",showspikes=True,)
    fig1.update_xaxes(mirror=True, showline=True, linewidth=2)

    return fig1

def card(name,id):
    cardbody = dbc.Card([dbc.CardBody([
                                    html.Span(name, className="card-text"),
                                    html.H6(#style={"color": "#5d8aa7"}, 
                                            id=id),
                                    ])
                                ], color="#003e4c", outline=True,inverse=True, style={"margin-top": "20px",#"margin-left": "10px",
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                        #"color": "#FFFFFF"
                                        })
    return cardbody

def header():
    header_geral = html.Div([
        html.Div([
            dbc.Row([
                dbc.Col(
                    html.H3(
                        dbc.Badge(
                            "BI-Prev",
                            color="#a50000",
                            className="me-1",
                                    )
                        )
                    ),
                    dbc.Col([
                        html.Img(
                            id="logo",
                            src=app.get_asset_url("logo.png"),
                            height=50,
                            )
                        ],style={"textAlign": "right"},),
                    ]),
                ],style={
                    "background-color": "#003e4c",  # 003e4c",
                    "margin": "0px",
                    "padding": "20px",
                    },
        ),
        html.Div([
            dbc.Nav([
                dbc.Navbar(
                    dbc.Container(
                        children=[
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Indicadores   ",
                                    href="/indicadores",
                                    className="nav-link",
                                    ),
                                    style={
                                        "margin": "-20px",
                                        "margin-left": "20px",
                                    },
                                ),
                            dbc.NavItem(
                                dbc.NavLink('',#Menu 2   ',
                                             href='/prestadores', 
                                             className="nav-link"),
                                             style={"margin": "-20px",
                                                    "margin-left": "20px"},),
                            dbc.NavItem(
                                dbc.NavLink('',#'Menu 3   ',
                                             href='/beneficiarios', 
                                             className="nav-link"),
                                             style={"margin": "-20px",
                                                    "margin-left": "20px"},),
                                    ],
                            fluid=True,
                        ),
                        color="light",
                        dark=False,
                        # class_name='collapse navbar-collapse',
                    )
                ],class_name="navbar navbar-light bg-light",),
                # ]),
            ]),
    ])

    return header_geral

tela_indicadores = html.Div(children=[
        dbc.Row([
            header(),
        ]),

            html.Div([
        dbc.Row([
                dbc.Col([
                    html.H5(
                        dbc.Badge(
                            "Filtrar pela competência:",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "35px",
                                "margin-top": "10px",
                                },
                                    )
                            ),
                        dcc.Dropdown(
                            id="select-ano",
                            value=anos[0],
                            options=[
                                {
                                    "label": i,
                                    "value": i,
                                }
                                for i in anos
                            ],
                            placeholder="Selecione o período",
                            style={
                                #"width": "60%",
                                #'padding': '3px',
                                "margin-left": "15px",
                                #'font-size':'18px',
                                "textAlign": "center",
                            },
                            ),

                        ], width=2),
        
                    dbc.Col([
                    html.H5(
                        dbc.Badge(
                            "Selecionar o Plano:",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "0px",#"25px",
                                "margin-top": "10px",
                                },
                                    )
                            ),
                        dcc.Dropdown(
                            id="select-plano",
                            value=planos[0],
                            multi=False,
                            options=[
                                {
                                    "label": i,
                                    "value": i,
                                }
                                for i in planos
                            ],
                            placeholder="Selecione o Plano",
                            style={
                                "width": "95%",
                                #'padding': '3px',
                                "margin-left": "0px",#"15px",
                                #'font-size':'18px',
                                "textAlign": "center",
                            },
                            ),
                            ], width=2),
                            
]),
            dbc.Row([
                dbc.Col([
                        dbc.Row([
                            card("Solvência Seca","solvencia_seca"),
                            card("Solvência Gerencial","solvencia_gerencial"),
                            card("Solvência Líquida","solvencia_liquida"),
                            card("Resultado Operacional","resultado_operacional"),
                            card("Maturidade Atuarial",'maturiade_atuarial'),
                            card("Solvência Financeira",'solvencia_financeira'),
                            card("Risco Legal",'risco_legal'),
                            card("Provisões em CD",'provisoes_cd'),
                            card("Passivo a Integralizar",'passivo_integralizar'),
                            card("Provisões em BD",'provisoes_bd'),
                            card("Ativo Total",'ativo'),
                            card("Exigível Operacional",'exig_operacional'),
                            card("Exigível Contingencial",'exig_contingencial'),
                            card("Patrimônio Social",'patrimonio_social'),
                            card("Patrimônio Líquido de Cobertura",'plc'),
                            card("Provisões Matemáticas",'provisoes'),
                            card("Resultado",'resultado'),
                        ],style={"margin-left": "25px",},),
                        ],md=2),

                   dbc.Col([
                       html.Div([], id='tabela_provisoes'),
                       dcc.Loading(
                            id="loading-1",
                            type="dot",
                            #children=html.Div(id="loading-output-1")
                            ),
                       dcc.Loading(
                            id="loading-2",
                            type="dot",
                            #children=html.Div(id="loading-output-2")
                            ),
                       
                   dbc.Row([ 
                   dbc.Col([
                       html.Div([
                       dcc.Graph(id="solvencia_seca_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),
                       dcc.Graph(id="solvencia_liquida_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),
                       dcc.Graph(id="maturidade_atuarial_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),
                       dcc.Graph(id="risco_legal_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),
                       dcc.Graph(id="passivo_integralizar_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                       dcc.Graph(id="ativo_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),
                       dcc.Graph(id="ex_cont_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),
                       dcc.Graph(id="plc_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),                                                                                                                                                                                                                  
#                       dcc.Graph(id="resultado_graph",
#                          style={"margin-top": "50px",
#                                "margin-left": "15px",},),
                       ],"One of two columns"),
                   ],#md=5, 
                   align="start"),

                       dbc.Col([
                           html.Div([
                       dcc.Graph(id="solvencia_gerencial_graph",
                          style={"margin-top": "50px"},),
                       dcc.Graph(id="resultado_operacional_graph",
                          style={"margin-top": "50px"},),
                       dcc.Graph(id="solvencia_financeira_graph",
                          style={"margin-top": "50px"},),
                       dcc.Graph(id="provisoes_cd_graph",
                          style={"margin-top": "50px"},),
                       dcc.Graph(id="provisoes_bd_graph_graph",
                          style={"margin-top": "50px"},),
                        dcc.Graph(id="ex_opera_graph",
                          style={"margin-top": "30px"},),
                       dcc.Graph(id="patrimonio_social_graph",
                          style={"margin-top": "50px"},),
                       dcc.Graph(id="provisoes_graph",
                          style={"margin-top": "50px"},),
                        dcc.Graph(id="resultado_graph",
                          style={"margin-top": "50px",
                                "margin-left": "0px",},),

                       ],"One of two columns"),
                   ],#md=5, 
                   align="end"),
                ]),
                
                ],style={"margin-left": "0px",
                         "margin-top": "15px",}, 
                         #width=9
                         ),

                        ]),
                        
                        ]),
                        ])

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)
# CALLBACKS =====

@app.callback(
    [   Output("loading-1", "children"),
        Output("solvencia_seca", 'children'),
        Output("solvencia_gerencial", 'children'),
        Output("solvencia_liquida", 'children'),
        Output("resultado_operacional", 'children'),
        Output('maturiade_atuarial', 'children'),
        Output('solvencia_financeira', 'children'),
        Output('risco_legal', 'children'),
        Output('provisoes_cd', 'children'),
        Output('passivo_integralizar', 'children'),
        Output('provisoes_bd', 'children'),
        Output('ativo', 'children'),
        Output('exig_operacional', 'children'),
        Output('exig_contingencial', 'children'),
        Output('patrimonio_social', 'children'),
        Output('plc', 'children'),
        Output('provisoes', 'children'),
        Output('resultado', 'children'),
    ],
    [
        Input('select-ano', 'value'),
        Input('select-plano', 'value'),
    ],
)
def update_cards(ano, plano):

    base_filtrada = balancete_pivot_test[(balancete_pivot_test.PLANO == plano) & (balancete_pivot_test.competencia == ano)].copy()

    if len(base_filtrada) == 0:
        return ['-' for i in colunas]
    
    else:
        valores = base_filtrada[colunas].copy()

    #    for i in contabil:
    #        valores[i] = format_currency(valores[i].fillna(0), "BRL", locale="pt_BR")
        for i in porcentagem:
            valores.loc[:,i] = ((round(valores[i] * 100 + 0.0,2)).astype(str) + ' %').str.replace('.',',',regex=False)
#            valores.loc[:,i] = valores.loc[:,i].str.replace('-0,0 %','0,0 %', regex=False)
    #        valores[i] = (str(round(valores[i]*100,2))+'%').replace(".", ",")

        for i in valores[contabil]:
            valores[i] = [format_currency(v + 0.0, "BRL", locale="pt_BR") for v in valores[i]]
            #valores[i] = valores[i].str.replace('-R$ 0,00','R$ 0,00', regex=False)

        for i in valores[valores.columns[:6]]:
            valores[i] = round(valores[i] + 0.0,4).astype(str).str.replace('.',',',regex=False)
            valores[i] = valores[i].str.replace(r'[-+]?\binf\b', '',regex=True)
        
        outputs = []
        outputs.append('')
        [outputs.append(i)for i in valores.values[0]]
    
        return [i for i in outputs]

@app.callback(
    [   Output("loading-2", "children"),
        Output("solvencia_seca_graph",'figure'),
        Output("solvencia_liquida_graph",'figure'),
        Output("maturidade_atuarial_graph",'figure'),
        Output("risco_legal_graph",'figure'),
        Output("passivo_integralizar_graph",'figure'),                                                                                                                                                                    
        Output("ativo_graph",'figure'),
        Output("ex_cont_graph",'figure'),
        Output("plc_graph",'figure'),                                                                      
        Output("resultado_graph",'figure'),                                                                      
        Output("solvencia_gerencial_graph",'figure'),
        Output("resultado_operacional_graph",'figure'),
        Output("solvencia_financeira_graph",'figure'),
        Output("provisoes_cd_graph",'figure'),
        Output("provisoes_bd_graph_graph",'figure'),
        Output("ex_opera_graph",'figure'),
        Output("patrimonio_social_graph",'figure'),
        Output("provisoes_graph",'figure'),
    ],
    [
        Input('select-ano', 'value'),
        Input('select-plano', 'value'),
    ],
)
def update_graphs(ano, plano):
    base_grafico = balancete_pivot_test[(balancete_pivot_test.PLANO == plano)].copy().sort_values(by='competencia')

    lista_graficos=['']

    for col,ind in zip(colunas,colunas_indicadores):
        tickf = 's' if col in porcentagem else 'n'
        
        lista_graficos.append(grafico(
        base_grafico,
        col,
        ind,
        tickf,
        ))

    
    return [i for i in lista_graficos]
    #

@app.callback(
    
        Output('tabela_provisoes','children')
    ,    
    [
        Input('select-ano', 'value'),
        Input('select-plano', 'value'),
    ],
)
def update_table(mes,plano):
    mes = pd.to_datetime(mes)
    mes_anterior = mes - relativedelta(months = 1)
    ipca_filtro1 = mes_anterior if plano =='BD-01' else mes
    ipca_filtro2 = pd.to_datetime(mes_anterior) - relativedelta(months = 1) if plano == 'BD-01' else mes_anterior

    tabela = {'Conceitos':
    [  'Variação das Provisões Matemáticas',
        'Variação das Provisões Matemáticas - Benefícios Concedidos - BD',
        'Variação das Provisões Matemáticas - Benefícios Concedidos - CD',

        'Variação das Provisões Matemáticas - Benefícios a Conceder - BD',
        'Variação das Provisões Matemáticas - Benefícios a Conceder - CD',

        'Variação das Provisões a Constituir',
        'Inflação do período (t-1)' if plano =='BD-01' else 'Inflação do período (t)'
        ],
    str(mes)[:7]:
    [   variacao(provisoes_matematicas,mes,plano),
        variacao('prov_concedidos_bd',mes,plano),
        variacao('prov_concedidos_cd',mes,plano),
        variacao('prov_conceder_bd',mes,plano),
        variacao('prov_conceder_cd',mes,plano),
        variacao(provisoes_constituir,mes,plano),
        '{:.2f}%'.format(ipca[ipca.VALDATA == ipca_filtro1].VALVALOR.values[0]).replace(".",",")
    ],
    str(mes_anterior)[:7]:
    [   variacao(provisoes_matematicas,mes_anterior,plano),
        variacao('prov_concedidos_bd',mes_anterior,plano),
        variacao('prov_concedidos_cd',mes_anterior,plano),
        variacao('prov_conceder_bd',mes_anterior,plano),
        variacao('prov_conceder_cd',mes_anterior,plano),
        variacao(provisoes_constituir,mes_anterior,plano),        
        "{:.2f}%".format(ipca[ipca.VALDATA == ipca_filtro2].VALVALOR.values[0]).replace(".",",")
        ]
        
        }
    tabela_df = pd.DataFrame.from_dict(tabela).fillna('-')

    tabela_dash = dash_table.DataTable(
    columns=[
        {"name": i,
            "id": i,
            "deletable": False,
            }
        for i in tabela_df.columns
    ],
    data=tabela_df.to_dict("records"),
    style_as_list_view=True,
    style_header={
        "backgroundColor": "#003e4c",
        "color": "white",
        "fontWeight": "bold",
        "text-align": "center",
        "fontSize": 14,
    },
    style_data_conditional=[
        {"if": {"column_id": tabela_df.columns[0]},
            "textAlign": "left", },
            ],

    style_cell={
        "padding": "8px",
        "font-family": "Helvetica",
        "fontSize": 13,
        "color": "#5d8aa7",
        "fontWeight": "bold",
    },
    fill_width=False,
)

    return tabela_dash

# Update page =========================

@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if (
        pathname == "/indicadores"
        or pathname == "/"
    ):
        return tela_indicadores
    elif pathname == '/prestadores':
        return #tela_prestadores
    
    elif pathname == '/beneficiarios':
        return #tela_beneficiarios
        
    else:
        return tela_indicadores

#======================================

if __name__ == "__main__":
    app.run_server(debug=False)  # , port=8051)
