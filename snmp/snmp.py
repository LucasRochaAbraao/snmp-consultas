#!/usr/bin/env python3
# coding=utf-8

import sys
from easysnmp import Session
"""
community das olts: qn31415926
algumas pons para teste:
    PON = 4194345984 #0/4/4
    PON = 4194344960 #0/5/0
    PON = 4194347008 #0/5/8
    PON = 4194304000 #0/0/0
    PON = 4194361344 #0/7/0
    PON = 4194304000 #0/0/0
"""

def status(olt, comnty, pon=None):
    """ Retorna o status das ONUs da pon passada,
    1 = online,  2 = offline"""
    try: # Tentando criar a sessão snmp
        session = Session(hostname=olt, community=comnty, version=2)
    except: # algum parâmetro errado
        print(f"\nAlgum erro ao tentar criar uma sessão, antes mesmo de fazer o snmp walk!\nOLT: {olt}\nCommunity: {comnty}")
        sys.exit()
    try: # Tentando realizar o snmpwalk
        if pon: # pon específica
            status_snmp = session.walk(f'.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15.{pon}') # oid que retorna ONT status (online = 1, offline = 2)
        else: # olt inteira
            status_snmp = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15')
    except: # timeout
        print("Não foi possível realizar o snmp walk dos status. Aguarde alguns instantes e tente novamente. Saindo...")
        sys.exit()
    status = []
    for stat in status_snmp:
        if stat.value == '1':
            status.append('online')
        elif stat.value == '2':
            status.append('offline')
    return status

def descricao(olt, comnty, pon=None):
    """ Retorna as descrições das ONUs da PON passada."""
    try: # Tentando criar a sessão snmp
        session = Session(hostname=olt, community=comnty, version=2)
    except: # algum parâmetro errado
        print(f"\nAlgum erro ao tentar criar uma sessão, antes mesmo de fazer o snmp walk!\nOLT: {olt}\nCommunity: {comnty}")
        sys.exit()
    try: # Tentando realizar o snmpwalk
        if pon: # pon específica
            descs_snmp = session.walk(f'.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.9.{pon}') # oid que retorna descrições
        else: # olt inteira
            descs_snmp = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.9') # oid que retorna descrições
    except: # timeout
        print("Não foi possível realizar o snmp walk das descrições. Aguarde alguns instantes e tente novamente. Saindo...")
        sys.exit()
    descs = []
    for desc in descs_snmp:
        descs.append(desc.value) # extrai o valor da descrição
    return descs                 # retorna uma lista com as descrições

def last_downtime(olt, comnty, pon=None):
    """ Retorna data + hora da última queda de cada onu da pon passada. """
    try: # Tentando criar a sessão snmp
        session = Session(hostname=olt, community=comnty, version=2, use_sprint_value=False)
    except: # algum parâmetro errado
        print(f"\nAlgum erro ao tentar criar uma sessão, antes mesmo de fazer o snmp walk!\nOLT: {olt}\nCommunity: {comnty}")
        sys.exit()
    try: # Tentando realizar o snmpwalk
        if pon: # pon específica
            last_downtime = session.walk(f'.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.23.{pon}') # oid que retorna o Downtime (em hexadecimal)
        else: # olt inteira
            last_downtime = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.23') # oid que retorna o Downtime (em hexadecimal)
    except: # timeout
        print("Não foi possível realizar o snmp walk do último downtime. Aguarde alguns instantes e tente novamente. Saindo...")
        sys.exit()    
    last_downtime_formatado = []
    for data_bin in last_downtime:
        data_hex = bin_to_hex(data_bin.value)
        onu_dt_lst = data_hex.split()
        ano, mes, dia, hora, minuto, segundo = onu_dt_lst[0], onu_dt_lst[1], onu_dt_lst[2], onu_dt_lst[3], onu_dt_lst[4], onu_dt_lst[5]
        last_downtime_formatado.append(f'{int(dia, 16):02d}-{int(mes, 16):02d}-{int(ano, 16)} {int(hora, 16):02d}:{int(minuto, 16):02d}:{int(segundo, 16):02d}')
    return last_downtime_formatado

def bin_to_hex(hex_codes_entrada):
    """ Transforma valores binários no last_downtime() em hexadecimais. """
    octets = [ord(c) for c in hex_codes_entrada]
    return "{:02X}{:02X} {:02X} {:02X} {:02X} {:02X} {:02X}".format(*octets)

def last_down_cause(olt, comnty, pon=None):
    """ Retorna o motivo da última queda de cada onu da pon passada. """
    try: # Tentando criar a sessão snmp
        session = Session(hostname=olt, community=comnty, version=2)
    except: # algum parâmetro errado
        print(f"\nAlgum erro ao tentar criar uma sessão, antes mesmo de fazer o snmp walk!\nOLT: {olt}\nCommunity: {comnty}")
        sys.exit()
    try: # Tentando realizar o snmpwalk
        if pon: # pon específica
            resultado = session.walk(f'1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24.{pon}') # oid que retorna descrições
        else: # olt inteira
            resultado = session.walk('1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24') # oid que retorna descrições
    except: # timeout
        print("Não foi possível realizar o snmp walk do last down cause. Aguarde alguns instantes e tente novamente. Saindo...")
        sys.exit()
    resultados_value = []
    for res in resultado:
        if res.value == '2':
            resultados_value.append("___LOS___")
        elif res.value == '13':
            resultados_value.append("dying-gasp")
        elif res.value == '-1':
            resultados_value.append("info_zerada")
        else:
            resultados_value.append("cond_estranha")
    return resultados_value                 # retorna uma lista com as descrições

def potencia(olt, comnty, pon=None, tipo='onu'):
    """ Retorna o sinal rx de cada onu na pon passada.""" # Saída é meiia estranha :/ ex: ['HWTC\x84½\x00\x9a', 'HWTC¶\x9eD\x9c']
    sinais_snmp = []
    try: # Tentando criar a sessão snmp
        session = Session(hostname=olt, community=comnty, version=2)
    except: # algum parâmetro errado
        print(f"\nAlgum erro ao tentar criar uma sessão, antes mesmo de fazer o snmp walk!\nOLT: {olt}\nCommunity: {comnty}")
        sys.exit()
    try: # Tentando realizar o snmpwalk
        if pon: # pon específica
            if tipo == 'onu':
                sinais_snmp = session.walk(f'1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4.{pon}') # oid que retorna Potência RX das ONUs
            elif tipo == 'olt':
                sinais_snmp = session.walk(f'.1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6.{pon}') # oid que retorna Potência TX das ONUs
            else:
                print(f'Para consutar a potência, escolha apenas "onu" ou "olt". Você escolheu: {tipo}')
        else: # olt inteira
            if tipo == 'onu':
                sinais_snmp = session.walk('1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4') # oid que retorna Potência RX das ONUs
            elif tipo == 'olt':
                sinais_snmp = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6') # oid que retorna Potência TX das ONUs
            else:
                print(f'Para consutar a potência, escolha apenas "onu" ou "olt". Você escolheu: {tipo}')
    except: # timeout
        print("Não foi possível realizar o snmp walk das potências. Aguarde alguns instantes e tente novamente. Saindo...")
        sys.exit()
    sinais = []
    for sinal in sinais_snmp:
        temp = f'{int(sinal.value) / 100:.2f}' 
        sinais.append(str(temp))
    return sinais

def serial(olt, comnty, pon=None):
    """ Retorna o serial de cada onu na pon passada. """ # falta validar
    try: # Tentando criar a sessão snmp
        session = Session(hostname=olt, community=comnty, version=2)
    except: # algum parâmetro errado
        print(f"\nAlgum erro ao tentar criar uma sessão, antes mesmo de fazer o snmp walk!\nOLT: {olt}\nCommunity: {comnty}")
        sys.exit()
    try: # Tentando realizar o snmpwalk
        if pon: # pon específica
            seriais_snmp = session.walk(f'.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3.{pon}') # oid que retorna descrições
        else: # olt inteira
            seriais_snmp = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3') # oid que retorna descrições
    except: # timeout
        print("Não foi possível realizar o snmp walk dos seriais. Aguarde alguns instantes e tente novamente. Saindo...")
        sys.exit()
    seriais = []
    for serial in seriais_snmp:
        seriais.append(serial.value) # extrai o valor da descrição
    return seriais                 # retorna uma lista com as descrições

def temp_placas(olt, comnty, pon):
    """ Retorna a temperatura de cada placa da olt. """
    session = Session(hostname=olt, community=comnty, version=2)
    descs = session.walk('1.3.6.1.4.1.2011.2.6.7.1.1.2.1.10 (hwMusaBoardTemperature)')
    descs_value = []
    for desc in descs:
        descs_value.append(desc.value) # extrai o valor da descrição
    return descs_value                 # retorna uma lista com as descrições

def uptime_olt(olt, comnty):
    """
    Uptime da OLT em ticks. Conversões:
    segundos = ticks / 100
    minutos = ticks / 6,000
    horas = ticks / 360,000
    dias = ticks / 8,640,000
    Por padrão, retorno em dias.
    """
    session = Session(hostname=olt, community=comnty, version=2)
    uptime_ticks = session.walk('1.3.6.1.2.1.1.3') # Uptime da OLT em ticks

    return int(int(uptime_ticks[0].value) / 60 / 60 /24 / 100) # Dias
    # printa aproximadamente os dias, não é exato.
    #return f'Uptime da olt \'{olt}\' é de aproximadamente {uptime / 100:.0f} dias.'
