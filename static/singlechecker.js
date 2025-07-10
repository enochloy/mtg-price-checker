function titleCase(string) {
    return string[0].toUpperCase() + string.slice(1).toLowerCase();
}

$('input').on('change input', function() {
        // Get checked checkbox values
        var checkedValues = $('.form-check-input:checked').map(function() {
            return this.value;
        }).get();

        // Get search box value
        var searchBoxValue = $('.form-control').val();

        console.log('Checked values:', checkedValues);
        console.log('Search box value:', searchBoxValue);

        $.ajax({
            type: 'POST',
            url: '/singlesearcher',
            data: {
                'checkedValues': checkedValues,
                'searchBoxValue': searchBoxValue
        },
        success: function(response) {
            console.log('Success. Response:', response);
            var cardsData = JSON.parse(response);
            console.log(cardsData);
            // Clear existing table rows
            $('tbody').empty();
            // Populate the table with new data
            $.each(cardsData, function(index, card) {
                $('tbody').append('<tr><td>' + card.name + '</td><td>$' + card.price + '</td><td>' + titleCase(card.store) + '</td></tr>');
            });
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
});