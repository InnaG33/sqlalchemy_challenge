import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"/api/v1.0/start_end_date/<start_date>/<end_date><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
     # Query all results     
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    precip_dict = {}

    for result in results:
        precip_dict[result[0]] = result[1]

# Return the JSON representation of your dictionary

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data"""
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query the most active station for the last year of data
    results = session.query(Measurement.tobs).\
        filter(Measurement.station=='USC00519281').\
        filter(Measurement.date > query_date).all()

    session.close()

    # Convert list of tuples into normal list
    TOBS = list(np.ravel(results))
    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(TOBS)

# @app.route("/api/v1.0/justice-league/superhero/<superhero>")
# def justice_league_by_superhero__name(superhero):

@app.route("/api/v1.0/start_date/<start_date>")
def start_date(start_date):
# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start date.
    session = Session(engine)
    dates = session.query(Measurement.date).all()
    session.close()
    query_date = ""

    list_dates = list(np.ravel(dates))
    for date in list_dates:
        if date == str(start_date):
            query_date = date

    if query_date !="":
        session = Session(engine)
        results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= query_date).all()
        session.close()

        start_date_query = list(np.ravel(results))
        return jsonify(start_date_query)
    else:
        return jsonify({"error": f"Date not found."}), 404

@app.route("/api/v1.0/start_end_date/<start_date>/<end_date>")
def start_end_date(start_date, end_date):
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
# for dates between the start and end date inclusive.
    session = Session(engine)
    dates = session.query(Measurement.date).all()
    session.close()

    start_query_date = ""
    end_query_date = ""

    list_dates = list(np.ravel(dates))
    for date in list_dates:
        if date == str(start_date):
            start_query_date = date
        if date == str(end_date):
            end_query_date = date

    if (start_query_date !="" and end_query_date !=""):
        session = Session(engine)
        results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_query_date).\
            filter(Measurement.date <= end_query_date).all()
        session.close()

        start_end_date_query = list(np.ravel(results))
        return jsonify(start_end_date_query)

    else:
        return jsonify({"error": f"Date range not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
