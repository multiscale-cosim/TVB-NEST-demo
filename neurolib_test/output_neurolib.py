import numpy as np
import os
from mpi4py import MPI


def output(path):
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
    fport_lock = open(path_to_files+'.unlock', "w+")
    fport_lock.close()
    print('OUTPUT : wait connection ' + port); sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('OUTPUT : connect to ' + port); sys.stdout.flush()

    # test one rate
    status_ = MPI.Status()
    check = np.empty(1, dtype='b')
    result = []
    time = 0
    while True:
        print("OUTPUT Data : start loop : wait all"); sys.stdout.flush()
        # Send to all the confirmation of the Consumer is ready
        request = comm.isend(True, dest=0, tag=0)
        MPI.Request.Waitall([request])
        print("OUTPUT Data : receive all"); sys.stdout.flush()

        # get the starting and ending time of the simulation
        time_step = np.empty(2, dtype='d')
        comm.Recv([time_step, 2, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
        print("OUTPUT Data : get time_step "+str(time_step)+" status : " + str(status_.Get_tag())); sys.stdout.flush()

        if status_.Get_tag() == 0:
            # Get the rate
            size = np.empty(1, dtype='i')
            comm.Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
            rate = np.empty(size[0], dtype='d')
            comm.Recv([rate, size[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
            result.append(rate)
            time += 1

        elif status_.Get_tag() == 1:
            print("OUTPUT Data : end "); sys.stdout.flush()
            # INTERNAL : close communication with translation function
            break
        else:
            raise Exception("Abnormal tag: bad mpi tag"+str(status_.Get_tag()))
    print('OUTPUT Data : End of send function'); sys.stdout.flush()
    comm.Barrier()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('OUTPUT : exit'); sys.stdout.flush()
    MPI.Finalize()
    print('OUTPUT :', np.concatenate(result)); sys.stdout.flush()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        output(sys.argv[1])
    else:
        print('missing argument')
