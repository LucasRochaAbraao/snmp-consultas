#!/usr/bin/env python3
# coding=utf-8

##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#      ver: 1.0  31/03/2021  #
##############################

import sys
import asyncio
from snmp import py_snmp


# TODO:
#

async def main():
    addresses = {
        'Bela_Roma': ['10.80.80.2', 'huawei'],
        'Volta_Redonda': ['10.80.80.6', 'huawei'],
        'Barra_Mansa': ['10.80.80.10', 'huawei'],
        'Porto_Real': ['10.80.80.14', 'huawei'],
        'Quatis': ['10.80.80.18', 'huawei'],
        'Itatiaia': ['10.80.80.22', 'huawei'],
        'Penedo': ['10.80.80.26', 'huawei'],
        'Jardim_Mar': ['10.80.80.38', 'datacom'],
        'Pirai_A': ['10.80.80.30', 'datacom'],
        'Pirai_B': ['10.80.80.34', 'datacom'],
        'Serrinha': ['10.80.80.42', 'datacom'],
        'Eng_Passos': ['10.80.80.46', 'datacom']
    }

    if len(sys.argv) < 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print("Consulte: ./sinal_consulta.py OLT desc")
            sys.exit()
        print("Por favor, escolha uma OLT sa lista abaixo, e em seguida coloque o código da conexão do cliente!:\n\n\t- Bela_Roma\n\t- Volta_Redonda\n\t- Barra_Mansa\n\t- Porto_Real\n\t- Quatis\n\t- Itatiaia\n\t- Penedo\n\t")
    else:
        if sys.argv[1] not in addresses.keys():
            print("Não é uma das opções!")
            print("Por favor, escolha uma OLT:\n\n\t- Bela_Roma\n\t- Volta_Redonda\n\t- Barra_Mansa\n\t- Porto_Real\n\t- Quatis\n\t- Itatiaia\n\t- Penedo\n\t")
            sys.exit()

    OLT = sys.argv[1]
    DESC = sys.argv[2]
    # 12978-QCK-DBA-107

    print("Um instante! Estamos verificando...")
    descs = await py_snmp.descricao(addresses[OLT][0], 'qn31415926', fabricante=addresses[OLT][1])
    sinais_rx = await py_snmp.potencia(addresses[OLT][0], 'qn31415926', tipo='rx', fabricante=addresses[OLT][1])
    #sinais_tx = await py_snmp.potencia(addresses[OLT], 'qn31415926', tipo="tx") # Encontrar o oid correto!
    
    if len(descs) != len(sinais_rx):
        print(f"Cuidado! Informação inconsistente a seguir. Quantidade de ONUs online é diferente da quantidade de ONUs com descrição!\n### {len(sinais_rx)} online vs {len(descs)} com descrição ###")

    achou = None
    for desc, sinal_rx in zip(descs, sinais_rx):
        if sinal_rx == "0.00":
            sinal_rx = "onu offline"
        if DESC in desc:
            achou = 'sim'
            if sinal_rx == "onu offline":
                print("ONU está offline!")
            else:
                print(f"Cliente: {desc} | Sinal: {sinal_rx} dBm")
    if not achou:
        print(f"Verifique a descrição do cliente, pois não consegui encontrar na OLT selecionada!")

if __name__ == '__main__':
    asyncio.run(main())
