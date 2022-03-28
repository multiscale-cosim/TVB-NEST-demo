import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI


def input(path, t_synch_nb, dt):
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
    fport_lock = open(path_to_files+'.unlock', "w+")
    fport_lock.close()
    print('INPUT : wait connection ' + port); sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('INPUT : connect to ' + port)

    # test one rate
    status_ = MPI.Status()
    check = np.empty(1, dtype='b')
    times = 0
    while True:
        print("INPUT Data : start loop : wait TVB"); sys.stdout.flush()
        # Consumer the state of TVB for knowing
        accept = False
        while not accept:
            req = comm.irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
            accept = req.wait(status_)
        print("INPUT Data : send data status : "+str(status_.Get_tag())); sys.stdout.flush()

        if status_.Get_tag() == 0:
            # INTERNAL : receive the data from translator function
            print("INPUT Data : get rate"); sys.stdout.flush()
            data = np.random.rand(t_synch_nb) * times/5000*100
            data = np.around(np.array(data, dtype='d'), decimals=1)
            send_shape = np.array(t_synch_nb, dtype='i')

            print("INPUT Data : send data :"+str(np.sum(data))); sys.stdout.flush()
            # time of stating and ending step
            comm.Send([np.array([times*dt*t_synch_nb,(times+1)*dt*t_synch_nb], dtype='d'), MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            # send the size of the rate
            comm.Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=0)
            # send the rates
            comm.Send([data, MPI.DOUBLE], dest=status_.Get_source(), tag=0)

            # INTERNAL : end sending data
            print("INPUT Data : end send"); sys.stdout.flush()
            times += 1

        elif status_.Get_tag() == 1:
            # INTERNAL : release the communication
            print("INPUT : end sim"); sys.stdout.flush()
            break

        else:
            raise Exception("Abnormal tag : bad mpi tag"+str(status_.Get_tag()))
    print('INPUT : End of send function'); sys.stdout.flush()
    comm.Barrier()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('INPUT : exit'); sys.stdout.flush()
    MPI.Finalize()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 4:
        input(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
    else:
        print('missing argument')
