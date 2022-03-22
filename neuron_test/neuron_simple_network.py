from neuron import h, load_mechanisms
from neuron.units import ms, mV
import numpy as np
import os
import sys

load_mechanisms(os.path.dirname(__file__)+'./detector/')
# initialisation MPI
h.nrnmpi_init()
# define dt for the simulation
h.dt = 0.1
print("############### dt",h.dt); sys.stdout.flush()
pc = h.ParallelContext()


class Cell:
    name = "BallAndStick"
    def __init__(self, gid, x, y, z, theta):
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()
        self.x = self.y = self.z = 0
        h.define_shape()
        self._rotate_z(theta)
        self._set_position(x, y, z)

        self._spike_detector = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self.spike_times = h.Vector()
        self._spike_detector.record(self.spike_times)

        self._ncs = []

        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v)

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
        stim_w=0.04,
        stim_t=9,
        stim_delay=1,
        syn_w=0.01,
        syn_delay=25,
        r=50,
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
        self._syn_w = syn_w
        self._syn_delay = syn_delay
        pc.set_gid2node(pc.id(), pc.id())
        theta = 2 * h.PI
        self.cells = {}
        self.cells[0] = Cell(0, h.cos(theta) * r, h.sin(theta) * r, 0, theta)
        pc.cell(self.cells[0]._gid, self.cells[0]._spike_detector)
        # ## stimulate gid 0
        # if pc.gid_exists(0):
        #     self._netstim = h.NetStim()
        #     self._netstim.interval = 10.0
        #     self._netstim.number = 5
        #     self._netstim.start = 0.0
        #     self._nc = h.NetCon(
        #         self._netstim, pc.gid2cell(pc.id()).syn
        #     )  ### grab cell with gid==0 wherever it exists
        #     self._nc.delay = stim_delay
        #     self._nc.weight[0] = stim_w
        # self._extern_input = h.NetCon('/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/peth_label',
        #                               pc.gid2cell(pc.id()).syn)
        self._extern_input = h.mpi_input()
        self._extern_input.set_path("/home/kusch/Documents/project/co_simulation/TVB-NEST-proof/neuron_test/input_port.txt")
        # self._extern_input.interval()
        self.net_ext = h.NetCon(
                self._extern_input, pc.gid2cell(pc.id()).syn #self.cells[0].syn
            )  ### grab cell with gid==0 wherever it exists
        self.net_ext.delay = stim_delay
        self.net_ext.weight[0] = stim_w
        pc.cell(self.cells[0]._gid, self.net_ext)


def get_all_spikes(ring):
    local_data = {cell._gid: list(cell.spike_times) for cell in ring.cells.values()}
    all_data = pc.py_allgather([local_data])
    pc.barrier()
    pc.done()
    data = {}
    for d in all_data:
        data.update(d[0])
    return data


def compare_dicts(dict1, dict2):
    # assume dict is {gid:[spiketimes]}

    # In case iteration order not same in dict1 and dict2, use dict1 key
    # order to access dict
    keylist = dict1.keys()

    # verify same set of keys
    assert set(keylist) == set(dict2.keys())

    # verify same count of spikes for each key
    assert [len(dict1[k]) for k in keylist] == [len(dict2[k]) for k in keylist]

    # Put spike times in array so can compare with a tolerance.
    array_1 = np.array([val for k in keylist for val in dict1[k]])
    array_2 = np.array([val for k in keylist for val in dict2[k]])
    if not np.allclose(array_1, array_2):
        print(array_1)
        print(array_2)
        print(array_1 - array_2)
    assert np.allclose(array_1, array_2)


def prun(tstop):
    pc.set_maxstep(10 * ms)
    h.finitialize(-65 * mV)
    pc.psolve(tstop)


def test_bas():
    stdspikes = {
        0: [10.925000000099914, 143.3000000001066],
        1: [37.40000000009994, 169.7750000000825],
        2: [63.87500000010596, 196.25000000005844],
        3: [90.35000000011198],
        4: [116.825000000118],
    }

    stdspikes_after_100 = {}
    for gid in stdspikes:
        stdspikes_after_100[gid] = [spk_t for spk_t in stdspikes[gid] if spk_t >= 100.0]

    ring = Ring()

    prun(200 * ms)  # at tstop/2 does a SaveState.save and BBSaveState.save
    stdspikes = get_all_spikes(ring)
    print(stdspikes)


if __name__ == "__main__":
    test_bas()
    pc.barrier()
    h.quit()