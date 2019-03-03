import os

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#----------------------------------------------
# Database Setup

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Samples_Metadata = Base.classes.sample_metadata
Samples = Base.classes.samples

#----------------------------------------------
# Return the homepage.

@app.route("/")
def index():
#    return '<h1> App started ... </h1>'
    return render_template("index.html")

#----------------------------------------------
# Return a list of sample (table column) names.

@app.route("/names")
def names():

    # Sample table column names are available sample ids
    return jsonify(Samples.__table__.columns.keys()[2:])

#----------------------------------------------
# Return the MetaData for a given sample.

@app.route("/metadata/<sample>")
def sample_metadata(sample):

    # Use dictionary of metadata table columns for query selection
    meta_cols = Samples_Metadata.__dict__

    # List of lables and column keys for query and return data
    desc = ['Sample Id', 'Ethnicity', 'Gender', 'Age', 'Location', 'BB Type', 'Wash Freq']
    cols = ['sample', 'ETHNICITY', 'GENDER', 'AGE', 'LOCATION', 'BBTYPE', 'WFREQ']
    sel  = [meta_cols[c] for c in cols]

    # Get metadata for selected subject sample
    results = db.session.query(*sel).filter(Samples_Metadata.sample == sample).first()
    
    # Return JSON data for selected subject metadata
    return jsonify([{desc[i]:results[i] for i in range(0,len(desc))}][0])

#----------------------------------------------------
# Return `otu_ids`, `otu_labels` and `sample_values`.

@app.route("/samples/<sample>")
def samples(sample):

    # Select table column based on sample id
    sample_cols = Samples.__dict__
    sel = [sample_cols[c] for c in ['otu_id', 'otu_label', sample]]

    # Query and filter the data sample, only keep rows with values above 1
    results = db.session.query(*sel).filter(sel[2]>1).order_by(desc(sel[2])).all()

    # Organize return data as arrays to facilitate plotting
    data = {'otu_id'   :[r[0] for r in results], 
            'otu_label':[r[1] for r in results], 
            'samples'  :[r[2] for r in results]}

    # Return JSON for selected sample data
    return jsonify(data)

if __name__ == "__main__":
    app.run()
