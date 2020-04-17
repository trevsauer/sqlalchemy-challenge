#Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Measurement Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the Measurement table
Measurement = Base.classes.measurement

#################################################
# Station Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the Station table
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#List out available routes on home page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_only/<start_only><br>"
        f"/api/v1.0/start/end/<start>/<end><br>"
    )

#Define precipitation page which returns date and precip value in list of dictionaries
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session to connect to db
    session = Session(engine)

    # Query date and precipitation value for all dates
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Creates dictionary for each date and precipitation value, puts them into a list
    prcp_list = [] 
    for date, prcp in results:
        date_dict = {date:prcp}
        prcp_list.append(date_dict)

    # Returns jsonified list of precip values
    return jsonify(prcp_list)

#Define stations page which returns array of all station names
@app.route("/api/v1.0/stations")
def stations():
    # Create our session to connect to db
    session = Session(engine)

    # Query station names
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Returns jsonified list of all station names
    return jsonify(all_stations)

#Return last year of temperature data for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session to connect to db
    session = Session(engine)

    # Query date and temp data and filter for most active station
    results = session.query(Measurement.date, Measurement.tobs)\
                            .filter(Measurement.station == "USC00519281")\
                            .filter(Measurement.date <= "2011-01-01").all()

    session.close()

    # Creates dictionary for each date and temperature value, puts them into a list
    temp_list = [] 
    for date, tobs in results:
        temp_dict = {date:tobs}
        temp_list.append(temp_dict)

    return jsonify(temp_list)

#Define start/end dates which provideds TMIN, TMAX, TAVG for dates between provided end and start dates
@app.route("/api/v1.0/start/end/<start>/<end>")
def start_end(start, end):

    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)

#Define start date which provideds TMIN, TMAX, TAVG for dates greater than or equal to provided start date
@app.route("/api/v1.0/start_only/<start_only>")
def start_only(start_only):
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_only).all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)


if __name__ == '__main__':
    app.run(debug=True)

