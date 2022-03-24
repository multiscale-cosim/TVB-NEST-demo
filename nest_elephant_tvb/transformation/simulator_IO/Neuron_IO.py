#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import numpy as np
from nest_elephant_tvb.transformation.communication.mpi_io_external import MPICommunicationExtern


class ConsumerNeuronData(MPICommunicationExtern):
    """
    Class for the receiving data from Neuron and transfer them to the translation function process.
    """
    def __init__(self, nb_neurons, *arg, **karg):
        """
        Consume data/spikes trains from Neuron
        :param id_first_spike_detector: id of the first spike detector
        :param arg: other parameters
        :param karg: other parameters
        """
        super().__init__(*arg, **karg)
        self.nb_neurons = nb_neurons
        self.logger.info('Consumer Neuron : end init')

    def simulation_time(self):
        """
        Receive data from Neuron and add them in a shared buffer.
        """
        self.logger.info("Consumer Neuron : simulation time")
        status_ = MPI.Status()
        num_sending = self.port_comms[0].Get_remote_size()  # The total number of the rank in Neuron MPI_COMM_WORLD
        check = np.empty(1, dtype='b')  # variable to get the state of Neuron
        shape = np.empty(1, dtype='i')  # variable to receive the shape of the data
        count = 0  # count the number of run
        while True:
            self.logger.info("Consumer Neuron : loop start : wait all")
            for i in range(1, self.nb_neurons + 1):
                self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
                tag = status_.Get_tag()
                self.logger.info("Consumer Neuron : run for i = "+str(i)+" tag = "+str(tag))
                if status_.Get_tag() != 0:
                    if i == 1:
                        # INTERNAL :ready to write in the buffer
                        self.logger.info("Consumer Neuron : prepare buffer")
                        self.communication_internal.send_spikes_ready()
                        if self.communication_internal.send_spike_exit:
                            self.logger.info("Consumer Neuron : break")
                            break
                    self.logger.info("Consumer Neuron : start get data")
                    source = status_.Get_source()
                    # send 'ready' to the neuron rank
                    self.port_comms[0].Send([np.array(True, dtype='b'), MPI.BOOL], dest=source, tag=tag)
                    # receive package size info
                    self.port_comms[0].Recv([shape, 1, MPI.INT], source=source, tag=tag, status=status_)
                    self.logger.info("Consumer Neuron : shape : "+str(self.communication_internal.shape_buffer))
                    # Add data in the buffer
                    datas = np.empty(shape[0], dtype='d')
                    self.port_comms[0].Recv([datas, MPI.DOUBLE],
                                            source=source, tag=tag, status=status_)
                    data_reshape = []
                    for data in datas:
                        data_reshape.append(i-1)
                        data_reshape.append(i-1)
                        data_reshape.append(data)
                    self.communication_internal.databuffer[self.communication_internal.shape_buffer[0]:self.communication_internal.shape_buffer[0]+shape[0]*3] = data_reshape
                    self.communication_internal.shape_buffer[0] += shape[0]*3  # move head
                    self.logger.info("Consumer Neuron : end receive data")
                elif status_.Get_tag() == 0:
                    break
            self.logger.info("Consumer Neuron : receive end " + str(count))
            count += 1

            if status_.Get_tag() == 0 or self.communication_internal.send_spike_exit:
                self.logger.info("Consumer Neuron : end simulation")
                # INTERNAL : close the communication
                self.communication_internal.send_spikes_end()
                self.port_comms[0].Barrier()
                self.logger.info("Consumer Neuron : Barrier")
                break
            else:
                # INTERNAL : end to write in the buffer
                self.communication_internal.send_spikes()

        self.logger.info('Consumer Neuron : End of receive function')


class ProducerDataNeuron(MPICommunicationExtern):
    """
    Class for sending data to Neuron. The data are from the translated function.
    """

    def __init__(self, nb_neurons, *arg, **karg):
        """
        Produce data/spikes trains from Neuron
        :param id_first_spike_detector: id of the first spike detector
        :param arg: other parameters
        :param karg: other parameters
        """
        super().__init__(*arg, **karg)
        self.nb_neurons = nb_neurons
        self.logger.info('Produce Neuron : end init')

    def simulation_time(self):
        """
        Send data to Neuron from a shared buffer
        """
        self.logger.info('Produce Neuron : simulation')
        # initialisation variable before the loop
        status_ = MPI.Status()
        source_sending = np.arange(0, self.port_comms[0].Get_remote_size(), 1)  # list of all the rank of Neuron MPI_COMM_WORLD
        check = np.empty(1, dtype='b')  # variable to get the state of Neuron
        count = 0  # count the number of run
        spikes_times = None
        while True:
            for i in range(1, self.nb_neurons + 1):
                self.logger.info('Produce Neuron : loop start : wait all i '+str(i) +' nb_neuron '+str(self.nb_neurons))
                self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
                tag = status_.Get_tag()
                self.logger.info('Produce Neuron : run tag '+str(tag))
                if status_.Get_tag() != 0:
                    if i == 1:
                        # INTERNAL : get the data to send
                        # (here is spike trains but Neuron can receive other type of data.
                        # For the other type of data, the format to send it is different
                        self.logger.info("Produce Neuron : start to send ")
                        spikes_times = self.communication_internal.get_spikes()
                        self.logger.info("Produce Neuron : shape buffer " + str(self.communication_internal.shape_buffer[0]))
                        if self.communication_internal.shape_buffer[0] == -1:
                             break
                        self.logger.info("Produce Neuron : spike time")
                    source = status_.Get_source()
                    # improvement: We do not care which source sends first,
                    #   give MPI the freedom to send in whichever order.
                    # Select the good spike train and send it
                    data = spikes_times[i-1]
                    send_shape = np.array(len(spikes_times[i-1]), dtype='i')
                    # firstly send the size of the spikes train
                    self.port_comms[0].Send([send_shape, MPI.INT], dest=source, tag=tag)
                    # secondly send the spikes train
                    data = np.array(data).astype('d')
                    self.port_comms[0].Send([data, MPI.DOUBLE], dest=source, tag=tag)
                    self.logger.info("Produce Neuron : end sending")
                elif status_.Get_tag() == 0:
                    # ending the run of Neuron
                    self.logger.info("Produce Neuron : end run")
                    break
            if status_.Get_tag() == 0 or self.communication_internal.shape_buffer[0] == -1:
                self.logger.info("Produce Neuron : end simulation")
                # INTERNAL : close the communication
                self.communication_internal.get_spikes_end()
                self.port_comms[0].Barrier()
                self.logger.info("Produce Neuron : Barrier")
                break
            else:
                self.communication_internal.get_spikes_release()
                count += 1
                self.logger.info("Produce Neuron : receive end " + str(count))



