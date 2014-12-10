$( document ).ready(function() {
    var dataYearlyBirthdays = {
        labels: years_charts_labels,
        datasets: [
            {
                label: "Same (wished last year)",
                fillColor: "rgba(142,168,191,0.2)",
                strokeColor: "rgba(142,168,191,1)",
                pointColor: "rgba(142,168,191,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(142,168,191,1)",
                data: years_charts_same
            },
            {
                label: "New (didn't wish last year)",
                fillColor: "rgba(39,204,119,0.2)",
                strokeColor: "rgba(39,204,119,1)",
                pointColor: "rgba(39,204,119,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(39,204,119,1)",
                data: years_charts_new
            },
            {
                label: "Lost (wished last year but not this year)",
                fillColor: "rgba(242,87,87,0.2)",
                strokeColor: "rgba(242,87,87,1)",
                pointColor: "rgba(242,87,87,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(242,87,87,1)",
                data: years_charts_lost
            },
            {
                label: "Total wishes",
                fillColor: "rgba(122,87,87,0.2)",
                strokeColor: "rgba(122,87,87,1)",
                pointColor: "rgba(122,87,87,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(122,87,87,1)",
                data: years_charts_all,
                segmentStrokeWidth: "5"
            }
        ]
    };

    var dataWordsUsed = {
        labels: word_chart_labels,
        datasets: [
            {
                label: "My First dataset",
                fillColor: "rgba(39,204,119,0.5)",
                strokeColor: "rgba(39,204,119,0.8)",
                highlightFill: "rgba(39,204,119,0.75)",
                highlightStroke: "rgba(39,204,119,1)",
                data: word_chart_count
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
		onAnimationComplete : null,
        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].lineColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
	}

    function draw() {
        /* Yearly Birthdays */
        $("#yearlyBirthdays").attr( 'width', $("#two").innerWidth()+'px' );
        //Get the context of the canvas element we want to select
        var ctxYearlyBirthdays = document.getElementById("yearlyBirthdays").getContext("2d");
        yearlyBirthdays = new Chart(ctxYearlyBirthdays).Line(dataYearlyBirthdays, options);
        yearlyBirthdays.generateLegend();

        /* Words used */
        $("#wordsUsed").attr( 'width', $("#two").innerWidth()+'px' );
        //Get the context of the canvas element we want to select
        var ctxWordsUsed = document.getElementById("wordsUsed").getContext("2d");
        wordsUsed = new Chart(ctxWordsUsed).Bar(dataWordsUsed, options);
    }
    $(window).on('load', function() { draw(); });
    $(window).resize( draw );
});

