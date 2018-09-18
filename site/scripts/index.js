(function(){ 
    var errorText = '<error>'

    window.index = {
        'init': function() {           
            initWeightGauge();
            initCpuGauge();
            initTempGauge();
            initLastFeed();

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

    function feed() {
        if(!confirm('Dispense food now?')) return;

        $.ajax({
            method: 'POST',
            url: '/api/feed'
        });
    }


})();

$(index.init);
