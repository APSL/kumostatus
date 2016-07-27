import datetime

import boto3
import numpy


class Get(object):
    color = False

    def __init__(self, label="", hours=1, namespace="", name="",
                 dimensions=None, statistics="Average", unit="Seconds",
                 yaxis=False, compare=False):

        self.basic_label = label
        self.namespace = namespace
        self.name = name
        self.dimensions = self.rebuild_dimensions(dimensions)
        self.unit = unit
        self.statistics = statistics
        self.points = []
        self._points = {}
        self.dates = []
        self.values = []
        self.yaxis = yaxis
        self.hours = hours
        self.compare = compare

        cloudwatch = boto3.resource("cloudwatch")
        metric = cloudwatch.Metric(self.namespace, self.name)

        _delta = datetime.timedelta(minutes=0)
        fixtime = 0

        if self.compare:
            _delta = datetime.timedelta(minutes=(self.compare*60) )
            fixtime = _delta.total_seconds()
            utcnow = datetime.datetime.utcnow() - _delta
            fromutc = utcnow - datetime.timedelta(minutes=hours * 60)
        else:
            utcnow = datetime.datetime.utcnow()
            fromutc = utcnow - datetime.timedelta(minutes=hours * 60)
            
        period = 60
        if hours > 24:
            period = 60 * 2

        self.response = metric.get_statistics(
            Dimensions=self.dimensions,
            StartTime=fromutc,
            EndTime=utcnow,
            Period=period,
            Statistics=[self.statistics],
            Unit=self.unit
        )

        for i in self.response["Datapoints"]:
            _key = i["Timestamp"] + _delta
            self._points[int(_key.strftime("%s"))] = i

        _smooth_split = 0
        if len(self._points) > 300:
            _smooth_split = int(round(len(self._points)/300))

        _smooth_points = []
        _smooth_dates = []
        _smooth_values = []
        for key in sorted(self._points):
            if _smooth_split > 0:
                _smooth_points.append(self._points[key])
                _smooth_dates.append(datetime.datetime.fromtimestamp(key))
                _smooth_values.append(self._points[key][self.statistics])

                if len(_smooth_points) == _smooth_split:

                    self.points.append(_smooth_points[0])
                    self.dates.append(_smooth_dates[0])

                    if "Minimum" in self._points[key]:
                        self.values.append(min(_smooth_values))
                    elif "Maximum" in self._points[key]:
                        self.values.append(max(_smooth_values))
                    else:
                        self.values.append(max(_smooth_values))

                    _smooth_points = []
                    _smooth_dates = []
                    _smooth_values = []
            else:
                self.points.append(self._points[key])
                self.dates.append(datetime.datetime.fromtimestamp(key))
                self.values.append(self._points[key][self.statistics])

            del self._points[key]


    def label(self):
        return "%s - %s" % (self.namespace, self.name)

    def points(self):
        return self.points

    def get_max_values(self):
        if len(self.values) <= 0:
            return 0
        return max(self.values)

    def get_min_values(self):
        if len(self.values) <= 0:
            return 0
        return min(self.values)

    def get_median_values(self):
        if len(self.values) <= 0:
            return 0
        return numpy.median(self.values)

    def get_equivalent(self):
        total = sum(self.values)
        return (total / self.hours) * 24

    def __getattr__(self, name):
        if name == "median":
            return self.num_format(unit=self.unit, value=self.get_median_values())

        elif name == "min":
            return self.num_format(unit=self.unit, value=self.get_min_values())

        elif name == "max":
            return self.num_format(unit=self.unit, value=self.get_max_values())

        elif name == "equivalent":
            return self.num_format(value=self.get_equivalent())

        elif name == "name_dimension":
            if len(self.dimensions) > 0:
                return self.dimensions[0]["Value"]
            return ""

    def num_format(self, unit="Count", value=0):
        if self.unit == "Percent":
            return "%d%%" % round(value, 0)
        elif self.unit == "Count" or self.unit == "None":
            return "{:20,.0f}".format(value)
        else:
            return "{:20,.2f}".format(value)

    def rebuild_dimensions(self, dimensions):
        new_dimensions = []
        for d, l in enumerate(dimensions):
            for k in l:
                params = {str(k).lower().title(): l[k]}
                try:
                    new_dimensions[d].update(params)
                except:
                    new_dimensions.append(params)
        return new_dimensions
