function buildMetadata(sample) {

    var url = "/metadata/" + sample;
    d3.json(url).then((metadataObj) => {
        var sampleMetadata = d3.select("#sample-metadata");
        sampleMetadata.html("");
        Object.keys(metadataObj).forEach(function (key) {
            var metadata = key + ": " + metadataObj[key];
            sampleMetadata.append("div").text(metadata)
        });
    });
}

function buildGaugeChart(dataList) {
    let sentiment_score = calculateSentimentScore(dataList);
    var level = 20 * sentiment_score;
    var degrees = 180 - level,
        radius = .5;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);

    var mainPath = 'M -.0 -0.025 L .0 0.025 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);

    var data = [{
        type: 'scatter',
        x: [0], y: [0],
        marker: {size: 28, color: '850000'},
        showlegend: false,
        name: 'speed',
        text: level,
        hoverinfo: 'text+name'
    },
        {
            values: [10 / 9, 10 / 9, 10 / 9, 10 / 9, 10 / 9, 10 / 9, 10 / 9, 10 / 9, 10 / 9, 10],
            rotation: 90,
            text: ['8-9', '7-8', '6-7', '5-6', '4-5', '3-4', '2-3', '1-2', '0-1', ''],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: ['rgba(14, 127, 0, .5)',
                    'rgba(14, 148, 0, 0.5)',
                    'rgba(110, 154, 22, .5)',
                    'rgba(129, 182, 22, 0.5)',
                    'rgba(170, 202, 42, .5)',
                    'rgba(191, 224, 45, 0.5)',
                    'rgba(202, 209, 95, .5)',
                    'rgba(210, 206, 145, .5)',
                    'rgba(232, 226, 202, .5)',
                    'rgba(255, 255, 255, 0)']
            },
            labels: ['8-9', '7-8', '6-7', '5-6', '4-5', '3-4', '2-3', '1-2', '0-1', ''],
            hoverinfo: 'label',
            hole: .5,
            type: 'pie',
            showlegend: false
        }];
    var layout = {
        shapes: [{
            type: 'path',
            path: path,
            fillcolor: '850000',
            line: {
                color: '850000'
            }
        }],
        title: 'Email Sentiment Guage',
        height: 400,
        width: 400,
        xaxis: {
            zeroline: false, showticklabels: false,
            showgrid: false, range: [-1, 1]
        },
        yaxis: {
            zeroline: false, showticklabels: false,
            showgrid: false, range: [-1, 1]
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 10,
            r: 40,
            t: 100,
            b: 10,
            pad: 10
        }
    };
    Plotly.newPlot("gauge", data, layout);

}


function validOrganizationName(name) {
    if (name !== null) {
        if (name.indexOf("\"") !== -1) {
            return false;
        }
        if (name.indexOf("\n") !== -1) {
            return false;
        }
        var valid = /^[a-zA-Z ]*$/.test(name);
        if (valid) {
            return true;
        }
    }
    return false;
}

function buildBarGraph(dataList) {
    let organizationsMap = {};
    organizationsMapList = [];
    let organizationNames = [];
    let organizationCounts = [];
    let organizationCountNames = [];
    let minCount = 1;
    dataList.forEach((email) => {
        let organizations = email.organizations;
        if (organizations !== undefined && organizations !== null) {
            organizations.forEach((organization) => {
                let organizationName = organization['name'];
                if (validOrganizationName(organizationName) === true) {
                    if (organizationsMap[organizationName] !== undefined) {
                        organizationName = organizationName.trim();
                        organizationsMap[organizationName] = organizationsMap[organizationName] + 1;
                    } else {
                        organizationsMap[organizationName] = 1;
                    }
                }
            });
        }
    });

    for (var k in organizationsMap) organizationNames.push(k);
    organizationNames.sort();
    organizationNames.forEach((name) => {
        organizationCounts.push(parseInt(organizationsMap[name]));
    })

    let organizationCountsSorted = organizationCounts.splice(0);
    organizationCountsSorted.sort((a, b) => a - b).reverse();

    if (organizationCountsSorted.length > 9) {
        organizationCountsSorted = organizationCountsSorted.slice(0, 10);
        minCount = organizationCountsSorted[9];
    }
    let totalCount = 10
    organizationNames.forEach((name) => {
        if (organizationsMap[name] >= minCount && totalCount > 0) {
            organizationsMapList.push({
                "name": name,
                "count": organizationsMap[name]
            })
            totalCount--;
        }
    })
    organizationsMapList = organizationsMapList.slice(0, 10);
    organizationNames = organizationNames.slice(0, 10);
    organizationCounts = organizationCounts.slice(0, 10);
    organizationsMapList = organizationsMapList.reverse();
    var trace1 = {
        x: organizationsMapList.map(row => row.count),
        y: organizationsMapList.map(row => row.name),
        name: "Organization",
        type: "bar",
        orientation: "h",
        marker: {
            color: 'rgba(35, 70, 125, .8)',
        }
    };

    // data
    var organizationsMapList = [trace1];

    // Apply the group bar mode to the layout
    var layout = {
        title: "Top 10 Organizations",
        margin: {
            l: 200,
            r: 50,
            t: 50,
            b: 50,
            pad: 10
        }
    };
    Plotly.newPlot("bar", organizationsMapList, layout);
}


function init() {
    var selector = d3.select("#selDataset");
    url = "https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json";
    d3.json(url).then((data) => {
        let max = 10;
        let dataList = data.dataList;
        dataList = dataList.splice(0, max);
        buildGaugeChart(dataList);
        buildBarGraph(dataList);
    });
}

function optionChanged(emailData) {
    console.log("emailData: " + emailData);
    var max = parseInt(emailData);
    url = "https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json";
    d3.json(url).then((data) => {
        let dataList = data.dataList;
        dataList = dataList.splice(0, max);
        buildGaugeChart(dataList);
        buildBarGraph(dataList);
    });
    var cloudImage = d3.select("#cloudImage");
    var cloud = d3.select("#cloud");
    cloud.html("");
    cloud.selectAll("*").remove();
    var imageURL = "/cloud/" + emailData;
    var myimage = cloud.append('img')
        .attr('src', imageURL)
        .attr('width', 600)
        .attr('height', 400)
        .attr('style', 'margin:0px')
}


function calculateSentimentScore(dataList) {
    let score = 0;
    let count = 0;
    dataList.forEach((email) => {
        console.log(email.sentiment)
        if (email.sentiment === 'NEUTRAL') {
            score += 5;
        } else if (email.sentiment === 'POSITIVE') {
            score += 9;
        }
        count++;
    });
    if (count > 0) {
        score = score / count;
    }
    console.log("Sentiment Score: " + score);
    return score;
}

// Initialize the dashboard
init();
