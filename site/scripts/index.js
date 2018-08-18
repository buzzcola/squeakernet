(function(){ 
    window.index = {
        'init': function() {
            var i = 0;
            for (const stat of ['cpu', 'temp', 'weight', 'lastFeed']) {
                window.setTimeout(function(){
                    window.setInterval(function() { getStat(stat) }, 5000);
                }, i++ * 500);                
            }            
        }
    };
    
    function getStat(route, target){
        var selector = '#' + (target || route);
        $.ajax('/' + route)
        .done(function(data){
            $(selector).text(data);
        })
        .fail(function() {
            $(selector).text("<error>")
        });
    }

})();

$(index.init);
