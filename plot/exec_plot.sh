#! /bin/bash
python plot_rate.py --rx --maxy 10000 \
                    --xlabel 'Time (seconds)' --ylabel  'Rate (Mbps)' \
					-i 'total' -f '../dados.bwm' -o 'fileName.png'

