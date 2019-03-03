
/*****************************************************/
/* buildMetadata - Get metadata for selected sample
*/
function buildMetadata(sample) {

  // Query and recieve sample metadata, populate the 
  // metadata table of the Dahsboard
  d3.json(`/metadata/${sample}`).then((metaData) => {
    d3.select('#meta-table').html("");  
    Object.entries(metaData).forEach(md => {
      tr = d3.select('#meta-table').append('tr');
      tr.append('td').append('small').text(md[0]);
      tr.append('td').append('small').text(`: ${md[1]}`)
    });

  // Draw the Gauge Chart for samples wash frequency
  buildGaugeChart (metaData['Wash Freq']);
  });
}

/*****************************************************/
/* buildCharts - Build the Pie and Bubble charts
*/
function buildCharts(sample) {

  d3.json(`/samples/${sample}`).then(samples => {

    // Set up pie chart for top 10 sample counts
    // Data is recieved sorted in descending order so
    // only need to take the first 10 values for the chart
    trace = {
      values    : samples.samples.slice(0,10),
      labels    : samples.otu_id.slice(0,10).map(otu => `otu: ${otu}`),
      hovertext : samples.otu_label.slice(0, 10),
      hoverinfo : 'label+value+text',
      title     : {text : 'Top 10 Sample Percentage',
                   font : {size : 20}},
      type      : 'pie'
    }

    // Layout for the pie chart. I had trouble controling 
    // height, width and position, of hard code for now.
    layout = {margin : {t:0, l:0, b:0, r:0},
              height : 450, width:500};

    // Draw Pie Chart in center column of row
    Plotly.newPlot('pie-chart', [trace], layout)

    // Setup the bubble chart, trace and layout objects
    trace = {
      x         : samples.otu_id,
      y         : samples.samples,
      mode      : 'markers',
      marker    : { size    : samples.samples,
                    symbol  : 'circle',
                    sizemin : 5,
                    color   : samples.otu_id,
                    colorscale : 'Jet'},
      hoverinfo : 'x+y'
    }

    layout = {
      title  : {text : 'Sample Count vs OTU-ID',
                font : {size : 20}},
      height : 700, 
      width  : 1200
    }

    Plotly.newPlot('scatter-plot', [trace], layout)
  });
}

/*****************************************************/
/* buildGaugeChart - Build the Gauge chart
*/
function buildGaugeChart (washFreq) {
  // Scale wash frequency to 180 degrees
  var level = (washFreq * (180/10))+5;

  // Trig to calc meter point
  var degrees = 180 - level;
  var radius  = .5;
  var radians = degrees * Math.PI / 180;

  var x = radius * Math.cos(radians);
  var y = radius * Math.sin(radians);

  // Path: may have to change to create a better triangle
  var mainPath = 'M -.0 -0.025 L .0 0.025 L ',
      pathX = String(x),
      space = ' ',
      pathY = String(y),
      pathEnd = ' Z';
  var path = mainPath.concat(pathX,space,pathY,pathEnd);

var values = [50/10, 50/10, 50/10, 50/10, 50/10, 50/10, 50/10, 50/10, 50/10, 50/10, 50]
var labels = ['9', '8', '7', '6', '5', '4', '3', '2', '1', '0', ''];
var text   = ['Diamond',  'Shinny',    'Clean',  'Sanitary', 'Average',
              'Passable', 'Managable', 'Trying', 'Crusty',   'Narly', ''];

var data = [{ 
    type : 'scatter',
    x : [0], y : [0],
    marker     : {size: 28, color:'850000'},
    showlegend : false,
    name       : 'speed',
    text       : level,
    hoverinfo  : 'text+name'},

  { values       : values,
    rotation     : 90,
    text         : labels,
    textinfo     : 'text',
    textposition : 'inside',
    marker       : {colors : ['rgba(14, 127, 0, .5)',    'rgba(110, 154, 22, .5)',
                              'rgba(170, 202, 42, .5)',  'rgba(202, 209, 95, .5)',
                              'rgba(170, 202, 42, .5)', 'rgba(232, 226, 202, .5)',
                              'rgba(210, 206, 145, .5)', 'rgba(232, 226, 202, .5)',
                              'rgba(210, 206, 145, .5)', 'rgba(232, 226, 202, .5)',
                              'rgba(155, 155, 155, 0)']},
    labels       : text,
    hoverinfo    : 'label',
    hole         : .5,
    type         : 'pie',
    showlegend   : false
}];

var layout = {
  shapes:[{
    type      : 'path',
    path      : path,
    fillcolor : '850000',
    line : { color : '850000'}
    }],

  title  : 'Wash Frequency Gauge',
  height : 550,
  width  : 600,
  xaxis  : {zeroline:false, showticklabels:false, showgrid: false, range: [-1, 1]},
  yaxis  : {zeroline:false, showticklabels:false, showgrid: false, range: [-1, 1]}
};

Plotly.newPlot('gauge-chart', data, layout);
}

/*****************************************************/
/* init - Initial setup for Dashboard page
*/
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

/*****************************************************/
/* optionChanged - Callback for sample selection change
*/
function optionChanged(newSample) {
  // Fetch new data each time a new sample is selected
  buildCharts(newSample);
  buildMetadata(newSample);
}

// Initialize the dashboard
init();
