# Generate static html files with images from CloudWatch API

This projects works just as CLI command.

## Templates

The template system is [Jinja2][cd3b9399]. It use some variables to generate the reports.

  [cd3b9399]: http://jinja.pocoo.org/ "Jinja2"

### Example template

```html
<html>
<body>
    <div class="col-md-12">

        <em>Generated at {{ gentime }}</em>

        {% for graph in graphs %}
            <div class="row">

                <div class="col-md-12">
                    <h2>{{ graph.Title }} <small>The last {{ graph.Timeframe }} hour(s)</small></h2>


                        <img class="img-responsive" src="data:image/png;base64,{{ graph.image_base64 }}">

                        {% for m in graph.metrics %}
                        <p>
                            <span style="color: {{ m.color }};">
                                {{ m.name_dimension }} / <strong>{{ m.name }}</strong>
                            </span>
                            [<span class="text-primary">median {{ m.median }}</span>]
                            [<span class="text-warning">max {{ m.max }}</span>]
                            [<span class="text-muted">min {{ m.min }}</span>]

                            {% if m.Unit == "Count" %}
                            <blockquote>
                                Equivalent to {{ m.equivalent }} per day.
                            </blockquote>
                            {% endif %}

                        </p>
                        {% endfor %}

                </div>

            </div>
        {% endfor %}
    </div>
</body>
</html>
```

## Parameters / CLI

#### dashboard.py
This is the main script.

#### --hours
Means: the last X hours.
The software works in UTC time.

#### --config
Define the route to the config file. This file must be in YML format.

#### --file
Route of the file where we has to save the generated HTML file.

_NOTE: If there is an error, the script will not overwrite the old file_

## Example config file
```yml
Credentials:
    AWS_ID: 'AAAAAAAAAAAAAAAA'
    AWS_PASS: 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
    region: 'eu-west-1'
Graphs:
    - LoadBalancer:
        title: "External Load balancer"
        metrics:
            - metric:
                label: "Latency external load balancer"
                namespace: "AWS/ELB"
                name: "Latency"
                dimensions:
                    name: "LoadBalancerName"
                    value: "DOTW-LB-EUWEST1-EXT"
                stadistics: "Average"
                unit: "Seconds"
                yaxis: False
            - metric:
                label: "Requests external load balancer"
                namespace: "AWS/ELB"
                name: "RequestCount"
                dimensions:
                    name: "LoadBalancerName"
                    value: "DOTW-LB-EUWEST1-EXT"
                stadistics: "Sum"
                unit: "Count"
                yaxis: True
```

## Example CRON jobs

```bash
* * * * * python /home/ec2-user/monitoring/dashboard.py --config="/home/ec2-user/config.yml" --hours 1 --file /var/www/status/index.html
*/2 * * * * python /home/ec2-user/monitoring/dashboard.py --config="/home/ec2-user/config.yml" --hours 8 --file /var/www/status/last8hours.html
*/10 * * * * python /home/ec2-user/monitoring/dashboard.py --config="/home/ec2-user/config.yml" --hours 24 --file /var/www/status/last24hours.html
*/10 * * * * python /home/ec2-user/monitoring/dashboard.py --config="/home/ec2-user/config.yml" --hours 48 --file /var/www/status/last48hours.html
```

## TODO

* Change the color palette. That needs solid colors and easy to read.
* Parameter to select the jinja2 templates in the command line
