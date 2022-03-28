import sys
sys.path.append(' /home/kusch/Documents/project/co_simulation/TVB-NEST-proof/lib/soft/lib/python3.8/site-packages/')
from neurolib.models.hopf import HopfModel
from neurolib.utils.loadData import Dataset
import matplotlib.pyplot as plt

ds = Dataset("gw")
model = HopfModel(Cmat = ds.Cmat, Dmat = ds.Dmat)
model.params['duration'] = 5000 # in ms, simulates for 5 minutes

model.run(chunkwise=True, append_outputs=True, chunksize=10)

# the results of the model are also accesible through an xarray DataArray
fig, axs = plt.subplots(1, 1, figsize=(6, 2), dpi=75)
plt.plot(model.xr().time, model.xr().loc['rates_exc'].T)
plt.show()