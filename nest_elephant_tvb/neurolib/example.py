import sys
import numpy as np
from neurolib.models.aln import ALNModel
from neurolib.utils.loadData import Dataset
import matplotlib.pyplot as plt
from nest_elephant_tvb.utils import create_logger

def run_example(co_simulation, path="", simtime=100,
                level_log=1, resolution=0.1,
                time_synch=0.0, id_proxy=None, seed=0):
    logger = create_logger(path, "neurolib", level_log)
    logger.info("start ")
    if co_simulation:
        path_mpi_output = path + "/transformation/receive_from_neurolib/"+ str(id_proxy[0]) + ".txt"
        path_mpi_input = path + "/transformation/send_to_neurolib/"+ str(id_proxy[0]) + ".txt"
        chunksize = int(np.around(time_synch / resolution))
        logger.info("start chunksize : "+str(chunksize)+" "+str(time_synch)+" "+str(resolution))

    ds = Dataset("gw")
    model = ALNModel(Cmat=ds.Cmat*4.0, Dmat=ds.Dmat, logger=logger, seed=seed)
    model.params['duration'] = simtime  # in ms, simulates for 5 minutes

    model.params['mue_ext_mean'] = 1.57
    model.params['mui_ext_mean'] = 1.6
    # We set an appropriate level of noise
    model.params['sigma_ou'] = 0.00 # 0.04
    # And turn on adaptation with a low value of spike-triggered adaptation currents.
    model.params['b'] = 100.0


    def coupling_function(params, init_vars, id_proxy, chunksize):
        coupling = [np.zeros(chunksize) for i in range(len(id_proxy))]
        for index, no in enumerate(id_proxy):
            for i in range(chunksize):
                for l in range(params['N']):
                    try:
                        coupling[index][i] += params['Cmat'][l, no] * params[init_vars[0]][
                            l, int(i - params['Dmat_ndt'][l, no] - 1)]
                    except IndexError:
                        coupling[index][i] += params['Cmat'][l, no] * params[init_vars[0]][l, 0]

                coupling[index][i] *= params['c_gl'] * params['Ke_gl']
        return coupling[0]


    logger.info("start sim"); sys.stdout.flush()
    if co_simulation:
        model.run(chunkwise=True, append_outputs=True, chunksize=chunksize,
              mpi=co_simulation, coupling_function=coupling_function, id_proxy=id_proxy,
              path_mpi_input=path_mpi_input, path_mpi_output=path_mpi_output)
    else:
        model.run(append_outputs=True, mpi=co_simulation )

    logger.info("neurolib plot"); sys.stdout.flush()
    # the results of the model are also accesible through an xarray DataArray
    fig, axs = plt.subplots(1, 1, figsize=(20, 20), dpi=300)
    plt.plot(model.xr().time, model.xr().loc['rates_exc'].T)
    plt.savefig(path+"/figures/neurolib.png")
    np.save(path+"/neurolib/time.npy", model.xr().time)
    np.save(path+"/neurolib/data.npy", [model.xr().loc['rates_exc'].T, model.xr().loc['rates_inh'].T, model.xr().loc['IA']])
    logger.info("neurolib end"); sys.stdout.flush()

if __name__ == "__main__":
    import neurolib
    print(neurolib.__file__)
    if len(sys.argv) == 2:
        import json
        with open(sys.argv[1]) as f:
            parameters = json.load(f)
            if parameters['co_simulation']:
                run_example(parameters['co_simulation'], path=parameters['path'], simtime=parameters['simulation_time'],
                        level_log=parameters['level_log'], resolution=parameters['resolution'],
                        time_synch=parameters['time_synchronization'], id_proxy=parameters['id_nest_region'],
                        seed=parameters['seed'])
            else:
                run_example(parameters['co_simulation'], path=parameters['path'], simtime=parameters['simulation_time'],
                        level_log=parameters['level_log'], resolution=parameters['resolution'], seed=parameters['seed']
                        )
    else:
        print('missing argument')