function titleCase(string) {
    return string[0].toUpperCase() + string.slice(1).toLowerCase();
}

$('button').on('click', function() {
    // Get textbox value
    var textArea = $('textarea').val().split('\n');
    console.log('Text Area:', textArea);

    // Get checked checkbox values
    var checkedValues = $('.form-check-input:checked').map(function() {
        return this.value;
    }).get();
    console.log('Checked values:', checkedValues);

    $.ajax({
        type: 'POST',
        url: '/decksearcher',
        data: {
            'textArea': textArea,
            'checkedValues': checkedValues
        },
        beforeSend: function() {
            $(".spinner-border").show();
        },
        success: function(response) {
            var cardsData = JSON.parse(response);
            
            createTables(cardsData);

        },
        error: function(error) {
            console.error('Error:', error);
        },
        complete: function() {
            $(".spinner-border").hide();
        }
    })
});

function createTables(cardsData) {
    var tablesContainer = $('#tablesContainer');
    tablesContainer.empty();  // Clear existing tables
    
    var stores = [...new Set(cardsData.map(card => card.store))];

    stores.forEach(function (store) {
        // Create a new table for each store
        var headerHtml = '<h2 class="mt-5">' + titleCase(store) + '</h2>';
        
        tablesContainer.append(headerHtml);
        
        var tableHtml = '<table class="table table-striped">' +
            '<thead>' +
            '<tr>' +
            '<th>Card Name</th>' +
            '<th>Price</th>' +
            '<th>Quantity</th>' +
            '<th>Total Cost</th>' +
            '</tr>' +
            '</thead>' +
            '<tbody id="tableBody-' + store.replaceAll(' ', '') + '">' +
            '</tbody>' +
            '</table>';

        tablesContainer.append(tableHtml);

        // Insert data into the corresponding table body
        var tableBody = $('#tableBody-' + store.replaceAll(' ', ''));
        var totalCost = 0;

        cardsData.forEach(function (card) {
            if ((card['store']) === store) {
                tableBody.append('<tr>' +
                    '<td>' + card['name'] + '</td>' +
                    '<td>' + card['price'] + '</td>' +
                    '<td>' + card['quantity'] + '</td>' +
                    '<td>' + (card['quantity'] * card['price']).toFixed(2) + '</td>' +
                    '</tr>');

                totalCost += card['quantity'] * card['price'];
            }
        });

    // Append the row for total cost
    tableBody.append('<tr class="table-info">' +
        '<td colspan="3"><strong>Total Cost</strong></td>' +
        '<td><strong>$' + totalCost.toFixed(2) + '</strong></td>' +
        '</tr>');           
    });
}