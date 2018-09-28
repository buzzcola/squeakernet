$(function() {
    
    // This makes an efficient client-side case-insensitive filtering function for the filtering feature 
    // of the grid. Probably overkill. Only supports text fields.
    function makeFilterFunction(filter) {
        var filteredFields = Object.keys(filter).filter(function(key) { return !!filter[key] });
        var ciFilter = {};
        for(var i = 0; i < filteredFields.length; i++) {
            ciFilter[filteredFields[i]] = filter[filteredFields[i]].toLowerCase();
        }

        if(Object.keys(filteredFields).length === 0) {
            return function(record) { return true; }
        }

        return function(record) {
            for(var i = 0; i < filteredFields.length; i++) {
                if(record[filteredFields[i]].toLowerCase().indexOf(ciFilter[filteredFields[i]]) === -1) {
                    return false;
                } 
            }
            return true;
        }
    }

    $("#grid").jsGrid({
        fields: [
            { name: "id", type: "number", width: 0, visible: false },            
            { name: "date", title: "Date", type: "text", width: 100 },
            { name: "category", title: "Category", type: "text", width: 75 },
            { name: "message", title: "Message", type: "text", width: 200 },
            { name: "reading", title: "Reading", type: "number", width: 50, filtering: false, itemTemplate: function(value) { return value.toFixed(1); } },
            { type: "control", editButton: false, deleteButton: false }
        ],

        height: 'auto',
        width: '100%',
 
        filtering: true,
        sorting: true,
        paging: false,
        editing: false,
        autoload: true,
        
        controller: {
            loadData: function(filter) {
                var filterFunction = makeFilterFunction(filter);
                var d = $.Deferred();
 
                $.ajax({
                    url: "/api/logs",
                    dataType: "json"
                }).done(function(response) {
                    console.log(filter)
                    d.resolve(response.filter(filterFunction));
                });
 
                return d.promise();
            }
        }
    });
});