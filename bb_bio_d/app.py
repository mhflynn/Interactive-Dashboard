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
    print (results)
    
    #return jsonify([{desc[i]:list(results)[i] for i in range(0,len(desc))}][0])
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


@app.route("/oldnames")
def oldnames():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Return a list of the column names (sample names)
    return jsonify(list(df.columns)[2:])



@app.route("/oldmetadata/<sample>")
def old_sample_metadata(sample):
    """Return the MetaData for a given sample."""
    sel = [
        Samples_Metadata.sample,
        Samples_Metadata.ETHNICITY,
        Samples_Metadata.GENDER,
        Samples_Metadata.AGE,
        Samples_Metadata.LOCATION,
        Samples_Metadata.BBTYPE,
        Samples_Metadata.WFREQ,
    ]

    results = db.session.query(*sel).filter(Samples_Metadata.sample == sample).all()

    print (results)

    # Create a dictionary entry for each row of metadata information
    sample_metadata = {}
    for result in results:
        sample_metadata["sample"] = result[0]
        sample_metadata["ETHNICITY"] = result[1]
        sample_metadata["GENDER"] = result[2]
        sample_metadata["AGE"] = result[3]
        sample_metadata["LOCATION"] = result[4]
        sample_metadata["BBTYPE"] = result[5]
        sample_metadata["WFREQ"] = result[6]

    print(sample_metadata)
    return jsonify(sample_metadata)


@app.route("/oldsamples/<sample>")
def oldsamples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Filter the data based on the sample number and
    # only keep rows with values above 1
    sample_data = df.loc[df[sample] > 1, ["otu_id", "otu_label", sample]]
    # Format the data to send as json
    data = {
        "otu_ids": sample_data.otu_id.values.tolist(),
        "sample_values": sample_data[sample].values.tolist(),
        "otu_labels": sample_data.otu_label.tolist(),
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
