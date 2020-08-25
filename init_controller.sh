# script inicialização do controlador
sudo pkill -f controller.py # elimina algum controlador anterior
source venv/bin/activate # ambiente virtual do python

method=${2:-'OSPF'} # pega o segundo argumento ou por padrão method='OSPF'
METHOD=$method venv/bin/ryu-manager controller.py # inicia controlador com a variavel de ambiente