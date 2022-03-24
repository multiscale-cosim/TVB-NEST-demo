import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI


def input(path, nb_neurons, t_synch):
    """
    Simulate some random spike train input
    :param path: the file for the configurations of the connection
    :return:
    """
    # Start communication channels
    path_to_files = path
    # For NEST
    # Init connection
    print("INPUT : Waiting for port details")
    info = MPI.INFO_NULL
    root = 0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    print('INPUT : wait connection ' + port); sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('INPUT : connect to ' + port)

    # test one rate
    status_ = MPI.Status()
    check = np.empty(1, dtype='b')
    starting = 1
    while True:
        for i in range(1, nb_neurons+1):
            comm.Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
            print("INPUT :  start to send"); sys.stdout.flush()
            print("INPUT :  status a tag ", status_.Get_tag()); sys.stdout.flush()
            tag = status_.Get_tag()
            if status_.Get_tag() != 0:
                source = status_.Get_source()
                print("Input : source is", source); sys.stdout.flush()
                # receive list ids
                shape = int(np.random.rand(1)*10)
                data = starting + np.random.rand(shape) * 20
                data = np.around(np.sort(np.array(data, dtype='d')), decimals=1)
                send_shape = np.array(shape, dtype='i')
                comm.Send([send_shape, MPI.INT], dest=source, tag=tag)
                print("INPUT :  shape data ", shape); sys.stdout.flush()
                comm.Send([data, MPI.DOUBLE], dest=source, tag=tag)
                print("INPUT :  send data", data); sys.stdout.flush()
            else:
                print("INPUT :  TAG end :",status_.Get_tag())
                break
        print("INPUT :  TAG end :", status_.Get_tag())
        if status_.Get_tag() != 0:
            starting += t_synch
        else:
            break
    comm.Barrier()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('INPUT : exit')
    MPI.Finalize()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 4:
        input(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
    else:
        print('missing argument')
