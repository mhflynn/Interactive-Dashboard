
var gMetaData = [];
var gSamples = {};

function buildMetadata(sample) {

  // @TODO: Complete the following function that builds the metadata panel

  // Use `d3.json` to fetch the metadata for a sample
    // Use d3 to select the panel with id of `#sample-metadata`

    // Use `.html("") to clear any existing metadata

    // Use `Object.entries` to add each key and value pair to the panel
    // Hint: Inside the loop, you will need to use d3 to append new
    // tags for each key-value in the metadata.

    // BONUS: Build the Gauge Chart
    // buildGauge(data.WFREQ);

  d3.json(`/metadata/${sample}`).then((metaData) => {
    d3.select('#meta-table').html("");  
    Object.entries(metaData).forEach(md => {
      tr = d3.select('#meta-table').append('tr');
      tr.append('td').text(md[0]);
      tr.append('td').text(`: ${md[1]}`)
    });
  });
}

function buildCharts(sample) {

  d3.json(`/samples/${sample}`).then(samples => {
    gSamples = samples;

    // Set up pie chart
    trace = {
      values : samples.samples.slice(0,10),
      labels : samples.otu_id.slice(0,10),
      hovertext: samples.otu_label.slice(0, 10),
      hoverinfo: "hovertext",
      type: 'pie'
    }

    layout = {margin: {t:0, l:0, b:0, r:0},
              height:400, width:550};
    //layout = {height:600, width:600};
    //layout = {autosize:true, automargin:true};

    Plotly.plot('pie-chart', [trace], layout)

    // Setup the bubble chart
    trace = {
      x: samples.otu_id,
      y: samples.samples,
      mode: 'markers',
      marker: { size:samples.samples}
    }
    layout = {title:"Scatter", height:700, width:1800}

    Plotly.plot('scatter-plot',[trace], layout, {})
  });
}

function init() {
  // Grab a reference to the dropdown select element
  var selector = d3.select("#selDataset");

  // Use the list of sample names to populate the select options
  d3.json("/names").then((sampleNames) => {
    sampleNames.forEach((sample) => {
      selector
        .append("option")
        .text(sample)
        .property("value", sample);
    });

    // Use the first sample from the list to build the initial plots
    const firstSample = sampleNames[0];
    buildCharts(firstSample);
    buildMetadata(firstSample);
  });
}

function optionChanged(newSample) {
  // Fetch new data each time a new sample is selected
  buildCharts(newSample);
  buildMetadata(newSample);
}

// Initialize the dashboard
init();
