import requests
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
import sqlite3
from sqlite3 import Error
import getpass


def conecta_ao_db(db_arquivo):
    """
    Conecta à base de dados SQLite, se o arquivo não existir, ele será criado.
    :param db_arquivo: caminho absoluto ou relativo ao arquivo_db
    :return: conexão sqlite3
    """
    sqlite3_conn = None

    try:
        sqlite3_conn = sqlite3.connect(db_arquivo)
        return sqlite3_conn

    except Error as err:
        print(err)

        if sqlite3_conn is not None:
            sqlite3_conn.close()




def clube_id_e_sessao():

    """Esta função inicializa a sessão requests para poder pegar os dados na API do Sokker e pega o id do clube.

      param: 
  
              login_name-> Login do usuário no sokker
  
              password -> senha do usuário no sokker

      return: sessao-> variável que será utilizada para pegar os dados da API após o login feito
      
              id do clube -> variável a ser utilizad para pegar as informações do clube do usuário logado quando necessário
    """

    # Informações de login
    
    login_name= input('Login: ')
    password= getpass.getpass('Password: ')

    # Request Session
    session = requests.Session()
  
    # login no sokker
    url_login= 'https://sokker.org/start.php?session=xml'
    cadastro= {'ilogin': login_name, 'ipassword': password}
  
    logging = session.post(url_login, data = cadastro)
    status= logging.status_code

    # Pegando o id do clube logado
    id_club = logging.text.split('=')[1]

    if len(id_club) <= 2:
        print("Algo errado ocorreu ao tentar acessar a API do jogo. Vá ao link (https://online.sokker.org/xmlinfo.php) e cheque o problema a partir do resultado da variável id_club e seu problema correspondente neste site.")
        
    else:
        print(f'Clube ID: {id_club}')
  
    return session, id_club



def pega_dados(url, sessao, search, tree_top= False):
    
    """Esta função pega os dados solicitados utilizando a estrutura XML da API do Sokker
    
    param:
    
    url -> url da API
    
    sessao -> Sessão iniciada a partir da função clube_id_e_sessao
    
    search -> topo da estrutura XML a partir da qual será pego os elementos
    
    tree_top -> se True, pega o topo da árvore XML que identifica o topo geral da árvore; se False, pega os elementos a partir da tag que está no topo de cada elemento desejado.
        
        Exemplo: para pegar as informações dos jogadores, podemos tanto colocar tree_top igual a True e como argumento de search utilizarmos o termo 'players' (topo geral do XML que guarda as informações dos jogadores); quanto colocarmos o tree_top igual a False e o argumento de search como player (singular) que é a tag que está no topo de CADA jogador específico.
        
        return: DataFrame com as informações solicitadas à API
        
        Para mais informações sobre a API e os links para cada informação: https://online.sokker.org/xmlinfo.php
    """

    #Acessa a url da API com os dados
    resp = sessao.get(url)
  
    # Cria objeto árvore de elementos
    root = ET.fromstring(resp.content)
  
    #Lista que guardará todas as informações retornadas pela API
    news_items= list()

    # Dicionário de cada elemento que será guardado na lista geral acima
    news = {}

    if tree_top:
  
    # Itera sobre cada elemento e pega suas informações guardando em um dataframe pandas
        for item in root.find(search):

            news= {}
  
            for child in item:
    
                news[child.tag] = child.text
  
            news_items.append(news)

        df= pd.DataFrame(news_items)

    else:

        # Itera sobre cada elemento e pega suas informações guardando em um dataframe pandas
        for item in root.findall(search):

            news= {}
  
            for child in item:
    
                news[child.tag] = child.text
  
            news_items.append(news)

        df= pd.DataFrame(news_items)


    return df