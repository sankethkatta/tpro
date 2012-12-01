var button = $("#tweetinput button");
var tbody = $("#resultTable tbody");

$("#tweetinput").submit(function(e) {
    e.preventDefault();
    var query = $(this).serialize();
    button.attr("disabled", "disabled");
    button.html("Analyzing...");

    $.ajax({
        url: "/analyze",
        type: "POST",
        dataType: "JSON",
        data: query
    }).done(function(data) {
       buildTable(data); 
    });
});

var buildTable = function(data) {
    button.removeAttr("disabled");
    button.html("Analyze");
    tbody.children().remove()
    for (i = 0; i < data.length; i++) {
       tbody.append("<tr><td>"+data[i].industry+"</td><td>"+data[i].user+"</td><td>"+data[i].score+"</td></tr>");
    };
};


// Initialize the D3 Circle Space
var container = d3.select("#circles").append("svg")
    .attr("width", "100%")
    .attr("height", "400px");

container.selectAll("data-circles")
    .data([{"color": "steelblue", "cx": "100px"}, {"color": "red", "cx": "200px"}])
    .enter()
    .append("circle")
    .attr("class", "data-circles")
    .attr("cx", function(d) { return(d.cx); })
    .attr("cy", 80)
    .attr("r", 20)
    .style("stroke", "#d0d0d0")
    .style("fill", function(d) { return(d.color); })
    .transition().duration(500).attr("r", "40px");

var circles = container.selectAll(".data-circles")
container.append("svg:text")
    .attr("x", 10)
    .attr("dy", ".31em")
    .text("testing");

circles.on("mouseover", function() {
    d3.select(this).transition().duration(500).delay(0).style("stroke-width", "5px");
});
circles.on("mouseout", function() {
    d3.select(this).transition().duration(500).delay(0).style("stroke-width", "0px");
});
