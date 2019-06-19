// This is adapted from https://bl.ocks.org/mbostock/2675ff61ea5e063ede2b5d63c08020c7

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

function thickness(weight) {
    return Math.tan(weight)*3;
}

function mouseover(d) {

            d3.select(this).style("fill", "orange");

            var mousecoord = [0,0];
            mousecoord = d3.mouse(this);

            d3.select("#tooltip")
                .style("left", mousecoord[0] + "px")
                .style("top", mousecoord[1]-75 + "px");

            d3.select("#id")
                .text(d.id);

            d3.select("#tooltip").classed("hidden", false);
        };

function mouseout(d) {

            d3.select(this).style("fill", "#0e6ea5");
            d3.select("#tooltip")
                .style("left", "0px")
                .style("top", "0px");

            d3.select("#id")
                .text("Dar es Salaam");
            d3.select("#tooltip").classed("hidden", true);
        };

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }))
    .force("charge", d3.forceManyBody().distanceMax(30))
    .force("center", d3.forceCenter(width / 2, height / 2));

d3.json("force/cluster.json", function (error, graph) {
    if (error) throw error;

    var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", function d(d){return thickness(d.weight);});

    var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("r", 5)
        .attr("x", width / 2, height / 2)
        .attr("y", width / 2, height / 2)
        .on("mouseover", mouseover)
        .on("mouseout", mouseout)
        .call(d3.drag()
            .on("start", mouseover)
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", mouseout)
            .on("end", dragended));

    node.append("svg:title")
      .attr("dx", 12)
      .attr("dy", ".35em")
      .text(function(d) { return d.id });

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node
            .attr("cx", function (d) {
                return d.x = Math.max(6, Math.min(width - 6, d.x));;
            })
            .attr("cy", function (d) {
                return d.y = Math.max(6, Math.min(height - 6, d.y));;
            });
    }
});

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.5).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}