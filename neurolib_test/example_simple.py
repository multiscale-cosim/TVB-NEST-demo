import sys
sys.path.append(' /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python3.8/site-packages/')
from neurolib.models.aln import ALNModel
from neurolib.utils.loadData import Dataset
import matplotlib.pyplot as plt
import scipy
import neurolib.utils.functions as func

ds = Dataset("gw")
model = ALNModel(Cmat = ds.Cmat, Dmat = ds.Dmat)
model.params['duration'] = 5*60*1000 # in ms, simulates for 5 minutes

model.params['mue_ext_mean'] = 1.57
model.params['mui_ext_mean'] = 1.6
# We set an appropriate level of noise
model.params['sigma_ou'] = 0.09
# And turn on adaptation with a low value of spike-triggered adaptation currents.
model.params['b'] = 5.0

model.run(chunkwise=True, chunksize=100000, bold=True)


# Plot functional connectivity and BOLD timeseries (z-scored)
fig, axs = plt.subplots(1, 2, figsize=(6, 2), dpi=75, gridspec_kw={'width_ratios' : [1, 2]})
axs[0].imshow(func.fc(model.BOLD.BOLD[:, 5:]))
axs[1].imshow(scipy.stats.mstats.zscore(model.BOLD.BOLD[:, model.BOLD.t_BOLD>10000], axis=1), aspect='auto',
              extent=[model.BOLD.t_BOLD[model.BOLD.t_BOLD>10000][0], model.BOLD.t_BOLD[-1], 0, model.params['N']])

axs[0].set_title("FC")
axs[0].set_xlabel("Node")
axs[0].set_ylabel("Node")
axs[1].set_xlabel("t [ms]")

# the results of the model are also accesible through an xarray DataArray
fig, axs = plt.subplots(1, 1, figsize=(6, 2), dpi=75)
plt.plot(model.xr().time, model.xr().loc['rates_exc'].T)
plt.show()