export LD_LIBRARY_PATH=/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/:$LD_LIBRARY_PATH
export PATH=/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/bin:$PATH
export PYTHONPATH=/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python3.8/site-packages/:/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python/:/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/lib/lib_py//lib/python3.8/site-packages/:$PYTHONPATH
cd ../neurolib/; pip install . --prefix=../lib/soft/; cd ../neurolib_test/
id_proxy=10
t_synch=10
dt="0.1"
rm /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neurolib_test/input_port.txt
rm /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neurolib_test/output_port.txt
mpirun -n 1 python3 output_neurolib.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neurolib_test/output_port.txt &
mpirun -n 1 python3 input_neurolib.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neurolib_test/input_port.txt $t_synch $dt &
sleep 2
#mpirun -n 1 valgrind python3 neuron_simple_network.py
mpirun -n 1 python3 example_simple_mpi.py /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neurolib_test/input_port.txt  /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neurolib_test/output_port.txt $id_proxy $t_synch
