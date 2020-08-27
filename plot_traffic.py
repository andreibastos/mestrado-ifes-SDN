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
args = parser.parse_args()

# leitura do arquivo csv
with open(args.file) as f:
    lines = f.readlines()  # ler as linhas
    data = dict()  # dados será um dicionário de interface
    for line in lines:
        columns = line.split(',')  # separa as colunas por virgula

        unixtimestamp = int(columns[0])  # obtém o tempo em unixtimestamp
        time = datetime.utcfromtimestamp(unixtimestamp)  # converte para time
        iface = columns[1]  # obtém o nome da interface de rede
        bytes_out = columns[2]  # bytes de saída
        bytes_in = columns[3]  # bytes de entrada

        # cada interface tem um dict de x = [] e y = []
        data.setdefault(iface, dict())
        data[iface].setdefault('y', [])
        data[iface].setdefault('x', [])

        # adiciona o tempo na lista de x
        data[iface]['x'].append(time)

        # verifica se quer plotar bytes de saida ou de entrada
        y = bytes_out if not args.rx else bytes_in

        # converte para Mb
        y = float(y) * 8.0 / (1 << 20) # está em bits, deve converter para MBytes/s
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
    N = len(x)  # tamanho do vetor
    x = np.arange(N)  # preenche com o tamanho do vetor (para ficar casado)

    y = iface['y']  # lista dos valores de y
    ymax = max(max(y), ymax)  # atualiza o ymax
    axes.plot(x, y, label=iface_name)  # plota o gráfico


fig.autofmt_xdate()  # formata o eixo de tempo para ficar espaçado
plt.grid()  # adiciona a grade
plt.legend()  # adiciona a legenda
plt.ylim((0, ymax*1.2))  # ajusta o eixo y para ficar 20% a mais que o maior y

# aguarda a figura
if args.output:
    plt.savefig(args.output)
    plt.show()
else:
    plt.show()
