## Andrei Bastos
## Mestrado IFES 2020 - Computação Aplicada - Redes de Computadores - SDN

# Testes completo

# variaveis
DIR_RESULTS=results

mkdir $DIR_RESULTS -p
# # fattre
# # OSPF
# sudo python main.py -t fattree -k 4 --method OSPF
# sed -i 's/total/Fattree - OSPF/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/fattree_OSPF.bwm

# # # ECMP
# sudo python main.py -t fattree -k 4 --method ECMP
# sed -i 's/total/Fattree - ECMP/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/fattree_ECMP.bwm

# cat $DIR_RESULTS/fattree_OSPF.bwm >$DIR_RESULTS/fattree.bwm
# cat $DIR_RESULTS/fattree_ECMP.bwm >>$DIR_RESULTS/fattree.bwm

# python plot_traffic.py -f $DIR_RESULTS/fattree.bwm -o $DIR_RESULTS/fattree.png

# # genérica 1
# python topologies/generate_generic.py -o topologies/topo1.txt --switches 16 --links 32

# # OSPF
# sudo python main.py -t generic -f topologies/topo1.txt --method OSPF
# sed -i 's/total/Topologia Generica 1 - OSPF/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/topo1_OSPF.bwm
# # ECMP
# sudo python main.py -t generic -f topologies/topo1.txt --method ECMP
# sed -i 's/total/Topologia Generica 1 - ECMP/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/topo1_ECMP.bwm

# # genérica 2
# python topologies/generate_generic.py -o topologies/topo2.txt --switches 16 --links 32

# # OSPF
# sudo python main.py -t generic -f topologies/topo2.txt --method OSPF
# sed -i 's/total/Topologia Generica 2 - OSPF/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/topo2_OSPF.bwm
# # ECMP
# sudo python main.py -t generic -f topologies/topo2.txt --method ECMP
# sed -i 's/total/Topologia Generica 2 - ECMP/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/topo2_ECMP.bwm

# # genérica 3
# python topologies/generate_generic.py -o topologies/topo3.txt --switches 16 --links 32

# # # OSPF
# sudo python main.py -t generic -f topologies/topo3.txt --method OSPF
# sed -i 's/total/Topologia Generica 3 - OSPF/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/topo3_OSPF.bwm
# # ECMP
# sudo python main.py -t generic -f topologies/topo3.txt --method ECMP
# sed -i 's/total/Topologia Generica 3 - ECMP/g' dados.bwm
# cp dados.bwm $DIR_RESULTS/topo3_ECMP.bwm

# junta todos resultados em um arquivo unico
cat $DIR_RESULTS/topo1_OSPF.bwm >$DIR_RESULTS/topo.bwm
cat $DIR_RESULTS/topo1_ECMP.bwm >>$DIR_RESULTS/topo.bwm
cat $DIR_RESULTS/topo2_OSPF.bwm >>$DIR_RESULTS/topo.bwm
cat $DIR_RESULTS/topo2_ECMP.bwm >>$DIR_RESULTS/topo.bwm
cat $DIR_RESULTS/topo3_OSPF.bwm >>$DIR_RESULTS/topo.bwm
cat $DIR_RESULTS/topo3_ECMP.bwm >>$DIR_RESULTS/topo.bwm
python plot_traffic.py -f $DIR_RESULTS/topo.bwm -o $DIR_RESULTS/topo.png

# ## bcube
# # OSPF
# sudo python main.py -t bcube -k 1 -n 4 --method OSPF
# # ECMP
# sudo python main.py -t bcube -k 1 -n 4 --method ECMP
