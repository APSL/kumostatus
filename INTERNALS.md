# Internal docs for developers

* dashboard.py
    * Parsea and read cli parameters
    * Parse and read the YML file
    * Start "Grap" object
        * Loop of graphs defined in the config file
            * Start new "GetStadistics.Metric" based on every "Graph" element of the YML
            * Load the data from CloudWatch using "GetStadistics.Get" and include in "GetStadistics.Metric"
        * Add the metrics in the general "Graph" object
            * Send all metrics to "Plot.PNG" to generate PNG images and return in base64 format
    * Send "Graph" object to jinja2 template
    * Save html result in a file
