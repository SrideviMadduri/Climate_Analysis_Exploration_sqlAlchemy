import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
from dateutil.relativedelta import relativedelta   

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

print(Base.classes.keys())
# Save reference to the table
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
        f"/api/v1.0/&lt;start&gt;<br/>"                
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB    
    #session = Session(engine)
    with Session(engine) as session:
        """ Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
        Return the JSON representation of your dictionary."""      
        recent_date = session.query(func.max(Measurement.date)).scalar()
        recent_date_minus_year = (datetime.strptime(recent_date, '%Y-%m-%d') - relativedelta(years=1)).strftime('%Y-%m-%d') 
        # Query all Measurement
        results =  session.query(Measurement.date, Measurement.prcp)\
            .filter(Measurement.date.between(recent_date_minus_year,recent_date))\
            .all()
        
    # Create a dictionary from the row data and append to a list of  all_date_percp
    all_date_percp = []
    for date, prcp in results:
        date_percp_dict = {date: prcp}  
        # date_percp_dict[date] = prcp
        all_date_percp.append(date_percp_dict)

    return jsonify(all_date_percp)

@app.route("/api/v1.0/stations")
def stations():
    with Session(engine) as session:        
        """ Return a JSON list of stations from the dataset."""          
    # Query all Station
        results = session.query(Station.name).all()
         
    #Convert list of tuples into normal list
    all_names = list(np.ravel(results))  

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB    
    with Session(engine) as session:
        """* Query the dates and temperature observations of the most active station for the previous year of data.
        * Return a JSON list of temperature observations (TOBS) for the previous year."""         
        recent_date_temp = session.query(func.max(Measurement.date)).scalar()    
        recent_date_minus_year_temp = (datetime.strptime(recent_date_temp, '%Y-%m-%d') - relativedelta(years=1)).strftime('%Y-%m-%d')
    
    # Query the dates and temperature observations of the most active station for the previous year of data
    # results = session.query(Measurement.date, Measurement.tobs)
    results = session.query(Measurement.tobs)\
        .filter(Measurement.date.between(recent_date_minus_year_temp,recent_date_temp, ) ,Measurement.station =='USC00519281')\
        .all()
      # Create a dictionary from the row data and append to a list of  all_date_tobs
    
    #Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))
    
    return jsonify(all_tobs)  


@app.route("/api/v1.0/<start>") 
@app.route("/api/v1.0/<start>/<end>")

def min_avg_max_temp2(start, end=None):
    """* Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
    * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.
    * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive)."""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    with Session(engine) as session:
        results =session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start)
        if end:
            results=results.filter( Measurement.date <= end)
        
        results = results.all()
    
     # Create a dictionary from the row data and append to a list of  all_min_max_avg_date
    all_min_max_avg_date = []
    
    for min, max, avg in results:
        date_tobs_dict = {}
        date_tobs_dict["TMIN"] = min  
        date_tobs_dict["TMAX"] = max
        date_tobs_dict["TAVG"] = avg   
        all_min_max_avg_date.append(date_tobs_dict)
    

    return jsonify(all_min_max_avg_date)


    
if __name__ == '__main__':
    app.run(debug=True)
