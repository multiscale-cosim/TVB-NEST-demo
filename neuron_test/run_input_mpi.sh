cd detector/; nrnivmodl ;cd .. ;
rm /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/input_port.txt
mpirun -n 1 python3 input_neurons.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/input_port.txt &
wait 2
#mpirun -n 1 valgrind python3 neuron_simple_network.py
mpirun -n 1 python3 neuron_simple_network.py
