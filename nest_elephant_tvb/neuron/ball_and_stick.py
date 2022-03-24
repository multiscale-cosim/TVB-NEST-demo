import matplotlib.pyplot as plt
from neuron import h, load_mechanisms
from neuron.units import ms, mV
import subprocess
import numpy as np
import os
import sys
from nest_elephant_tvb.utils import create_logger, _make_plot
import time

load_mechanisms(os.path.dirname(__file__)+'/../../neuron_test/detector/')
# initialisation MPI
h.nrnmpi_init()
# define dt for the simulation
pc = h.ParallelContext()

# start fresh with respect to SaveState and BBSaveState
def rmfiles():
    if pc.id() == 0:
        subprocess.run("rm -f state*.bin", shell=True)
        subprocess.run("rm -r -f bbss_out", shell=True)
        subprocess.run("rm -r -f in", shell=True)
    pc.barrier()

class Cell:
    name = "BallAndStick"
    def __init__(self, co_simulation, gid, x, y, z, theta, stim_delay, stim_w, path_input, path_output, t_synch=20.0):
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()
        self.x = self.y = self.z = 0
        h.define_shape()
        self._rotate_z(theta)
        self._set_position(x, y, z)

        if co_simulation:
            self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, path_output, t_synch, sec=self.soma)
        else:
            self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self.spike_times = h.Vector()
        self._spike_detector.record(self.spike_times)

        self._ncs = []

        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v)

        # Cell 1
        pc.set_gid2node(self._gid, pc.id())
        pc.cell(self._gid, self._spike_detector)
        if co_simulation:
            self._extern_input = h.mpi_input()
            if self._gid == 0:
                self._extern_input.set_path(path_input)
            self._extern_input.time_synch = t_synch
            self.net_ext = h.NetCon(self._extern_input, pc.gid2cell(self._gid).syn)  ### grab cell with gid==0 wherever it exists
            self.net_ext.delay = stim_delay
            self.net_ext.weight[0] = stim_w
            pc.cell(self._gid, self.net_ext)


    def __repr__(self):
        return "{}[{}]".format(self.name, self._gid)

    def _set_position(self, x, y, z):
        for sec in self.all:
            for i in range(sec.n3d()):
                sec.pt3dchange(
                    i,
                    x - self.x + sec.x3d(i),
                    y - self.y + sec.y3d(i),
                    z - self.z + sec.z3d(i),
                    sec.diam3d(i),
                )
        self.x, self.y, self.z = x, y, z

    def _rotate_z(self, theta):
        """Rotate the cell about the Z axis."""
        for sec in self.all:
            for i in range(sec.n3d()):
                x = sec.x3d(i)
                y = sec.y3d(i)
                c = h.cos(theta)
                s = h.sin(theta)
                xprime = x * c - y * s
                yprime = x * s + y * c
                sec.pt3dchange(i, xprime, yprime, sec.z3d(i), sec.diam3d(i))

    def _setup_morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dend = h.Section(name="dend", cell=self)
        self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 12.6157
        self.dend.L = 200
        self.dend.diam = 1

    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100  # Axial resistance in Ohm * cm
            sec.cm = 1  # Membrane capacitance in micro Farads / cm^2
        self.soma.insert("hh")
        for seg in self.soma:
            seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
            seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
            seg.hh.gl = 0.0003  # Leak conductance in S/cm2
            seg.hh.el = -54.3  # Reversal potential in mV
        # Insert passive current in the dendrite
        self.dend.insert("pas")
        for seg in self.dend:
            seg.pas.g = 0.001  # Passive conductance in S/cm2
            seg.pas.e = -65  # Leak reversal potential m

        self.syn = h.ExpSyn(self.dend(0.5))
        self.syn.tau = 2 * ms


class Ring:
    """A network of *N* ball-and-stick cells where cell n makes an
    excitatory synapse onto cell n + 1 and the last, Nth cell in the
    network projects to the first cell.
    """

    def __init__(
        self,
        co_simulation=False,
        N=2,
        stim_w=0.001,
        stim_t=9,
        stim_delay=0.1,
        syn_w=0.0001,
        syn_delay=0.1,
        r=3,
        path_input="",
        path_output="",
        t_synch=20.0
    ):
        """
        :param N: Number of cells.
        :param stim_w: Weight of the stimulus
        :param stim_t: time of the stimulus (in ms)
        :param stim_delay: delay of the stimulus (in ms)
        :param syn_w: Synaptic weight
        :param syn_delay: Delay of the synapse
        :param r: radius of the network
        """
        self._N = N
        self._syn_w = syn_w
        self._syn_delay = syn_delay
        theta = 2 * h.PI
        self.cells = {}
        for i in range(N):
            self.cells[i] = Cell(co_simulation, i, h.cos(theta) * r, h.sin(theta) * r, 0, theta, stim_delay, stim_w,
                                 path_input, path_output, t_synch=t_synch)

        for target in self.cells.values():
            source_gid = (target._gid - 1 + self._N) % self._N
            nc = pc.gid_connect(source_gid, target.syn)
            nc.weight[0] = self._syn_w
            nc.delay = self._syn_delay
            target._ncs.append(nc)

        # ## stimulate gid 0
        # if pc.gid_exists(0):
        #     self._netstim = h.NetStim()
        #     self._netstim.interval = 10.0
        #     self._netstim.number = 5
        #     self._netstim.start = 0.0
        #     self._nc = h.NetCon(
        #         self._netstim, pc.gid2cell(0).syn
        #     )  ### grab cell with gid==0 wherever it exists
        #     self._nc.delay = stim_delay
        #     self._nc.weight[0] = stim_w


def get_all_spikes(ring):
    local_data = {cell._gid: list(cell.spike_times) for cell in ring.cells.values()}
    all_data = pc.py_allgather([local_data])
    pc.barrier()
    pc.done()
    data = {}
    for d in all_data:
        data.update(d[0])
    return data


def prun(tstop):
    pc.set_maxstep(10 * ms)
    h.finitialize(-65 * mV)
    pc.psolve(tstop)


def run_example(co_simulation, path, nb_neurons, time_synch, resolution, simtime, level_log):
    path_input = path + "/transformation/spike_generator/neuron.txt"
    path_output = path + "/transformation/spike_detector/neuron.txt"
    while not os.path.exists(path_input + '.unlock'):
        time.sleep(1)
    while not os.path.exists(path_output + '.unlock'):
        time.sleep(1)

    logger = create_logger(path, 'neuron', level_log)
    logger.info("configure kernel")
    h.dt = resolution
    ring = Ring(co_simulation, N=nb_neurons, path_input=path_input, path_output=path_output, t_synch=time_synch)
    logger.info("run simulation")
    prun(simtime * ms)  # at tstop/2 does a SaveState.save and BBSaveState.save
    logger.info("get spikes simulation")
    stdspikes = get_all_spikes(ring)
    print(stdspikes)

    logger.info("plot result")
    times = np.concatenate(list(stdspikes.values()))
    node_id =  np.concatenate([np.ones(len(stdspikes[i]))*i for i in range(len(stdspikes))])
    print(times.shape)
    if times.shape[0] != 0:
        _make_plot(np.array([times,node_id]).ravel(),
                   times.tolist(), node_id.tolist(),
                   list(range(len(stdspikes)))
                   )
        logger.info("save plot result")
        plt.savefig(path + "/figures/plot_neuron.png")

    logger.info("exit")
    pc.barrier()
    del ring
    h.quit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        import json
        with open(sys.argv[1]) as f:
            parameters = json.load(f)
            run_example(parameters['co_simulation'], path=parameters['path'], simtime=parameters['simulation_time'],
                        level_log=parameters['level_log'], resolution=parameters['resolution'],
                        time_synch=parameters['time_synchronization'], nb_neurons=parameters['nb_neurons'][0])
    else:
        print('missing argument')
