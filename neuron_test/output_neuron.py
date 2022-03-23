import numpy as np
import os
from mpi4py import MPI


def output(path, nb_neurons):
    """
    Simulate some random spike train input
    :param path: the file for the configurations of the connection
    :return:
    """
    # Start communication channels
    path_to_files = path
    # For NEST
    # Init connection
    print("OUTPUT : Waiting for port details")
    info = MPI.INFO_NULL
    root = 0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    print('OUTPUT : wait connection ' + port); sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('OUTPUT : connect to ' + port)

    # test one rate
    status_ = MPI.Status()
    check = np.empty(1, dtype='b')
    result = [[] for i in range(nb_neurons)]
    time = 0
    while True:
        for i in range(1, nb_neurons+1):
            comm.Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
            print("OUTPUT :  start to send time", time); sys.stdout.flush()
            print("OUTPUT :  status a tag ", status_.Get_tag()); sys.stdout.flush()
            tag = status_.Get_tag()
            if status_.Get_tag() != 0:
                comm.Send([np.array(True, dtype='b'), MPI.BOOL], dest=status_.Get_source(), tag=tag)
                shape = np.empty(1, dtype='i')
                comm.Recv([shape, 1, MPI.INT], source=status_.Get_source(), tag=tag, status=status_)
                print("OUTPUT :shape is", shape);sys.stdout.flush()
                data = np.empty(shape[0], dtype='d')
                comm.Recv([data, shape[0], MPI.DOUBLE], source=status_.Get_source(), tag=tag, status=status_)
                print("OUTPUT :data is ", data); sys.stdout.flush()
                result[i-1].append(data)
            else:
                print("OUTPUT :  TAG end :", status_.Get_tag())
                break
        time += 1
        print("OUTPUT :  TAG end :", status_.Get_tag())
        if status_.Get_tag() == 0:
            break
    comm.Barrier()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('OUTPUT : exit')
    MPI.Finalize()
    for data in result:
        print('OUTPUT :', np.concatenate(data))


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        output(sys.argv[1], int(sys.argv[2]))
    else:
        print('missing argument')
