# script inicialização do controlador
sudo pkill -f controller.py # elimina algum controlador anterior
source venv/bin/activate # ambiente virtual
venv/bin/ryu-manager controller.py # inicia controlador