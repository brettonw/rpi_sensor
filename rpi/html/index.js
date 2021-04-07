"use strict;"

let Html = Bedrock.Html.Builder;

let computeColor = function (value, min, max, minColor, maxColor, zeroColor) {
    if (value == 0) return zeroColor; else if (value < min) return minColor; else if (value > max) return maxColor;

    let interpolant = (value - min) / (max - min);
    //interpolant = Math.min (1, Math.max (0, interpolant));
    let rValue = Math.floor(255 * ((interpolant < 0.5) ? Math.sqrt(interpolant * 2) : 1));
    let gValue = Math.floor(255 * ((interpolant > 0.5) ? Math.sqrt(1 - ((interpolant * 2) - 1)) : 1));
    return "rgb(" + rValue + "," + gValue + ",0)";
};

let makeScale = function () {
    let element = document.getElementById("scaleBar");
    let height = element.clientHeight / element.clientWidth;
    let builder = Html.begin ("http://www.w3.org/2000/svg;svg", { attributes: { width: "100%", height: "100%", viewBox: "0 0 1 " + height },  style: { margin: "0", display: "block" } });
    const divisions = 100;
    let scale = 1 / divisions;
    for (let i = 0; i < divisions; ++i) {
        builder.add ("http://www.w3.org/2000/svg;rect", { attributes: { x: i * scale, y: 0, width: scale, height: height, fill: computeColor ((i + 0.5) * scale, 0, 1) } });
    }
    document.getElementById("scaleBar").appendChild(builder.end ());
};
makeScale ();


let refresh = function () {

    document.getElementById("bodysize").innerHTML = document.body.clientWidth + " x " + document.body.clientHeight;

    // timestamps are in seconds or ms, but we always want ms
    let conditionTime = function (t) {
        // if t is in seconds, expand it to ms
        return (t < 1.e10) ? (t * 1e3) : t;
    };

    // compute the delta minutes between two timestamps
    const msToMinutes = 1 / (1000 * 60);
    let minutesDelta = function (t1, t2) {
        let deltaMs = Math.abs (conditionTime(t1) - conditionTime (t2));
        let deltaMinutes = deltaMs * msToMinutes;
        return deltaMinutes;
    };

    // a source data array might not have any data in it for some time periods, for
    // instance if the server was offline during the data collection. we split such an
    // array into multiple arrays rather than try to correlate them
    let splitSource = function (source) {
        // the expected gap is about 10 seconds, so we will look for gaps bigger than
        // 15 seconds, or 0.25 minutes
        let maxGap = 0.25;
        let sources = [];

        let start = 0;
        for (let i = 1; i < source.length; ++i) {
            if (minutesDelta(source[i].timestamp, source[i - 1].timestamp) > maxGap) {
                sources.push (source.slice (start, i));
                start = i;
            }
        }
        sources.push (source.slice (start, source.length));

        // return the result
        return sources;
    };

    // all of our samples are being conducted in 10 second intervals
    const responsesPerMinute = 6;
    const graphHours = 3;
    const graphMinutes = graphHours * 60;

    // set plot colors to repeat correctly
    let colors = ["rgb(114,147,203)", "rgb(132,186,91)", "rgb(225,151,76)"];

    let nowTime = Date.now(); //response[0].timestamp;
    let nowDate = new Date (nowTime);
    document.getElementById("div-time").innerText = nowDate.toLocaleDateString() + " " + nowDate.toLocaleTimeString();

    let digestSource = function (source, key) {
        let dataSet = [];

        // trim the source to be only full minutes in length
        source.length -= source.length % responsesPerMinute;

        // loop over the array in minute long chunks
        for (let i = 0, end = Math.min(source.length / responsesPerMinute, graphMinutes); i < end; ++i) {
            let offset = i * responsesPerMinute;
            let minute = source.slice(offset, offset + responsesPerMinute);
            let average = minute.reduce(function (total, current) {
                return {
                    x: total.x + (minutesDelta(current.timestamp, nowTime) / responsesPerMinute),
                    y: total.y + (current[key] / responsesPerMinute)
                }
            }, {x: 0, y: 0});
            if (average.x < graphMinutes) {
                dataSet.push(average);
            } else {
                break;
            }
        }

        return dataSet;
    };

    let makeWheel = function (average, value, min, max, minColor = "#080", maxColor = "#800", zeroColor = "#008") {

        // compute the color of the ring
        let color1 = computeColor (average, min, max, minColor, maxColor, zeroColor);
        let color2 = computeColor (value, min, max, minColor, maxColor, zeroColor);

        let addNumber = function (builder, size1, size2, dy1, dy2, width1, width2, spacing, baseline, value, color) {
            value = Math.round (value * 10) / 10;
            let v1 = Math.floor (value);
            let v2 = Math.floor ((value - v1) * 10);

            // determined roughly by experimentation
            let overallWidth = (width1 * v1.toString ().length) + 1.33 * (spacing + width2);
            let right = (overallWidth / 2) - (spacing + width2);

            return builder
                //.add ("http://www.w3.org/2000/svg;line", { attributes: { x1: -0.65, y1: baseline, x2: 0.65, y2: baseline, "stroke-width": 0.025, stroke: "#ddd" } })
                .add ("http://www.w3.org/2000/svg;text", { attributes: { x: right, y: baseline, dy: dy1, fill: color, "font-family": "Helvetica, Arial", "font-size": size1, "text-anchor": "end" }, innerHTML: v1 })
                .add ("http://www.w3.org/2000/svg;text", { attributes: { x: right + spacing, y: baseline, dy: dy2, fill: color, "font-family": "Helvetica, Arial", "font-size": size2, "text-anchor": "start" }, innerHTML: v2 })
        };

        let radius = 0.96;
        let builder = Html
            .begin("div", { style: { width: "100%", margin: "0" } })
                .begin ("http://www.w3.org/2000/svg;svg", { attributes: { width: "100%", viewBox: "-1 -1 2 2" },  style: { margin: "0", display: "block" } })
                    .add ("http://www.w3.org/2000/svg;path", { attributes: { d: "M " + radius + " 0 a " + radius + " " + radius + " 0 0 0 -" + (radius * 2) + " 0", fill: color1 } })
                    .add ("http://www.w3.org/2000/svg;path", { attributes: { d: "M -" + radius + " 0 a " + radius + " " + radius + " 0 0 0 " + (radius * 2) + " 0", fill: color2 } })
                    .add ("http://www.w3.org/2000/svg;circle", { attributes: { cx: 0, cy: 0, r: radius, stroke: "#444", "stroke-width": 0.025, fill: "none" } })
                    .add ("http://www.w3.org/2000/svg;circle", { attributes: { cx: 0, cy: 0, r: radius * 0.75, stroke: "#444", "stroke-width": 0.025, fill: "white" } })
                    //.add ("http://www.w3.org/2000/svg;line", { attributes: { x1: -0.65, y1: 0, x2: 0.65, y2: 0, "stroke-width": 0.025, stroke: "#ddd" } });
                    .add ("http://www.w3.org/2000/svg;line", { attributes: { x1: -0.5, y1: 0.3, x2: 0.5, y2: 0.3, "stroke-width": 0.025, stroke: "#ddd" } });
        addNumber (builder, 0.3, 0.2, "5%", "3%", 1 / 5, 1 / 6, 0.025, -0.425, average, "#666")
        return addNumber (builder, 0.65, 0.4, "12%", "7%",1 / 2.75, 1 / 4.5, 0.05, 0, value, "black")
                .end ()
            .end ();
    };

    let computeAverage = function (data, timePeriod) {
        let redux = data.reduce ( function (redux, value) {
            if ((value.x < timePeriod) && (value.y > 0)) {
                redux.sum += value.y;
                redux.count++;
            }
            return redux;
        }, { sum: 0, count: 0 } );
        return (redux.count > 0) ? (redux.sum / redux.count) : 0;
    };

    const sensorDataSourceUrl = "history.json";
    Bedrock.Http.get(sensorDataSourceUrl, (response) => {
        // the first element is always (timestamp: 0)
        response.shift ();

        // the times need to be expressed as minutes ago, so we start by reversing the
        // input data to make the first sample be the latest one
        response.reverse ();
        if (response.length > 0) {

            // look at the first record to build a list of the values we want to generate graphs of
            let keys = [];
            for (let key of Object.keys(response[0])) {
                if (key !== "timestamp") {
                    if (key.indexOf("-") < 0) {
                        keys.push(key);
                    }
                }
            }

            // loop over the keys
            if (keys.length > 0) {
                // each graph should end up in a display like this
                // <div class="widthOuterShell">
                //   <div class="wheelPlotOuterShell">
                //     <div class="wheelPlotInnerShell">
                //       <div class="wheelDiv">
                //         <div class="wheelDivInterior" id="plot-wheel"></div>
                //       </div>
                //       <div class="chartDiv" id="plot-chart"></div>
                //     </div>
                //   </div>
                // </div>
                let plotContainer = document.getElementById("plotContainer");

                for (let key of keys) {
                    // create the document structure mentioned above
                    let plotInnerShell = Html
                        .begin("div", { class: "widthOuterShell" })
                        .begin("div", { class: "wheelPlotOuterShell" })
                        .begin("div", { class: "wheelPlotInnerShell" });

                    // create the data set to display
                    let sources = splitSource(response);
                    let dataSets = [];

                    // loop over all of the source sets
                    for (let source of sources) {
                        let dataSet = digestSource(source, key);
                        if (dataSet.length > 0) {
                            dataSets.push(dataSet.map(a => ({x: a.x, y: a.y / 1000})));
                        }
                    }

                    // add two data sets to set a range
                    /*
                    dataSets.push([{x: 0, y: 48}]);
                    dataSets.push([{x: 0, y: 62}]);
                    */

                    // create the wheel element
                    let wheelDivElement = document.getElementById("plot-wheel");
                    wheelDivElement.innerHTML = "";
                    let average = computeAverage(dataSets[0], 30);
                    wheelDivElement.appendChild(makeWheel(average, dataSets[0][0].y, 45, 85));

                    // create the actual plot
                    let svg = PlotSvg
                        .setColors(colors)
                        .setPlotPoints(false)
                        .multipleLine(key, "Time (minutes ago)", response[0][key + "-unit"], dataSets);

                    // add the graph
                    document.getElementById("plot-chart").innerHTML = svg;
                }
            }
        }
    });

    // refresh at the beginning of every minute
    var now = new Date();
    var delay = 60 * 1000;
    var start = delay - (now.getSeconds()) * 1000 + now.getMilliseconds();

    setTimeout(refresh, start);
}

refresh ();

