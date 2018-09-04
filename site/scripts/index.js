(function(){ 
    window.index = {
        'init': function() {
            var i = 0;
            for (const stat of ['cpu', 'temp', 'weight', 'lastFeed']) {
                getStat(stat);
                window.setTimeout(function(){
                    window.setInterval(function() { getStat(stat) }, 5000);
                }, i++ * 500);                
            }

            $('#feed-button').click(feed);
        }
    };
    
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
            $(selector).text(data);
        })
        .fail(function() {
            $(selector).text("<error>")
        });
    }

})();

$(index.init);
