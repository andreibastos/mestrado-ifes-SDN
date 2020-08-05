# Redes Definidas por Software
Automatização de teste de rede utilizando Ryu e Mininet

## Configuração 
- Instalar o virtual env
```
sudo apt-get install python-virtualenv
```
- criar o ambiente virtual
```
virtualenv -p python2.7 venv
```
- ativar o ambiente virtual
```
source venv/bin/activate
```
- instalar as dependências
```
pip install -r requeriments.txt
```

## Executando
considerando [mininet](http://mininet.org/) instalado


```
sudo python main.py -t bcube -k 1 -n 4
or
sudo python main.py -t fattree -k 4 
```
