#!/usr/bin/env python3
# coding=utf-8

##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#      ver: 1.1 27/5/20      #
##############################

import sys
from easysnmp import Session

def ont_status(olt, comnty):
    """retorna o status de todas ONUs,
    1 = online,  2 = offline"""
    session = Session(hostname=olt, community=comnty, version=2)
    status_snmp = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15') # oid que retorna ONT status (online = 1, offline = 2)
    status_all = []
    for status in status_snmp:
        val = status.value # extrai o valor da descrição
        if val == '1':
            status_all.append('online') # extrai o valor da descrição
        elif val == '2':
            status_all.append('offline')
        else:
            status_all.append(f'status desconhecido: {val}')
    return status_all

def descricao(olt, comnty):
    session = Session(hostname=olt, community=comnty, version=2)
    descs = session.walk('.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.9') # oid que retorna descrições
    descs_value = []
    for desc in descs:
        descs_value.append(desc.value) # extrai o valor da descrição
    return descs_value                 # retorna uma lista com as descrições

def ont_last_downtime(olt, comnty):
    """ """
    session = Session(hostname=olt, community=comnty, version=2, use_sprint_value=False)
    last_downtime = session.bulkwalk('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.23') # oid que retorna o Downtime (em hexadecimal)
    downtime_all = []
    for data in last_downtime:
        data_hex = bin_pra_hex(data.value)
        downtime_all.append(data_hex) # extrai o valor da descrição
    return downtime_all

def bin_pra_hex(hex_codes_entrada):
  octets = [ord(c) for c in hex_codes_entrada]
  return "{:02X}{:02X} {:02X} {:02X} {:02X} {:02X} {:02X}".format(*octets)

def main():
    if len(sys.argv) < 2:
        print("Por favor, especifique uma OLT:\nBela_Roma\nVolta_Redonda\nBarra_Mansa\nPorto_Real\nQuatis\nItatiaia\nPenedo")
        sys.exit()
    OLT = sys.argv[1]
    addresses = {
        'Bela_Roma': '10.80.80.2',
        'Volta_Redonda': '10.80.80.6',
        'Barra_Mansa': '10.80.80.10',
        'Porto_Real': '10.80.80.14',
        'Quatis': '10.80.80.18',
        'Itatiaia': '10.80.80.22',
        'Penedo': '10.80.80.26'
    }

    print("consultando desc")
    try:
        desc_all = descricao(addresses[OLT], 'qn31415926')
    except:
        print("Não foi possível realizar a consulta snmp. Aguarde um momento e tente novamente!")

    print("consultando status")
    try:
        status_all = ont_status(addresses[OLT], 'qn31415926')
    except:
        print("Não foi possível realizar a consulta snmp. Aguarde um momento e tente novamente!")

    print("consultando downtime")
    try:
        last_downtime_all = ont_last_downtime(addresses[OLT], 'qn31415926')
    except:
        print("Não foi possível realizar a consulta snmp. Aguarde um momento e tente novamente!")

    last_downtime_formatado = []
    for onu in last_downtime_all:
        onu_lst_dt = onu.split()
        ano, mes, dia, hora, minuto, segundo = onu_lst_dt[0], onu_lst_dt[1], onu_lst_dt[2], onu_lst_dt[3], onu_lst_dt[4], onu_lst_dt[5]
        last_downtime_formatado.append(f'{int(dia, 16)}-{int(mes, 16)}-{int(ano, 16)} {int(hora, 16)}:{int(minuto, 16)}:{int(segundo, 16)}')

    for onu_desc, onu_status, onu_last_downtime in zip(desc_all, status_all, last_downtime_formatado):
        if len(onu_desc) > 5:
            onu_desc = onu_desc[:5]
        print(f'Cliente {onu_desc}\testá {onu_status}\túltima queda: {onu_last_downtime}')


if __name__ == '__main__':
    main()
