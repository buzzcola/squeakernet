(function(){ 
    var errorText = '<error>'

    window.index = {
        'init': function() {           
            initWeightGauge();
            initCpuGauge();
            initTempGauge();

            var i = 0;
            for (const stat of ['lastFeed']) {
                getStat(stat);
                window.setTimeout(function(){
                    window.setInterval(function() { getStat(stat) }, 5000);
                }, i++ * 500);                
            }

            $('#feed-button').click(feed);
        }
    };

    function initWeightGauge() {

        var weightGauge = new JustGage({
            id: "weightGauge",
            value: 0,
            min: 0,
            max: 75,
            symbol: 'g',
            title: 'Kibbles'
          });

        refreshWeightGauge = function() {
            $.ajax('/api/weight')
            .done(function(data){
                result = JSON.parse(data);
                weightGauge.refresh(+result.reading);
            });
        }

        window.setInterval(refreshWeightGauge, 5000);
        refreshWeightGauge();
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

    function feed() {
        if(!confirm('Dispense food now?')) return;

        $.ajax({
            method: 'POST',
            url: '/api/feed'
        });
    }

    function getStat(route, target){
        var selector = '#' + (target || route);
        $.ajax('/api/' + route)
        .done(function(data){
            if(selector == '#lastFeed') {
                // special: humanize last feed date.
                var humanized = moment(data).fromNow();
                $(selector).text(humanized);
                $(selector).attr('title', data);
            } else {
                $(selector).text(data);
            }
        })
        .fail(function() {
            $(selector).text("<error>")
        });
    }

})();

$(index.init);
