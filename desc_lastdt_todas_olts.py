#!/usr/bin/env python3
# coding=utf-8

##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#      ver: 1.2 27/5/20      #
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

def ont_last_downtime(olt, comnty):
    """ """
    session = Session(hostname=olt, community=comnty, version=2, use_sprint_value=False)
    last_downtime = session.bulkwalk('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.22') # oid que retorna o Downtime (em hexadecimal)
    downtime_all = []
    for data in last_downtime:
        data_hex = bin_pra_hex(data.value)
        onu_lst_dt = data_hex.split()
        ano, mes, dia, hora, minuto, segundo = onu_lst_dt[0], onu_lst_dt[1], onu_lst_dt[2], onu_lst_dt[3], onu_lst_dt[4], onu_lst_dt[5]
        downtime_all.append(f'{int(dia, 16)}-{int(mes, 16)}-{int(ano, 16)} {int(hora, 16)}:{int(minuto, 16)}:{int(segundo, 16)}')
        #downtime_all.append(data_hex) # extrai o valor da descrição
    return downtime_all
    
def bin_pra_hex(hex_codes_entrada):
  octets = (ord(c) for c in hex_codes_entrada)
  return "{:02X}{:02X} {:02X} {:02X} {:02X} {:02X} {:02X}".format(*octets)

def main():
    addresses = {
        'Bela_Roma': '10.80.80.2',
        'Volta_Redonda': '10.80.80.6',
        'Barra_Mansa': '10.80.80.10',
        'Porto_Real': '10.80.80.14',
        'Quatis': '10.80.80.18',
        'Itatiaia': '10.80.80.22',
        'Penedo': '10.80.80.26'
    }

    acumulado_status = []
    acumulado_downtime = []
    
    for olt in addresses:
        print(f"Consultando a olt {olt}")
        for 
        print(f"Consultando status")
        status_all = ont_status(addresses[olt], 'qn31415926')
        print("Consultando last downtime")
        last_downtime_all = ont_last_downtime(addresses[olt], 'qn31415926')
        print("\n")


#        last_downtime_formatado = []
#        for onu_status, onu_last_downtime in zip(status_all, last_downtime_all):
#            onu_dt_lst = onu_last_downtime.split()
#            ano, mes, dia, hora, minuto, segundo = onu_dt_lst[0], onu_dt_lst[1], onu_dt_lst[2], onu_dt_lst[3], onu_dt_lst[4], onu_dt_lst[5]
#            print(f'{int(dia, 16)}-{int(mes, 16)}-{int(ano, 16)} {int(hora, 16)}:{int(minuto, 16)}:{int(segundo, 16)}')
        for onu_status, onu_last_downtime in zip(status_all, last_downtime_formatado):
            print(f'Status da onu: {onu_status}\tLast Downtime: {onu_last_downtime}\n')


if __name__ == '__main__':
    main()
