#export LD_LIBRARY_PATH=/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/:$LD_LIBRARY_PATH
#export PATH=/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/bin:$PATH
#export PYTHONPATH=/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python/:/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/lib/lib_py//lib/python3.8/site-packages/:$PYTHONPATH
#cd detector/; nrnivmodl ;cd .. ;
nb_neurons=10
t_synch='20.0'
rm /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/input_port.txt
rm /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/output_port.txt
mpirun -n 1 python3 output_neuron.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/output_port.txt $nb_neurons &
mpirun -n 1 python3 input_neurons.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/input_port.txt $nb_neurons $t_synch &
sleep 1
#mpirun -n 1 valgrind python3 neuron_simple_network.py
mpirun -n 1 python3 neuron_simple_network.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/input_port.txt  /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/output_port.txt $nb_neurons $t_synch
