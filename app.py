import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close()
    earliest_date = datetime.datetime.strptime(last_date.date, '%Y-%m-%d')
    earliest_date = earliest_date - datetime.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip =  pd.DataFrame(session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= earliest_date)).dropna() 
            #.filter(Measurement.prcp > 0))

    # Save the query results as a Pandas DataFrame and set the index to the date column
    precip = precip.set_index('date')
    precip = precip.groupby('date').max()    
    
    # Sort the dataframe by date
    precip = precip.sort_index(ascending=True)
    
    # Convert DataFrame to data dictionary
    precip_date = precip.to_dict(orient="index")
       
    return jsonify(precip_date)
    
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to show list of stations
    stations = session.query(Station.station)
    session.close()
    
    # Load list into data dictionary
    all_stations = []
    for station in stations:
        station_dict = {}
        station_dict["stations"] = station
        all_stations.append(station_dict)
        
    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram

    # Perform a query to retrieve the data and tobs scores
    temp_last_date = session.query(Measurement.date).filter(Measurement.station == "USC00519281").order_by(Measurement.date.desc()).first()
    temp_earliest_date = datetime.datetime.strptime(temp_last_date.date, '%Y-%m-%d')
    temp_earliest_date = temp_earliest_date - datetime.timedelta(days=365)
    temp =  pd.DataFrame(session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= temp_earliest_date))
               
    session.close()
    
    # Save the query results as a Pandas DataFrame and set the index to the date column
    temp = temp.set_index('date')
    #precip = precip.groupby('date').max()

    # Sort the dataframe by date
    temp = temp.sort_index(ascending=True)
   
    # Convert  DataFrame to data dictionary  
    station_temp = temp.to_dict(orient="index")
       
    return jsonify(station_temp)
    

@app.route("/api/v1.0/<start>")
def temps(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and tobs scores
    temp_earliest_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    temp = pd.DataFrame(session.query(func.min(Measurement.tobs).label("TMIN"),func.avg(Measurement.tobs).label("TAVG"),func.max(Measurement.tobs).label("TMAX")).filter(Measurement.date >= temp_earliest_date))
    session.close()           
    
    # Convert  DataFrame to data dictionary  
    temp = temp.to_dict(orient="index")
       
    return jsonify(temp)


@app.route("/api/v1.0/<start>/<end>")
def temp(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and tobs scores
    temp_earliest_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    temp_end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    temp = pd.DataFrame(session.query(func.min(Measurement.tobs).label("TMIN"),func.avg(Measurement.tobs).label("TAVG"),func.max(Measurement.tobs).label("TMAX")).filter(Measurement.date >= temp_earliest_date).filter(Measurement.date <= temp_end_date))
    session.close()           
    
    # Convert  DataFrame to data dictionary  
    temp = temp.to_dict(orient="index")
       
    return jsonify(temp)





if __name__ == '__main__':
    app.run(debug=True)
