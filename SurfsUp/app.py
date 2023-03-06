import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"Here's the Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_year = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()
    session.close()

    all_scores = []
    for date, prcp in precipitation_year:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        all_scores.append(prcp_dict)

    return jsonify(all_scores)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Return a JSON list of stations from the dataset.
    results = session.query(Measurement.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
# Query the dates and temperature observations of the most-active station
    total_year_temp = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').all()
    session.close()
# Return a JSON list of temperature observations for the previous year
    all_observations = []
    for date, tobs in total_year_temp:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperatures"] = tobs
        all_observations.append(tobs_dict)

    return jsonify(all_observations)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    # Return a JSON list of the min, max,avg temp for a specified start or start-end range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    
    start_tobs = []
    for min, avg, max in results:
        start_dict = {}
        start_dict["Min Temp"] = min
        start_dict["Average Temp"] = avg
        start_dict["Max Temp"] = max
        start_tobs.append(start_dict) 
        return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    
    start_end_tobs = []
    for min, avg, max in results:
        start_end_dict = {}
        start_end_dict["Min Temp"] = min
        start_end_dict["Average Temp"] = avg
        start_end_dict["Max Temp"] = max
        start_end_tobs.append(start_end_dict) 
        return jsonify(start_end_tobs)
    
if __name__ == '__main__':
    app.run(debug=True)
