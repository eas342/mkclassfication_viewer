import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
pi = np.pi


class App(object):
    def __init__(self, master):
        self.master = master
        self.thisPlayer = Bunch(
            rebounds=20.0,
            freeThrows=5.0,
            steal=5.0,
            underRim=10,
            distance=10)
        self.fig = mplfig.Figure(figsize=(1.5, 1.5))
        self.ax = self.fig.add_axes([0.025, 0.025, 0.95, 0.95], polar=True)
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=master)
        self.ax.grid(False)

        N = 5
        theta = np.arange(0.0, 2 * pi, 2 * pi / N)
        radii = [self.thisPlayer.rebounds, self.thisPlayer.freeThrows,
                 self.thisPlayer.steal, self.thisPlayer.underRim,
                 self.thisPlayer.distance]
        width = [2 * pi / (N)] * 5
        bars = (
            # self.ax.bar(0, 20, width=2 * pi, linewidth=0) +
            self.ax.bar(theta, radii, width=width, bottom=0.2))
        cmap = plt.get_cmap('jet')
        for r, bar in zip(radii, bars):
            bar.set_facecolor(cmap(r / 20.))
            bar.set_alpha(0.5)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()


class Bunch(object):
    """
    http://code.activestate.com/recipes/52308
    foo=Bunch(a=1,b=2)
    """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


def main():
    root = tk.Tk()
    app = App(root)
    tk.mainloop()

if __name__ == '__main__':
    main()