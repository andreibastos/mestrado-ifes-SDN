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
(considerando [ryu](https://ryu-sdn.org/) e [mininet](http://mininet.org/) instalados)
```
python main.py
```
