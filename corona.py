import json
import logging
import math
import os
import urllib.request

from flask import Flask, request
from redis import Redis
import datetime as dt

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# REDIS_HOST = os.getenv("REDIS_HOST", "redis")
# redis_db = Redis(host=REDIS_HOST, db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)


def rest_call(url="https://api.covid19api.com/dayone/country/np"):
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) ' \
                 'Chrome/6.0.472.63 Safari/534.3'
    headers = {'User-Agent': user_agent}

    try:
        req = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(req)
        json_data = json.loads(response.read().decode('utf8'))
        if json_data and len(json_data) != 0:
            return json_data
    except Exception as e:
        logger.warning('Error fetching data from ' + url, e)
        return None
    return None


@app.errorhandler(404)
def page_not_found(error):
    return "<h1>404</h1>"


@app.route('/country', methods=['GET'])
def country_list():
    countries = rest_call("https://api.covid19api.com/countries")

    if not countries:
        return app.response_class(
            response="<p>Error</p>",
            status=400,
            mimetype='text/html'
        )

    countries_data = []
    for country in countries:
        data = {
            "country": country["Country"],
            "country_code": country["ISO2"],
        }
        countries_data.append(data)

    response = app.response_class(
        response=json.dumps(countries_data, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/', methods=['GET'])
def home():
    corona_data_world = rest_call("https://api.covid19api.com/summary")
    if not corona_data_world:
        return app.response_class(
            response="<p>Error</p>",
            status=400,
            mimetype='text/html'
        )
    total = {
        "Total Confirmed": corona_data_world["Global"]["TotalConfirmed"],
        "Total Recovered": corona_data_world["Global"]["TotalRecovered"],
        "Total Death": corona_data_world["Global"]["TotalDeaths"]
    }
    new = {
        "New Confirmed": corona_data_world["Global"]["NewConfirmed"],
        "New Recovered": corona_data_world["Global"]["NewRecovered"],
        "New Death": corona_data_world["Global"]["NewDeaths"]
    }
    data = {
        "date": "latest",
        "country": "Global",
        "total": total,
        "new": new
    }

    np_data = None
    for each_country_data in corona_data_world["Countries"]:
        if each_country_data["CountryCode"] == "NP":
            np_data = each_country_data
            break

    total = {
        "Total Confirmed": np_data["TotalConfirmed"],
        "Total Recovered": np_data["TotalRecovered"],
        "Total Death": np_data["TotalDeaths"]
    }
    new = {
        "New Confirmed": np_data["NewConfirmed"],
        "New Recovered": np_data["NewRecovered"],
        "New Death": np_data["NewDeaths"]
    }
    data["Nepal"] = {
        "date": np_data["Date"].replace("T", " ").replace("Z", " UTC"),
        "country": np_data["Country"],
        "total": total,
        "new": new
    }

    response = app.response_class(
        response=json.dumps(data, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/all', methods=['GET'])
def all_country_data():
    corona_data_world = rest_call("https://api.covid19api.com/summary")

    if not corona_data_world:
        return app.response_class(
            response="<p>Error</p>",
            status=400,
            mimetype='text/html'
        )

    all_data = []
    for each_country_data in corona_data_world["Countries"]:
        total = {
            "Total Confirmed": each_country_data["TotalConfirmed"],
            "Total Recovered": each_country_data["TotalRecovered"],
            "Total Death": each_country_data["TotalDeaths"]
        }
        new = {
            "New Confirmed": each_country_data["NewConfirmed"],
            "New Recovered": each_country_data["NewRecovered"],
            "New Death": each_country_data["NewDeaths"]
        }
        data = {
            "date": each_country_data["Date"].replace("T", " ").replace("Z", " UTC"),
            "country": each_country_data["Country"],
            "country_code": each_country_data["CountryCode"],
            "total": total,
            "new": new
        }
        all_data.append(data)

    response = app.response_class(
        response=json.dumps(all_data, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/<country_code>', methods=['GET'])
def country_data(country_code):
    corona_data_world = rest_call("https://api.covid19api.com/summary")

    if not corona_data_world:
        return app.response_class(
            response="<p>Error</p>",
            status=400,
            mimetype='text/html'
        )

    country_data = None
    for each_country_data in corona_data_world["Countries"]:
        if country_code == each_country_data["CountryCode"].lower():
            country_data = each_country_data
            break

    if not country_data:
        return app.response_class(
            response="<p>Error</p>",
            status=400,
            mimetype='text/html'
        )

    total = {
        "Total Confirmed": country_data["TotalConfirmed"],
        "Total Recovered": country_data["TotalRecovered"],
        "Total Death": country_data["TotalDeaths"]
    }
    new = {
        "New Confirmed": country_data["NewConfirmed"],
        "New Recovered": country_data["NewRecovered"],
        "New Death": country_data["NewDeaths"]
    }
    data = {
        "date": country_data["Date"].replace("T", " ").replace("Z", " UTC"),
        "country": country_data["Country"],
        "total": total,
        "new": new
    }
    response = app.response_class(
        response=json.dumps(data, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/history/<country_code>', methods=['GET'])
def country_history_data(country_code):
    # date = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=30)
    # print(date.isoformat())
    # url = "https://api.covid19api.com/live/country/{}/status/confirmed/date/{}".format(country_code, date.isoformat()+"Z")



    date = dt.datetime.utcnow().date().isoformat()
    corona_data = None
    if os.path.exists(date+country_code):
        html = ""
        with open(date+country_code, "r") as f:
            html = f.read()
            f.close()
        response = app.response_class(
            response=html,
            status=200,
            mimetype='text/html'
        )
        return response
    else:
        url = "https://api.covid19api.com/country/"+country_code
        # url = "https://api.covid19api.com/total/dayone/country/"+country_code
        corona_data = rest_call(url)

    if not corona_data:
        return app.response_class(
            response="<p>Invalid country code {}</p>".format(country_code),
            status=400,
            mimetype='text/html'
        )

    html = '''
<!DOCTYPE html>
<html>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<head>
<style>
table {
  width:100%;
}
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
th, td {
  padding: 5px;
  text-align: left;
}
table#t01 tr:nth-child(even) {
  background-color: #eee;
}
table#t01 tr:nth-child(odd) {
 background-color: #fff;
}
table#t01 th {
  background-color: black;
  color: white;
}
</style>
</head>
<body>

<h2>Corona Data {{Country}}</h2>

<table id="t01">
  <tr>
    <th>Date</th>
    <th>Confirmed</th> 
    <th>Recovered</th>
    <th>Death</th>
  </tr>
  {{row-of-table}}
</table>
</body>
</html>
    '''
    row = '''
  <tr>
    <td>{{Date}}</td>
    <td>{{Confirmed}}</td> 
    <td>{{Recovered}}</td>
    <td>{{Death}}</td>
  </tr>
    '''
    all_rows = ""
    country = None
    previousDate, currentDate = None, None
    for each_day_data in reversed(corona_data):
        country = str(each_day_data["Country"])
        previousDate = str(each_day_data["Date"]).split("T")[0]
        break

    prevConfirmed, prevRecovered, prevDeath = [0] * 3
    confirmed, recovered, death = [0] * 3
    isFirst = True
    data_date = previousDate
    for each_day_data in reversed(corona_data):
        currentDate = str(each_day_data["Date"]).split("T")[0]
        if currentDate != previousDate:
            if isFirst:
                r = row.replace("{{Date}}", "Total") \
                    .replace("{{Confirmed}}", str(confirmed)) \
                    .replace("{{Recovered}}", str(recovered)) \
                    .replace("{{Death}}", str(death))
                all_rows = all_rows + r
            else:
                r = row.replace("{{Date}}", data_date) \
                    .replace("{{Confirmed}}", str(int(math.fabs(prevConfirmed - confirmed)))) \
                    .replace("{{Recovered}}", str(int(math.fabs(prevRecovered - recovered)))) \
                    .replace("{{Death}}", str(int(math.fabs(prevDeath - death))))
                all_rows = all_rows + r
                data_date = previousDate
            previousDate = currentDate
            prevConfirmed, prevRecovered, prevDeath = confirmed, recovered, death
            confirmed, recovered, death = [0] * 3
            isFirst = False

        confirmed = confirmed + each_day_data["Confirmed"]
        recovered = recovered + each_day_data["Recovered"]
        death = death + each_day_data["Deaths"]

    html = html.replace("{{row-of-table}}", all_rows) \
        .replace("{{Country}}", country)
    with open(date+country_code, "w") as f:
        f.write(html)
        f.close()
    response = app.response_class(
        response=html,
        status=200,
        mimetype='text/html'
    )
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "8443")), debug=False)
