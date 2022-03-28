import sys

import numpy as np

sys.path.append(' /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python3.8/site-packages/')
from neurolib.models.aln import ALNModel
from neurolib.utils.loadData import Dataset
import matplotlib.pyplot as plt

print("start "); sys.stdout.flush()
path_mpi_input = sys.argv[1]
path_mpi_output = sys.argv[2]
id = [int(sys.argv[3])]
chunksize = int(sys.argv[4])

ds = Dataset("gw")
model = ALNModel(Cmat=ds.Cmat, Dmat=ds.Dmat)
model.params['duration'] = 50  # in ms, simulates for 5 minutes
id_proxy = [0]

model.params['mue_ext_mean'] = 1.57
model.params['mui_ext_mean'] = 1.6
# We set an appropriate level of noise
model.params['sigma_ou'] = 0.00
# And turn on adaptation with a low value of spike-triggered adaptation currents.
model.params['b'] = 5.0


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
    print(coupling[0]); sys.stdout.flush()
    return coupling[0]


print("start sim"); sys.stdout.flush()
model.run(chunkwise=True, append_outputs=True, chunksize=10,
          mpi=True, coupling_function=coupling_function, id_proxy=[0],
          path_mpi_input=path_mpi_input , path_mpi_output=path_mpi_output)

# the results of the model are also accesible through an xarray DataArray
fig, axs = plt.subplots(1, 1, figsize=(6, 2), dpi=75)
plt.plot(model.xr().time, model.xr().loc['rates_exc'].T)
plt.show()

