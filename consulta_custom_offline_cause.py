#!/usr/bin/env python3
# coding=utf-8

##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#     ver: 1.0  29/03/2021   #
##############################

import sys
import asyncio
import pathlib
import configparser
from snmp import py_snmp

def get_config(file_name, item):
    config = configparser.ConfigParser()
    config.read(str(pathlib.Path(__file__).parent.absolute()) + f'/{file_name}.ini')
    return config[f'{item}']

def get_oid_pon(placa, pon):
    placa_gpon_parser = get_config('snmp/placas_gpon_huawei', f'PLACA_{placa}')
    pon_oid = placa_gpon_parser[f'PON_{pon}']
    return pon_oid

async def resultado(olt_ip, pon):
    last_downtime = await py_snmp.last_downtime(olt_ip, 'qn31415926', pon)
    down_cause = await py_snmp.last_down_cause(olt_ip, 'qn31415926', pon)
    desc_all = await py_snmp.descricao(olt_ip, 'qn31415926', pon)
    status_all = await py_snmp.status(olt_ip, 'qn31415926', pon)
    
    print(f'Total de ONUs na PON: {len(status_all)}\n')
    print('DESC\tDOWN_CAUSE\tHORÁRIO')
    for desc, status, down_c, horario in zip(desc_all, status_all, down_cause, last_downtime):
        if status == 'offline':
            print(f'{desc} - {down_c} - {horario}')
    #print(f"Total de ONUs na PON: {len(status_all)}")
    #print(f"Total de offline[los]: {status_all.count('offline')}[{down_cause.count('___LOS___')}]")

async def main():
    # ./consulta.py Olt 0/3/1
    addresses = {
        'Bela_Roma': '10.80.80.2',
        'Volta_Redonda': '10.80.80.6',
        'Barra_Mansa': '10.80.80.10',
        'Porto_Real': '10.80.80.14',
        'Quatis': '10.80.80.18',
        'Itatiaia': '10.80.80.22',
        'Penedo': '10.80.80.26'
    }
    if sys.argv[1] not in addresses.keys():
        print("Não é uma das opções!")
        print("Por favor, escolha uma OLT:\n\n\t- Bela_Roma\n\t- Volta_Redonda\n\t- Barra_Mansa\n\t- Porto_Real\n\t- Quatis\n\t- Itatiaia\n\t- Penedo\n\t")
        exit()

    OLT = sys.argv[1]
    placa_pon = sys.argv[2].split('/')
    PLACA = placa_pon[1]
    PON = placa_pon[2]

    oid = get_oid_pon(PLACA, PON)
    await resultado(addresses[OLT], oid)

if __name__ == '__main__':
    asyncio.run(main())
