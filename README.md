# SNMP
Guardo aqui scripts que realizam consultas através de snmp, além de criar uma mini lib para consultas em OLTs Huawei.
Esse repositório também inclui uma licença open source pra copiar (desde que use a mesma licença no seu projeto).

Segue abaixo instruções de instalação, configuração e execução dos códigos.

## Instalação
Primeiro é necessário instalar, configurar e ativar um ambiente virtual, para um melhor gerenciamento do projeto.
```
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```
Agora, instale o pacote necessário para consultas snmp, *pysnmp*. Todos os scripts usam esse pacote. Para fazer o menu do script `menu_consulta.py` instale o pacote *PyInquirer*, e para gerar o banner instale o *PyFiglet*.
```
pip install pysnmp PyInquirer PyFiglet
```

## Configuração
##### menu_consultas.py

##### lista_consulta.py

##### total_online.py

## Execução


Distribuído sob a licença `GNU GENERAL PUBLIC LICENSE`. Veja `LICENSE` para mais informações.