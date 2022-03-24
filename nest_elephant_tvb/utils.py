import os
import shutil
import logging
import numpy

def create_logger(path, name, log_level):
    """
    create a logger
    it's important for debugging the co-simulation because each modules is in independent processe
    :param path: path of the result
    :param name: name of the logger and for the file
    :param log_level: level of log
    :return: logger
    """
    # Configure logger
    logger = logging.getLogger(name)
    fh = logging.FileHandler(path + '/log/' + name + '.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if log_level == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif log_level == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif log_level == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif log_level == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif log_level == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)
    return logger


def create_folder(path):
    """
    creation of the folder and if already exist delete it
    :param path: path of the folder
    :return: nothing
    """
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)

def _make_plot(ts, ts1, node_ids, neurons, hist=True, hist_binwidth=5.0,
               grayscale=False, title=None, xlabel=None):
    """
    COPY FUNCTION FROM NEST SIMULATOR
    Generic plotting routine.

    Constructs a raster plot along with an optional histogram (common part in
    all routines above).

    Parameters
    ----------
    ts : list
        All timestamps
    ts1 : list
        Timestamps corresponding to node_ids
    node_ids : list
        Global ids corresponding to ts1
    neurons : list
        Node IDs of neurons to plot
    hist : bool, optional
        Display histogram
    hist_binwidth : float, optional
        Width of histogram bins
    grayscale : bool, optional
        Plot in grayscale
    title : str, optional
        Plot title
    xlabel : str, optional
        Label for x-axis
    """
    import matplotlib.pyplot as plt

    plt.figure()

    if grayscale:
        color_marker = ".k"
        color_bar = "gray"
    else:
        color_marker = "."
        color_bar = "blue"

    color_edge = "black"

    if xlabel is None:
        xlabel = "Time (ms)"

    ylabel = "Neuron ID"

    if hist:
        ax1 = plt.axes([0.1, 0.3, 0.85, 0.6])
        plotid = plt.plot(ts1, node_ids, color_marker)
        plt.ylabel(ylabel)
        plt.xticks([])
        xlim = plt.xlim()

        plt.axes([0.1, 0.1, 0.85, 0.17])
        t_bins = numpy.arange(
            numpy.amin(ts), numpy.amax(ts),
            float(hist_binwidth)
        )
        n, _ = _histogram(ts, bins=t_bins)
        num_neurons = len(numpy.unique(neurons))
        heights = 1000 * n / (hist_binwidth * num_neurons)

        plt.bar(t_bins, heights, width=hist_binwidth, color=color_bar,
                edgecolor=color_edge)
        plt.yticks([
            int(x) for x in
            numpy.linspace(0.0, int(max(heights) * 1.1) + 5, 4)
        ])
        plt.ylabel("Rate (Hz)")
        plt.xlabel(xlabel)
        plt.xlim(xlim)
        plt.axes(ax1)
    else:
        plotid = plt.plot(ts1, node_ids, color_marker)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    if title is None:
        plt.title("Raster plot")
    else:
        plt.title(title)

    plt.draw()

    return plotid

def _histogram(a, bins=10, bin_range=None, normed=False):
    """
    COPY FUNCTION FROM NEST SIMULATOR
    Calculate histogram for data.

    Parameters
    ----------
    a : list
        Data to calculate histogram for
    bins : int, optional
        Number of bins
    bin_range : TYPE, optional
        Range of bins
    normed : bool, optional
        Whether distribution should be normalized

    Raises
    ------
    ValueError
    """
    from numpy import asarray, iterable, linspace, sort, concatenate

    a = asarray(a).ravel()

    if bin_range is not None:
        mn, mx = bin_range
        if mn > mx:
            raise ValueError("max must be larger than min in range parameter")

    if not iterable(bins):
        if bin_range is None:
            bin_range = (a.min(), a.max())
        mn, mx = [mi + 0.0 for mi in bin_range]
        if mn == mx:
            mn -= 0.5
            mx += 0.5
        bins = linspace(mn, mx, bins, endpoint=False)
    else:
        if (bins[1:] - bins[:-1] < 0).any():
            raise ValueError("bins must increase monotonically")

    # best block size probably depends on processor cache size
    block = 65536
    n = sort(a[:block]).searchsorted(bins)
    for i in range(block, a.size, block):
        n += sort(a[i:i + block]).searchsorted(bins)
    n = concatenate([n, [len(a)]])
    n = n[1:] - n[:-1]

    if normed:
        db = bins[1] - bins[0]
        return 1.0 / (a.size * db) * n, bins
    else:
        return n, bins
