import base64
from io import BytesIO
from PIL import Image

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class PNG(object):
    ax_max_value = 0
    ay_max_value = 0

    def __init__(self, datas=False):
        ay = False
        set_xlabel = False
        set_ylabel = False
        fig, ax = plt.subplots()

        try:
            if len(datas) <= 0:
                self.image = "empty"
                return
        except:
            self.image = "empty"
            return


        for s in datas:

            if len(s.dates) <= 0:
                continue
            if len(s.values) <= 0:
                continue
            if s.yaxis:
                if not ay:
                    ay = ax.twinx()
                ay.plot(
                    s.dates,
                    s.values,
                    linestyle='solid',
                    linewidth=1.8,
                    color=s.color,
                    label=s.label()
                )
                ay.set_ylim([0, self.get_max('y', s)])

                if not set_ylabel:
                    ay.set_ylabel(s.label(), color=s.color)
                    set_ylabel = True
            else:
                ax.plot(
                    s.dates,
                    s.values,
                    linestyle='solid',
                    linewidth=1.8,
                    color=s.color,
                    label=s.label()
                )
                ax.set_ylim([0, self.get_max('x', s)])

                if not set_xlabel:
                    ax.set_ylabel(s.label(), color=s.color)
                    set_xlabel = True

        ax.fmt_ydata = mdates.DateFormatter("%d")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.grid(True)

        if ay:
            ay.fmt_xdata = mdates.DateFormatter('%d')
            ay.grid(True)

        fig.autofmt_xdate()
        fig.tight_layout()

        self.output = BytesIO()
        plt.savefig(self.output, dpi=75)
        plt.close()
        self.image = self.output.getvalue()
        self.optimizepng()
        self.output.close()

    def optimizepng(self):
        buffer = BytesIO()
        img = Image.open(self.output)
        img.save(buffer, format="PNG", compress_level=5, optimize=True)
        self.image = buffer.getvalue()
        buffer.close()

    def get_max(self, f, s):
        if s.unit == "Percent":
            return 100

        m = max(s.values)
        m += m * 10 / 100

        if f == "x":
            if self.ax_max_value < m:
                self.ax_max_value = m
            return self.ax_max_value
        elif f == "y":
            if self.ay_max_value < m:
                self.ay_max_value = m
            return self.ay_max_value

    def image_base64(self):
        if self.image == "empty":
            return ""
        return base64.b64encode(self.image).decode('ascii')
