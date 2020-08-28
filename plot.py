#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Realizar gráficos
"""

"""Output of bwm-ng csv has the following columns:
unix_timestamp;iface_name;bytes_out;bytes_in;bytes_total;packets_out;packets_in;packets_total;errors_out;errors_in
"""

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
import numpy as np
import argparse

## argumentos
parser = argparse.ArgumentParser()
parser.add_argument(
    '--file', '-f', help="arquivo de leitura (csv)",
    required=True, dest="file")

parser.add_argument(
    '--output', '-o', help="arquivo de saída (png)",
    required=True, dest="output")

parser.add_argument(
    '--rx', help="indica se vai plotar os bytes de saida ou de entrada",
    dest="rx", default=False)

# realiza o parser dos argumentos
args = parser.parse_args()

# leitura do arquivo csv
with open(args.file) as f:
    lines = f.readlines()  # ler as linhas
    data = dict()  # dados será um dicionário de interface
    for line in lines:
        columns = line.split(',')  # separa as colunas por virgula
        if len(columns) < 3: # se não tiver colunas suficiente, pula
            continue

        unixtimestamp = int(columns[0])  # obtém o tempo em unixtimestamp
        time = datetime.utcfromtimestamp(unixtimestamp)  # converte para time

        iface = columns[1]  # obtém o nome da interface de rede
        bytes_out = columns[2]  # bytes de saída
        bytes_in = columns[3]  # bytes de entrada

        # cada interface tem um dict de x = [] e y = []
        data.setdefault(iface, dict())
        data[iface].setdefault('x', [])
        data[iface].setdefault('y', [])

        # adiciona o tempo na lista de x
        data[iface]['x'].append(unixtimestamp)

        # verifica se quer plotar bytes de entrada ou de saida
        y = bytes_in if args.rx else bytes_out

        # converte para Mb
        # está em bits/s, deve converter para MBytes/s
        y = float(y) * 8.0 / (1 << 20)
        data[iface]['y'].append(y)  # adiciona na lista de y

# prepara o gráfico de 1 linha e 1 coluna
fig, axes = plt.subplots(ncols=1, nrows=1)
axes.set_xlabel("Tempo (segundos)")  # eixo x
ylabel = "Saída (Mbps)" if args.rx else 'Entrada (Mbps)'
axes.set_ylabel(ylabel)  # eixo y

# título
axes.set_title("Taxa de Entrada")
if args.rx:
    plt.title("Taxa de Saída")

ymax = 0  # máximo valor de y, global (todas interfaces)
for iface_name in data.keys():  # para cada interface
    iface = data[iface_name]
    x = iface['x']  # obtem o array do eixo x (vetor de tempo)
    y = iface['y']  # obtem o array do eixo y

    # verifica a duração 
    duration = x[-1] - x[0] +1  # duração (última  - primeira + 1 segundo)
    period = duration*1.0/len(x)
    if (duration*period > len(y) ):
        duration -= 1
        period = duration*1.0/len(x)

    # preenche um vetor de tempo de 0 até duration indo pedaço a pedaço
    t = np.arange(0, duration,  period)

    ymax = max(max(y), ymax)  # atualiza o ymax
    axes.plot(t, y, label=iface_name)  # plota o gráfico

fig.autofmt_xdate()  # formata o eixo de tempo para ficar espaçado
plt.grid()  # adiciona a grade
plt.legend()  # adiciona a legenda
plt.ylim((0, ymax*1.2))  # ajusta o eixo y para ficar 20% a mais que o maior y

# aguarda a figura
if args.output:
    plt.savefig(args.output)
