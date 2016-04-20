from flask import Flask, render_template, request, redirect
import json
import pandas as pd
import requests

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    return redirect('/buses')
  else:
  	return render_template('index.html')

@app.route('/buses')
def buses():
  def _flatten_dict(root_key, nested_dict, flattened_dict):
      for key, value in nested_dict.iteritems():
          next_key = root_key + "_" + key if root_key != "" else key
          if isinstance(value, dict):
              _flatten_dict(next_key, value, flattened_dict)
          else:
              flattened_dict[next_key] = value
      return flattened_dict
      
  #This is useful for the live MTA Data
  def nyc_current(MTA_API_BASE, MTA_API_KEY):
      resp = requests.get(MTA_API_BASE.format(key=MTA_API_KEY)).json()
      #print resp
      info = resp['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity']
      return pd.DataFrame([_flatten_dict('', i, {}) for i in info])
  
  
  MTA_API_BASE = 'http://bustime.mta.info/api/siri/vehicle-monitoring.json?key={key}'
  MTA_API_KEY = 'ffac85e6-bf25-4762-9b43-d46b5ad2f5d8'
  # example: https://github.com/conorbranagan/bustime/blob/master/bus_status.py
  # documentation: http://bustime.mta.info/wiki/Developers/SIRIVehicleMonitoring
  df = nyc_current(MTA_API_BASE,MTA_API_KEY)

  df_lat_lon = df[['MonitoredVehicleJourney_VehicleLocation_Latitude','MonitoredVehicleJourney_VehicleLocation_Longitude']]
  jsonDf = df_lat_lon.dropna().to_json(orient='records')
  output = jsonDf.replace('{\"MonitoredVehicleJourney_VehicleLocation_Latitude\":',"[")
  output = output.replace(',\"MonitoredVehicleJourney_VehicleLocation_Longitude\":',",")
  output = output.replace('}',"]")
  output = "var buses = " + output + ";"
  text_file = open("static/data/busesnow.js", "w")
  text_file.write(output)
  text_file.close()

  df['total'] = 1
  grouped = df.groupby(['MonitoredVehicleJourney_LineRef','MonitoredVehicleJourney_DestinationName'])
  df_count = grouped.count().reset_index()[['MonitoredVehicleJourney_LineRef','MonitoredVehicleJourney_DestinationName','total']]
  #print df_count.describe()
  df_count.rename(columns={'MonitoredVehicleJourney_LineRef': 'Line'}, inplace=True)
  df_count.rename(columns={'MonitoredVehicleJourney_DestinationName': 'Direction'}, inplace=True)
  df_count.rename(columns={'total': 'Total Buses On Route'}, inplace=True)
  output = df_count.to_html(index=False)

  return render_template('buses.html', output=output)


if __name__ == '__main__':
  app.run(port=33507)
