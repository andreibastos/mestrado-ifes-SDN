## Andrei Bastos
## Mestrado IFES 2020 - Computação Aplicada - Redes de Computadores - SDN

# Testes completo

# variaveis
DIR_RESULTS=results


mkdir $DIR_RESULTS -p
# fattre
# OSPF
# sudo python main.py -t fattree -k 4 --method OSPF
sed -i 's/total/fattree_OSPF/g' dados.bwm
cp dados.bwm $DIR_RESULTS/fattree_OSPF.bwm

# # ECMP
# sudo python main.py -t fattree -k 4 --method ECMP
sed -i 's/total/fattree_ECMP/g' dados.bwm
cp dados.bwm $DIR_RESULTS/fattree_ECMP.bwm

cat $DIR_RESULTS/fattree_OSPF.bwm > $DIR_RESULTS/fattree.bwm
cat $DIR_RESULTS/fattree_ECMP.bwm >> $DIR_RESULTS/fattree.bwm


python plot/plot_rate.py --rx --maxy 20000 \
    --xlabel 'Time (seconds)' --ylabel 'Rate (Mbps)' -f $DIR_RESULTS/fattree.bwm -o 'fattree.png'

# # genérica 1
# python topologies/generate_generic.py -o topologies/topo1.txt --switches 20 --links 32 -v
# # OSPF
# sudo python main.py -t generic -f topologies/topo1.txt --method OSPF
# # ECMP
# sudo python main.py -t generic -f topologies/topo1.txt --method ECMP

# # genérica 2
# python topologies/generate_generic.py -o topologies/topo2.txt --switches 20 --links 32 -v
# # OSPF
# sudo python main.py -t generic -f topologies/topo2.txt --method OSPF
# # ECMP
# sudo python main.py -t generic -f topologies/topo2.txt --method ECMP

# # genérica 3
# python topologies/generate_generic.py -o topologies/topo3.txt --switches 20 --links 32 -v
# # OSPF
# sudo python main.py -t generic -f topologies/topo3.txt --method OSPF
# # ECMP
# sudo python main.py -t generic -f topologies/topo3.txt --method ECMP

# ## bcube
# # OSPF
# sudo python main.py -t bcube -k 1 -n 4 --method OSPF
# # ECMP
# sudo python main.py -t bcube -k 1 -n 4 --method ECMP
