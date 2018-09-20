(function(){ 
    var errorText = '<error>'

    window.index = {
        'init': function() {           
            initWeightGauge();
            initCpuGauge();
            initTempGauge();
            initLastFeed();
            initLineChart();

            $('#feed-button').click(feed);
        }
    };

    function initWeightGauge() {

        $.ajax('/api/config/dispenser/desired_grams')
        .done(function(weightString){
            var maxWeight = parseFloat(weightString);
            var weightGauge = new JustGage({
                id: "weightGauge",
                value: 0,
                min: 0,
                max: maxWeight,
                symbol: 'g',
                title: 'Kibbles',
                levelColors: ["#ff0000", "#f9c802", "#a9d70b"]
            });

            var refreshWeightGauge = function() {
                $.ajax('/api/weight')
                .done(function(data){
                    result = JSON.parse(data);
                    weightGauge.refresh(Math.max(+result.reading, 0));
                });
            }

            window.setInterval(refreshWeightGauge, 5000);
            refreshWeightGauge();    
        });
    }

    function initCpuGauge() {

        var cpuGauge = new JustGage({
            id: "cpuGauge",
            value: 0,
            min: 0,
            max: 100,
            symbol: '%',
            title: 'CPU Utilization'
          });

        refreshCpuGauge = function() {
            $.ajax('/api/cpu')
            .done(function(data){
                cpuGauge.refresh(+data);
            });
        }

        window.setInterval(refreshCpuGauge, 5000);
        refreshCpuGauge();
    }

    function initTempGauge() {

        var gauge = new JustGage({
            id: "tempGauge",
            value: 0,
            decimals: 1,
            min: 10,
            max: 85,
            symbol: '°',
            title: "CPU Temperature"
          });

        refresh = function() {
            $.ajax('/api/temp')
            .done(function(data){
                gauge.refresh(+data);
            });
        }

        window.setInterval(refresh, 5000);
        refresh();
    }

    function initLastFeed() {

        var refresh = function() {
            var lastFeedSelector = '#lastFeed';
            var feedAmountselector = '#feedAmount';

            $.ajax('/api/lastFeed')
            .done(function(data){
                var result = JSON.parse(data);                
                var humanized = moment(result.date).fromNow();
                $(lastFeedSelector).text(humanized);
                $(lastFeedSelector).attr('title', result.date);
                $(feedAmountselector).text(Math.round(result.reading));
            })
            .fail(function() {
                $(lastFeedSelector).text("<error>")
            });
        };
        
        refresh();
        window.setInterval(refresh, 5000);
    }

    function initLineChart(){
        $.ajax('/api/today')
            .done(function(data){
                var result = JSON.parse(data);
                // highcharts wants milliseconds since epoch. Also
                // smooth out the negatives.
                processed = result.map(function(pair) {
                    return [
                        +new Date(pair[0]), 
                        Math.max(Number.parseFloat(pair[1].toFixed(1)), 0)];
                });

                // avoid sloping lines - add a point ~1 minute before each point
                // to reflect the non-recorded weights in between.
                var filler = new Array(processed.length);
                for(var i = 0; i < processed.length - 1; i++) {
                    var current = processed[i];
                    var next = processed[i + 1];
                    filler[i] = [next[0] - 59999, current[1]];
                }
                // finally put in a point for right now with the last
                // recorded weight so the chart is up to date.
                var last = processed[processed.length - 1];
                filler[filler.length - 1] = [+new Date(), last[1]];

                var processedAndFilled = processed
                    .map(function(p,i) { return [p, filler[i]]; })
                    .reduce(function(a,b) { return a.concat(b); });
                
                renderLineChart(processedAndFilled);
            });
    }

    function renderLineChart(data) {

        Highcharts.chart('lineChart', {
            title: {
                text: "Today's feeding"
            },        
            yAxis: {
                title: {
                    text: 'Grams of Kibble in Bowl'
                }
            },
            xAxis: {
                type: 'datetime'
            },
            legend: {
                enabled: false
            },        
            time: {
                useUTC: false
            },
            series: [{
                type: 'area',
                name: 'Kibbles (g)',
                data: data
            }],
        });
    }

    function feed() {
        if(!confirm('Dispense food now?')) return;

        $.ajax({
            method: 'POST',
            url: '/api/feed'
        });
    }


})();

$(index.init);
