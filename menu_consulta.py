#!/usr/bin/env python3
# coding=utf-8

##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#      ver: 1.2  05/04/2021  #
##############################

import os
import sys
import time
import asyncio
import pathlib
import subprocess
import configparser
from snmp import py_snmp
from decouple import Config, RepositoryEnv # pip install python-decouple
from PyInquirer import style_from_dict, Token, prompt, Separator

# TODO:
# - Opção de receber uma caixa e consultar a pon dela - OK
# - Opção de consultar uma olt inteira (junto com opções de placa)
# - Mostrar a letra da placa junto, e ir montando o formato com as opções selecionadas no menu
# formato: qck-abc-1.01

STYLE = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

#DOTENV_FILE = '/home/lucas/Dev/snmp-consultas/.env'
DOTENV_FILE = f'{os.path.dirname(os.readlink(os.path.abspath(__file__)))}/.env'
config = Config(RepositoryEnv(DOTENV_FILE))
SNMP_COMMUNITY = config('COMMUNITY')

def get_config(file_name, item=None):
    if item:
        config = configparser.ConfigParser()
        config.read(str(pathlib.Path(__file__).parent.absolute()) + f'/{file_name}.ini')
        return config[f'{item}']
    else:
        config = configparser.ConfigParser()
        config.read(str(pathlib.Path(__file__).parent.absolute()) + f'/{file_name}.ini')
        return config

def get_olts(olts_parser):
    olts = {}
    for olt in olts_parser:
        olts[olt] = olts_parser[olt]
    return olts

def get_placas(placas_gpon_parser):
    placas_gpon = {}
    for placa in placas_gpon_parser:
        placas_gpon[placa] = placas_gpon_parser[placa]
    return placas_gpon

def opcoes(todos_itens, menu_option, todas_pons=None): # todos_itens = tuple
    itens = []
    for item in todos_itens:
        itens.append({'name': item.upper()})
    if todas_pons:
        itens.append({'name': 'olt inteira'})
    itens.append({'name': menu_option})
    return itens

def opcoes_menu(opcoes_lista, modo, menu_option):
    gerar_opcoes = [{
            'type': 'list',
            'message': f'Selecione a {modo} desejada:',
            'name': f'{modo}s',
            'choices': opcoes(opcoes_lista, menu_option)}] # OLTS
    escolha = prompt(gerar_opcoes, style=STYLE)
    resposta = ''.join(valor for valor in escolha.values())
    return resposta

def consulta_caixa(caixa, placas_gpon_parser):
    # Retorna qual a olt, slot e pon de uma caixa no formato qck-aaa-1.01 
    olt_nome, olt_ip = mapear_letra(caixa[4:5], "olt")
    placa   = f'PLACA_{mapear_letra(caixa[5:6], "placa", olt_nome)}'
    pon_ind = mapear_letra(caixa[6:7], "pon")
    pon     = placas_gpon_parser.get(placa, pon_ind)
    return olt_ip, pon

def mapear_letra(letra, modo, olt=None):
    alpha = 'a b c d e f g h i j k l m n o p'.split()
    # para mudar a ordem(posição) da placa de cada OLT, é só colocar na ordem direto no config.ini
    estrutura_olt = {
            'a': 'Volta Redonda', 'b': 'Barra Mansa', 'c': 'Bela Roma', 'd': 'Porto Real',
            'e': 'Quatis', 'f': 'Tati', 'g': 'Penedo', 'h': 'Pirai'
    }
    olts_parser = get_config('snmp/config', 'OLTS')
    
    if modo == 'olt':    
        olt = estrutura_olt[letra]
        return olt, olts_parser[olt].split()[0]

    elif modo == 'placa':
        placas_olt_selecionada = olts_parser[olt].split()[1:]
        estrutura_placa = {}
        for ind, placa in enumerate(placas_olt_selecionada):
            estrutura_placa[alpha[ind]] = placa
        if letra in estrutura_placa:
            return estrutura_placa[letra]
        else:
            print(f"Essa OLT não possui a placa selecionada ({letra})!")
            sys.exit()

    elif modo == 'pon':
        return f'PON_{str(alpha.index(letra)).upper()}'

    else:
        return "Opção não encontrada!"

async def resultado(olt_ip, pon, olt_inteira=None):
    last_downtime = await py_snmp.last_downtime(olt_ip, SNMP_COMMUNITY, pon)
    down_cause = await py_snmp.last_down_cause(olt_ip, SNMP_COMMUNITY, pon)
    desc_all = await py_snmp.descricao(olt_ip, SNMP_COMMUNITY, pon)
    status_all = await py_snmp.status(olt_ip, SNMP_COMMUNITY, pon)
    
    clientes_com_los = {}
    if olt_inteira:
        print('\n\t--- TODOS ---\n')
        print('DESC\tSTATUS\tDOWN_CAUSE\tHORÁRIO')
    for desc, status, down_c, horario in zip(desc_all, status_all, down_cause, last_downtime):
        if down_c == 'los' or down_c == 'sem_info':
            clientes_com_los[desc] = [down_c, horario]
        if olt_inteira:
            print(f'{desc}\t{status}\t{down_c}\t{horario}')
    print(f'Total de ONUs na PON: {len(desc_all)}\n')

    # printa os clientes capturados no loop anterior.
    # Isso é apenas pra facilitar algum diagnóstico
    print('\n\t--- ONUs OFFLINE ---\n')
    print('DESC\tDOWN_CAUSE\tHORÁRIO')
    for _, (desc, status, down_c, horario) in enumerate(zip(desc_all, status_all, down_cause, last_downtime)):
        if status == 'offline':
            print(f'{desc}\t{down_c}\t{horario}')
    print(f"Total de ONUs offline na PON: {status_all.count('offline')}")

async def main():
    #subprocess.Popen("clear")
    from pyfiglet import Figlet
    # http://www.figlet.org/examples.html
    print(Figlet("eftifont").renderText('CONSULTAS GPON'))
    
    olts_parser = get_config('snmp/config', 'OLTS')
    placas_gpon_parser = get_config('snmp/placas_gpon_huawei')
    olts = get_olts(olts_parser)
    placas_gpon = get_placas(placas_gpon_parser)

    olt_inteira = None
    if len(sys.argv) > 2:
        print("Gerando relatório de todos clientes, além dos offline.")
        olt_inteira = 'olt inteira'

    if len(sys.argv) > 1:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print("Ajuda:\n-h [--help]: Esse menu\n\nModo de usar:\n\
                menu_consulta [caixa]|[tudo] [tudo]\n    \
                    ex1: menu_consulta qck-abc-1.01 ---> consulta apenas a pon ABC\n\
                            ex2: menu_consulta tudo ---> consulta a olt inteira da pon a ser selecionada no próximo menu\n\
                                    ex3: menu_consulta qck-abc-1.01 tudo ---> consulta a olt inteira da pon ABC")
            sys.exit()
        if sys.argv[1] == 'tudo':
            olt_inteira = 'olt inteira'
        else: # caixa nap passada
            caixa_olt, pon = consulta_caixa(sys.argv[1], placas_gpon_parser)
            if olt_inteira:
                resultado(caixa_olt, pon, olt_inteira=True)
            else:
                print(caixa_olt, pon)
                resultado(caixa_olt, pon)
            sys.exit()

    while True:
        # Opções de qual OLT será consultada
        resposta_olt = opcoes_menu(tuple(olts.keys()), 'OLT', 'sair')
        if resposta_olt == 'sair':
            print('Volte sempre!')
            time.sleep(0.5)
            sys.exit()

        #Pega as informações da OLT escolhida acima
        olt_selecionada = olts.get(resposta_olt.lower())
        olt_ip = olt_selecionada.split()[0]
        olt_placas_opcoes = []
        for placa in olt_selecionada.split()[1:]: # retorna assim: ip placa1 placa2 placa3 ...
            olt_placas_opcoes.append(f'Placa_{placa}')

        # Opções de qual Placa da OLT será consultada
        resposta_placa = opcoes_menu(tuple(olt_placas_opcoes), 'PLACA', 'voltar')
        if resposta_placa == 'voltar':
            continue

        # Opções de qual PON da Placa da OLT será consultada
        pons = (f'PON_{p}' for p in range(16))
        resposta_pon = opcoes_menu(pons, 'PON', 'voltar')
        if resposta_pon == 'voltar':
            continue
        
        print(f"OLT Selecionada: {resposta_olt}")
        print(f"Placa Selecionada: {resposta_placa}")
        print(f"PON selecionada: {resposta_pon}")

        pon = placas_gpon.get(resposta_placa)[resposta_pon]
        
        if olt_inteira:
            await resultado(olt_ip, pon, olt_inteira=True)
        else:
            await resultado(olt_ip, pon)
        
        denovo = input("\n\nDeseja consultar novamente? (s/N):  ")
        if denovo.lower().startswith('s'):
            continue
        sys.exit()

if __name__ == '__main__':
    asyncio.run(main())
