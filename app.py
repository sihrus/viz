from flask import Flask, render_template, request, redirect
import json
import pandas as pd
import requests

app = Flask(__name__)
app.vars={}

@app.route('/')
def main():
  return redirect('/index')
  #return redirect('/indexd3')
  #return redirect('/d3buses')

'''
# used for testing d3... ended up not using!
@app.route('/d3buses', methods=['GET', 'POST'])
def d3buses():

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

  return render_template('d3buses.html', output=output)

@app.route('/indexd3', methods=['GET', 'POST'])
def indexd3():
  return render_template('indexd3.html')
'''

@app.route('/index', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    clicked = request.form.getlist('submit')
    if 'Realtime Heatmap of All MTA Buses' in clicked:
      return redirect('/buses')
    else:
      text = request.form['text'].upper()
      app.vars['text'] = text
      return redirect('/mybuses')
  else:
    return render_template('index.html')


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


@app.route('/buses', methods=['GET','POST'])
def buses():
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

  df['total'] = 1
  grouped = df.groupby(['MonitoredVehicleJourney_LineRef','MonitoredVehicleJourney_DestinationName'])
  df_count = grouped.count().reset_index()[['MonitoredVehicleJourney_LineRef','MonitoredVehicleJourney_DestinationName','total']]
  df_count.rename(columns={'MonitoredVehicleJourney_LineRef': 'Line'}, inplace=True)
  df_count.rename(columns={'MonitoredVehicleJourney_DestinationName': 'Direction'}, inplace=True)
  df_count.rename(columns={'total': 'Total Buses On Route'}, inplace=True)
  output2 = df_count.to_html(index=False)

  return render_template('buses.html', output=output, output2=output2)

@app.route('/mybuses', methods=['GET','POST'])
def mybuses():
  MTA_API_BASE = 'http://bustime.mta.info/api/siri/vehicle-monitoring.json?key={key}'
  MTA_API_KEY = 'ffac85e6-bf25-4762-9b43-d46b5ad2f5d8'
  # example: https://github.com/conorbranagan/bustime/blob/master/bus_status.py
  # documentation: http://bustime.mta.info/wiki/Developers/SIRIVehicleMonitoring
  df = nyc_current(MTA_API_BASE,MTA_API_KEY)
  
  text = app.vars['text']
  print "TEXT", text
  try:
    df = df[df['MonitoredVehicleJourney_LineRef'] == str('MTA NYCT_'+text)]
    df_lat_lon = df[['MonitoredVehicleJourney_VehicleLocation_Latitude','MonitoredVehicleJourney_VehicleLocation_Longitude']]
    jsonDf = df_lat_lon.dropna().to_json(orient='records')
    output = jsonDf.replace('{\"MonitoredVehicleJourney_VehicleLocation_Latitude\":',"[")
    output = output.replace(',\"MonitoredVehicleJourney_VehicleLocation_Longitude\":',",")
    output = output.replace('}',"]")

    df['total'] = 1
    grouped = df.groupby(['MonitoredVehicleJourney_LineRef','MonitoredVehicleJourney_DestinationName'])
    df_count = grouped.count().reset_index()[['MonitoredVehicleJourney_LineRef','MonitoredVehicleJourney_DestinationName','total']]
    df_count.rename(columns={'MonitoredVehicleJourney_LineRef': 'Line'}, inplace=True)
    df_count.rename(columns={'MonitoredVehicleJourney_DestinationName': 'Direction'}, inplace=True)
    df_count.rename(columns={'total': 'Total Buses On Route'}, inplace=True)
    output2 = df_count.to_html(index=False)

    return render_template('mybuses.html', output=output, output2=output2)
  except:
    flash('INVALID BUS CODE!')
    print "ERROR, BAD MTA CODE"


if __name__ == '__main__':
  app.run(port=33507)
