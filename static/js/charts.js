$( document ).ready(function() {
    var data = {
        labels: years_charts_labels,
        datasets: [
            {
                label: "My First dataset",
                fillColor: "rgba(142,168,191,0.2)",
                strokeColor: "rgba(142,168,191,1)",
                pointColor: "rgba(142,168,191,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(142,168,191,1)",
                data: years_charts_same
            },
            {
                label: "My Second dataset",
                fillColor: "rgba(39,204,119,0.2)",
                strokeColor: "rgba(39,204,119,1)",
                pointColor: "rgba(39,204,119,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(39,204,119,1)",
                data: years_charts_new
            },
            {
                label: "My Third dataset",
                fillColor: "rgba(242,87,87,0.2)",
                strokeColor: "rgba(242,87,87,1)",
                pointColor: "rgba(242,87,87,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(242,87,87,1)",
                data: years_charts_lost
            }
        ]
    };

    // Define default option for line chart
	var options = {
		scaleOverlay : false,
		scaleOverride : false,
		scaleSteps : null,
		scaleStepWidth : null,
		scaleStartValue : null,
		scaleLineColor : "rgba(0,0,0,.1)",
		scaleLineWidth : 1,
		scaleShowLabels : true,
		scaleLabel : "<%=value%>",
		scaleFontFamily : "'proxima-nova'",
		scaleFontSize : 10,
		scaleFontStyle : "normal",
		scaleFontColor : "#909090",
		scaleShowGridLines : true,
		scaleGridLineColor : "rgba(0,0,0,.05)",
		scaleGridLineWidth : 1,
		bezierCurve : true,
		pointDot : true,
		pointDotRadius : 3,
		pointDotStrokeWidth : 1,
		datasetStroke : true,
		datasetStrokeWidth : 2,
		datasetFill : true,
		animation : true,
		animationSteps : 60,
		animationEasing : "easeOutQuart",
		onAnimationComplete : null
	}
    function draw() {
        $("#myChart").attr( 'width', $("#two").innerWidth()+'px' );
        //Get the context of the canvas element we want to select
        var ctx = document.getElementById("myChart").getContext("2d");
        myNewChart = new Chart(ctx).Line(data, options);
    }
    $(window).on('load', function() { draw(); });
    $(window).resize( draw );
});

