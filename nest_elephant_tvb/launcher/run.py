#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import datetime
import os
import json
import subprocess
import copy
from nest_elephant_tvb.utils import create_folder, create_logger


def run(parameters):
    '''
    run the simulation
    :param parameters: parameters of the simulation
    :return:
    '''
    my_env = os.environ.copy()
    my_env["PATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/bin:' + my_env["PATH"]
    my_env["PYTHONPATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python/:/home/kusch/Documents/project/co_simulation/TVB-NEST-demo/venv/lib/python3.8/site-packages/:' + my_env["PYTHONPATH"]
    my_env["LD_LIBRARY_PATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/:' + my_env["LD_LIBRARY_PATH"]
    path = parameters['path']
    # start to create the repertory for the simulation
    create_folder(path)
    create_folder(path + "/log")
    create_folder(path + '/nest')
    create_folder(path + '/tvb')
    create_folder(path + '/transformation')
    create_folder(path + '/transformation/spike_detector/')
    create_folder(path + '/transformation/send_to_tvb/')
    create_folder(path + '/transformation/spike_generator/')
    create_folder(path + '/transformation/receive_from_tvb/')
    create_folder(path + '/figures')
    save_parameter(parameters)

    logger = create_logger(path, 'launcher', parameters['level_log'])

    logger.info('time: ' + str(datetime.datetime.now()) + ' BEGIN SIMULATION \n')

    # chose between running on cluster or local pc
    mpirun = ['mpirun']  # example : ['mpirun'] , ['srun','-N','1']

    processes = []  # process generate for the co-simulation
    processes.append(run_nest(my_env, mpirun, parameters['path'] + '/parameter.json', logger))

    # create transformer between Nest to TVB :
    processes.append(run_nest_to_tvb(my_env, mpirun, parameters['path'], logger))

    # create transformer between TVB to Nest:
    processes.append(run_tvb_to_nest(my_env, mpirun, parameters['path'], logger))

    # Run TVB in co-simulation
    processes.append(run_tvb(my_env, mpirun, parameters['path'] + '/parameter.json', logger))

    # FAT END POINT : add monitoring of the different process
    for process in processes:
        process.wait()
    logger.info('time: ' + str(datetime.datetime.now()) + ' END SIMULATION \n')


def run_neuron_tvb(parameters):
    """
    run the simulation
    :param parameters: parameters of the simulation
    :return:
    """
    my_env = os.environ.copy()
    my_env["PATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/bin::/home/kusch/Documents/project/co_simulation/TVB-NEST-demo/venv/bin/' + my_env["PATH"]
    my_env["PYTHONPATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python/:/home/kusch/Documents/project/co_simulation/TVB-NEST-demo/venv/lib/python3.8/site-packages/:' + my_env["PYTHONPATH"]
    my_env["LD_LIBRARY_PATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/:' + my_env["LD_LIBRARY_PATH"]
    path = parameters['path']
    # start to create the repertory for the simulation
    create_folder(path)
    create_folder(path + "/log")
    create_folder(path + '/neuron')
    create_folder(path + '/tvb')
    create_folder(path + '/transformation')
    create_folder(path + '/transformation/spike_detector/')
    create_folder(path + '/transformation/send_to_tvb/')
    create_folder(path + '/transformation/spike_generator/')
    create_folder(path + '/transformation/receive_from_tvb/')
    create_folder(path + '/figures')
    save_parameter(parameters)

    logger = create_logger(path, 'launcher', parameters['level_log'])

    logger.info('time: ' + str(datetime.datetime.now()) + ' BEGIN SIMULATION \n')

    # chose between running on cluster or local pc
    mpirun = ['mpirun']  # example : ['mpirun'] , ['srun','-N','1']


    processes = []  # process generate for the co-simulation
    processes.append(run_neuron(my_env, mpirun, parameters['path'] + '/parameter.json', logger))

    # create transformer between Nest to TVB :
    processes.append(run_neuron_to_tvb(my_env, mpirun, parameters['path'], logger))

    # create transformer between TVB to Nest:
    processes.append(run_tvb_to_neuron(my_env, mpirun, parameters['path'], logger))

    # Run TVB in co-simulation
    processes.append(run_tvb(my_env, mpirun, parameters['path'] + '/parameter.json', logger))

    # FAT END POINT : add monitoring of the different process
    for process in processes:
        process.wait()
    logger.info('time: ' + str(datetime.datetime.now()) + ' END SIMULATION \n')

def run_nest_neurolib(parameters):
    """
    run the simulation
    :param parameters: parameters of the simulation
    :return:
    """
    my_env = os.environ.copy()
    my_env["PATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/bin::/home/kusch/Documents/project/co_simulation/TVB-NEST-demo/venv/bin/' + my_env["PATH"]
    my_env["PYTHONPATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python3.8/site-packages/:/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python/:/home/kusch/Documents/project/co_simulation/TVB-NEST-demo/venv/lib/python3.8/site-packages/:' + my_env["PYTHONPATH"]
    my_env["LD_LIBRARY_PATH"] = '/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/:' + my_env["LD_LIBRARY_PATH"]
    path = parameters['path']
    # start to create the repertory for the simulation
    create_folder(path)
    create_folder(path + "/log")
    create_folder(path + '/nest')
    create_folder(path + '/neurolib')
    create_folder(path + '/transformation')
    create_folder(path + '/transformation/spike_detector/')
    create_folder(path + '/transformation/send_to_neurolib/')
    create_folder(path + '/transformation/spike_generator/')
    create_folder(path + '/transformation/receive_from_neurolib/')
    create_folder(path + '/figures')
    save_parameter(parameters)

    logger = create_logger(path, 'launcher', parameters['level_log'])

    logger.info('time: ' + str(datetime.datetime.now()) + ' BEGIN SIMULATION \n')

    # chose between running on cluster or local pc
    mpirun = ['mpirun']  # example : ['mpirun'] , ['srun','-N','1']


    processes = []  # process generate for the co-simulation
    processes.append(run_nest(my_env, mpirun, parameters['path'] + '/parameter.json', logger))

    # create transformer between Nest to TVB :
    processes.append(run_nest_to_neurolib(my_env, mpirun, parameters['path'], logger))

    # create transformer between TVB to Nest:
    processes.append(run_neurolib_to_nest(my_env, mpirun, parameters['path'], logger))

    # Run TVB in co-simulation
    processes.append(run_neurolib(my_env, mpirun, parameters['path'] + '/parameter.json', logger))

    # FAT END POINT : add monitoring of the different process
    for process in processes:
        process.wait()
    logger.info('time: ' + str(datetime.datetime.now()) + ' END SIMULATION \n')

def run_nest(my_env, mpirun, path_parameter, logger):
    """
    launch NEST
    :param mpirun: multiprocessor launcher
    :param path_parameter: path of the parameter file
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../nest/Balanced_network_reduce_co-sim.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '2', 'python3', dir_path]
    argv += [path_parameter]
    logger.info("NEST start :" + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )


def run_tvb(my_env, mpirun, path_parameter, logger):
    """
    launch TVB
    :param mpirun: multiprocessor launcher
    :param path_parameter: path of the parameter file
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../tvb/TVB_simple_example_co_sim.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '1', 'python3', dir_path]
    argv += [path_parameter]
    logger.info("TVB start :" + str(argv))
    print("TVB start :", argv)
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )


def run_nest_to_tvb(my_env, mpirun, path, logger):
    """
    launch Transformer NEST to TVB
    :param mpirun: multiprocessor launcher
    :param path: path of the simulation folder
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../transformation/nest_to_tvb.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '1', 'python3', dir_path]
    argv += [path]
    logger.info("Transformer NEST to TVB start : " + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )


def run_tvb_to_nest(my_env, mpirun, path, logger):
    """
    launch Transformer TVB to NEST
    :param mpirun: multiprocessor launcher
    :param path: path of the simulation folder
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../transformation/tvb_to_nest.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '1', 'python3', dir_path]
    argv += [path]
    logger.info("Translator TVB to NEST start : " + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )


def run_neuron_to_tvb(my_env, mpirun, path, logger):
    """
    launch Transformer NEURON to TVB
    :param mpirun: multiprocessor launcher
    :param path: path of the simulation folder
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../transformation/neuron_to_tvb.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '3', 'python3', dir_path]
    argv += [path]
    logger.info("Transformer NEURON to TVB start : " + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )


def run_tvb_to_neuron(my_env, mpirun, path, logger):
    """
    launch Transformer TVB to NEURON
    :param mpirun: multiprocessor launcher
    :param path: path of the simulation folder
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../transformation/tvb_to_neuron.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '3', 'python3', dir_path]
    argv += [path]
    logger.info("Translator TVB to NEURON start : " + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )

def run_neuron(my_env, mpirun, path_parameter, logger):
    """
    launch NEURON
    :param mpirun: multiprocessor launcher
    :param path_parameter: path of the parameter file
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../neuron/ball_and_stick.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '1', 'python3', dir_path]
    argv += [path_parameter]
    logger.info("NEURON start :" + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )

def run_nest_to_neurolib(my_env, mpirun, path, logger):
    """
    launch Transformer NEST to NEUROLIB
    :param mpirun: multiprocessor launcher
    :param path: path of the simulation folder
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../transformation/nest_to_neurolib.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '3', 'python3', dir_path]
    argv += [path]
    logger.info("Transformer NEST to NEUROLIB start : " + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )


def run_neurolib_to_nest(my_env, mpirun, path, logger):
    """
    launch Transformer NEUROLIB to TVB
    :param mpirun: multiprocessor launcher
    :param path: path of the simulation folder
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../transformation/neurolib_to_nest.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '3', 'python3', dir_path]
    argv += [path]
    logger.info("Translator Neurolib to TVB start : " + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )

def run_neurolib(my_env, mpirun, path_parameter, logger):
    """
    launch NEURON
    :param mpirun: multiprocessor launcher
    :param path_parameter: path of the parameter file
    :param logger: logger of the launcher
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../neurolib/example.py"
    argv = copy.copy(mpirun)
    argv += ['-n', '1', 'python3', dir_path]
    argv += [path_parameter]
    logger.info("NEUROLIB start :" + str(argv))
    return subprocess.Popen(argv,
                            # need to check if it's needed or not (doesn't work for me)
                            stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                            env=my_env
                            )

def save_parameter(parameters):
    """
    save the parameters of the simulations in json file
    :param parameters: dictionary of parameters
    :return: nothing
    """
    # save the value of all parameters
    f = open(parameters['path'] + '/parameter.json', "wt")
    json.dump(parameters, f)
    f.close()


if __name__ == "__main__":
    parameter_default = {"co_simulation": False,
                         "path": "",
                         "simulation_time": 1000.0,
                         "level_log": 1,
                         "resolution": 0.1,
                         "nb_neurons": [100]
                         }

    # NEST only
    path_file = os.path.dirname(__file__)
    parameter_nest_only = copy.copy(parameter_default)
    parameter_nest_only['path'] = path_file + "/../../result_sim/nest_only/"
    create_folder(parameter_nest_only['path'])
    create_folder(parameter_nest_only['path'] + "/log/")
    create_folder(parameter_nest_only['path'] + "/figures/")
    create_folder(parameter_nest_only['path'] + "/nest/")
    save_parameter(parameter_nest_only)
    logger_nest_only = create_logger(parameter_nest_only['path'], 'launcher', 1)
    my_env = os.environ.copy()
    process = run_nest(my_env, ['mpirun'], parameter_nest_only['path'] + '/parameter.json', logger_nest_only)
    process.wait()

    # TVB only
    path_file = os.path.dirname(__file__)
    parameter_tvb_only = copy.copy(parameter_default)
    parameter_tvb_only['path'] = path_file + "/../../result_sim/tvb_only/"
    create_folder(parameter_tvb_only['path'])
    create_folder(parameter_tvb_only['path'] + "/log/")
    create_folder(parameter_tvb_only['path'] + "/figures/")
    save_parameter(parameter_tvb_only)
    logger_tvb_only = create_logger(parameter_tvb_only['path'], 'launcher', 1)
    my_env = os.environ.copy()
    process = run_tvb(my_env, ['mpirun'], parameter_tvb_only['path'] + '/parameter.json', logger_tvb_only)
    process.wait()

    # Neuron only
    path_file = os.path.dirname(__file__)
    parameter_neuron_only = copy.copy(parameter_default)
    parameter_neuron_only['path'] = path_file + "/../../result_sim/neuron_only/"
    create_folder(parameter_neuron_only['path'])
    create_folder(parameter_neuron_only['path'] + "/log/")
    create_folder(parameter_neuron_only['path'] + "/figures/")
    save_parameter(parameter_neuron_only)
    logger_neuron_only = create_logger(parameter_neuron_only['path'], 'launcher', 1)
    my_env = os.environ.copy()
    process = run_neuron(my_env, ['mpirun'], parameter_neuron_only['path'] + '/parameter.json', logger_neuron_only)
    process.wait()

    # Neurolib only
    path_file = os.path.dirname(__file__)
    parameter_neurolib_only = copy.copy(parameter_default)
    parameter_neurolib_only['path'] = path_file + "/../../result_sim/neurolib_only/"
    create_folder(parameter_neurolib_only['path'])
    create_folder(parameter_neurolib_only['path'] + "/log/")
    create_folder(parameter_neurolib_only['path'] + "/figures/")
    save_parameter(parameter_neurolib_only)
    logger_neurolib_only = create_logger(parameter_neurolib_only['path'], 'launcher', 1)
    my_env = os.environ.copy()
    process = run_neurolib(my_env, ['mpirun'], parameter_neurolib_only['path'] + '/parameter.json', logger_neurolib_only)
    process.wait()

    # Co-simulation
    path_file = os.path.dirname(__file__)
    parameter_co_simulation = copy.copy(parameter_default)
    parameter_co_simulation['path'] = path_file + "/../../result_sim/co-simulation/"
    parameter_co_simulation.update({
        "co_simulation": True,
        # parameter for the synchronization between simulators
        "time_synchronization": 1.2,
        "id_nest_region": [0],
        # parameter for the transformation of data between scale
        "nb_brain_synapses": 1,
        'id_first_neurons': [1],
        "save_spikes": True,
        "save_rate": True,
    })
    run(parameter_co_simulation)

    # Co-simulation
    path_file = os.path.dirname(__file__)
    parameter_co_simulation = copy.copy(parameter_default)
    parameter_co_simulation['path'] = path_file + "/../../result_sim/co-simulation_neuron/"
    parameter_co_simulation.update({
        "co_simulation": True,
        # parameter for the synchronization between simulators
        "time_synchronization": 1.2,
        "id_nest_region": [0],
        # parameter for the transformation of data between scale
        "nb_brain_synapses": 1,
        "save_spikes": True,
        "save_rate": True,
    })
    run_neuron_tvb(parameter_co_simulation)

    # Co-simulation
    path_file = os.path.dirname(__file__)
    parameter_co_simulation = copy.copy(parameter_default)
    parameter_co_simulation['path'] = path_file + "/../../result_sim/co-simulation_neurolib/"
    parameter_co_simulation.update({
        "co_simulation": True,
        # parameter for the synchronization between simulators
        "time_synchronization": 1.2,
        "id_nest_region": [0],
        # parameter for the transformation of data between scale
        "nb_brain_synapses": 1,
        'id_first_neurons': [1],
        "save_spikes": True,
        "save_rate": True,
        "simulation_time": 1000.8,
    })
    run_nest_neurolib(parameter_co_simulation)
