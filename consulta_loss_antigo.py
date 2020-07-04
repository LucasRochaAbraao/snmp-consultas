#!/usr/bin/env python3
# coding=utf-8

##############################
#     LUCAS ROCHA ABRAÃO     #
#   lucasrabraao@gmail.com   #
#  github: LucasRochaAbraao  #
#      ver: 1.2  28/05/2020  #
##############################

import sys
from snmp import snmp

def main(): 
    #OLT a ser consultada
    OLT = sys.argv[1]
    # sendo testada atualmente. Vou mudar pra conf.ini
    PON = 4194313728 # 0/1/6
    #PON = 4194337792 # 0/4/4
    #PON = 4194344960 #0/5/0
    #PON = 4194347008 #0/5/8
    #PON = 4194304000 #0/0/0
    #PON = 4194361344 #0/7/0
    #PON = 4194337536 # 0/4/3
    #PON = 4194338048 # 0/4/5

    if len(sys.argv) > 2:
        PON = sys.argv[2]

    addresses = {
        'Bela_Roma': '10.80.80.2',
        'Volta_Redonda': '10.80.80.6',
        'Barra_Mansa': '10.80.80.10',
        'Porto_Real': '10.80.80.14',
        'Quatis': '10.80.80.18',
        'Itatiaia': '10.80.80.22',
        'Penedo': '10.80.80.26'
    }

    ### LAST DOWN TIME ###
    last_downtime = snmp.last_downtime(addresses[OLT], 'qn31415926', PON)

    ### LAST DOWN CAUSE ###
    down_cause = snmp.last_down_cause(addresses[OLT], 'qn31415926', PON)

    ### DESCRIÇÃO ###
    desc_all = snmp.descricao(addresses[OLT], 'qn31415926', PON)
    
    ### STATUS ###
    status_all = snmp.status(addresses[OLT], 'qn31415926', PON)

    # Printa as informações formatadas e pega os
    # clientes cujo last down cause foi 'los'
    clientes_com_los = {}
    print('\t--- PON 0/7/0 ---')
    print('DESC\tSTATUS\tDOWN_CAUSE\tHORÁRIO')
    for desc, status, down_c, last_dt in zip(desc_all, status_all, down_cause, last_downtime):
        if down_c == 'los' or down_c == 'sem_info':
            clientes_com_los[desc] = [down_c, last_dt]
        print(f'{desc}\t{status}\t{down_c}\t{last_dt}')
    print(f'Total: {len(desc_all)}')

    # printa os clientes capturados no loop anterior.
    # Isso é apenas pra facilitar algum diagnóstico
    print('\n\t--- APENAS OFFLINE ---')
    print('DESC\tDOWN_CAUSE\tHORÁRIO')
    for ind, (desc, status, down_c, horario) in enumerate(zip(desc_all, status_all, down_cause, last_downtime)):
        if status == 'offline':
            print(f'{desc}\t{down_c}\t{horario}')
    print(f"Total offline: {status_all.count('offline')}")


if __name__ == '__main__':
    main()
