#!/usr/bin/env python3
# coding=utf-8
##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#      ver: 1.0 13/3/20      #
##############################
 
import sys
from snmp import py_snmp

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

    if len(sys.argv) < 2:
        print("Por favor, escolha uma OLT:\n\n\t- Bela_Roma\n\t- Volta_Redonda\n\t- Barra_Mansa\n\t- Porto_Real\n\t- Quatis\n\t- Itatiaia\n\t- Penedo\n\t")
    elif len(sys.argv) > 2:
        print("Escolha apenas 1 OLT, por favor!")
    else:
        if sys.argv[1] not in addresses.keys():
            print("Não é uma das opções!")
            print("Por favor, escolha uma OLT:\n\n\t- Bela_Roma\n\t- Volta_Redonda\n\t- Barra_Mansa\n\t- Porto_Real\n\t- Quatis\n\t- Itatiaia\n\t- Penedo\n\t")
            sys.exit()

    OLT = sys.argv[1]

    status_all = py_snmp.status(addresses[OLT], 'qn31415926')

    online = []
    for onu in status_all:
        if onu == '1':
            online.append(onu)

    print(f'Total de ONUs cadastradas na OLT {OLT}: {len(status_all)}')
    print(f'Total de ONUs online na OLT {OLT}: {len(online)}')


if __name__ == '__main__':
    main()
