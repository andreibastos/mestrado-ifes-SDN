# Redes Definidas por Software
Automatização de teste de rede utilizando Ryu e Mininet

## Configuração 
- Instalar o virtual env
```bash
sudo apt-get install python-virtualenv
```
- criar o ambiente virtual
```bash
virtualenv -p python2.7 venv
```
- ativar o ambiente virtual
```bash
source venv/bin/activate
```
- instalar as dependências
```bash
pip install -r requeriments.txt
```

todos os passos abaixo é considerando ambiente virtual ativo

## Gerando redes genéricas
```bash
python generate_generic.py -o topo3.txt --switches 6 --links 10 -v
``` 
```shell 
python generate_generic.py -h
# output
usage: generate_generic.py [-h] [-s S] [-l L] [-o OUTPUT] [-v]

optional arguments:
  -h, --help      show this help message and exit
  -s, --switches  número de switches (default: 4)
  -l --links      número links na rede (default: dobro de switches)
  -o, --output    Arquivo de saída
  -v, --view      visualizar a rede
``` 

## Iniciando Controlador
```bash
venv/bin/ryu-manager controller.py
```

## Executando Minenet
considerando [mininet](http://mininet.org/) instalado

```bash
# bcube
sudo python main.py -t bcube -k 1 -n 4
```
```bash
# fattre
sudo python main.py -t fattree -k 4 
```
```bash
# genérica
sudo python main.py -t generic -f topo1.txt 
```

## Executar Teste Completo
```bash
./full_test 
```
