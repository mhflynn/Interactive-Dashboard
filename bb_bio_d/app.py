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


#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Samples_Metadata = Base.classes.sample_metadata
Samples = Base.classes.samples


@app.route("/")
def index():
    """Return the homepage."""
#    return '<h1> App started ... </h1>'
    return render_template("index.html")

# This commentis annoying

@app.route("/names")
def names():
    """Return a list of sample (table column) names."""
    return jsonify(Samples.__table__.columns.keys()[2:])

@app.route("/metadata/<sample>")
def sample_metadata(sample):
    """Return the MetaData for a given sample."""

    meta_cols = Samples_Metadata.__dict__

    desc = ['Sample Id', 'Ethnicity', 'Gender', 'Age', 'Location', 'BB Type', 'Wash Freq']
    cols = ['sample', 'ETHNICITY', 'GENDER', 'AGE', 'LOCATION', 'BBTYPE', 'WFREQ']
    sel  = [meta_cols[c] for c in cols]

    results = db.session.query(*sel).filter(Samples_Metadata.sample == sample).first()
    
    return jsonify([{desc[i]:results[i] for i in range(0,len(desc))}][0])


@app.route("/samples/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""

    sample_cols = Samples.__dict__
    sel = [sample_cols[c] for c in ['otu_id', 'otu_label', sample]]

    # Query and filter the data sample, only keep rows with values above 1
    results = db.session.query(*sel).filter(sel[2]>1).order_by(desc(sel[2])).all()

    data = {'otu_id'   :[r[0] for r in results], 
            'otu_label':[r[1] for r in results], 
            'samples'  :[r[2] for r in results]}

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
