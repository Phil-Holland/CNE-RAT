$(function() {

    // hide error when the form gets changed
    $('#config-form').change(function() {
        $('#validation-error').slideUp(100);
    });

    /*
        ensembl site urls
    */
    // hide mart and dataset select divs on page load
    $(document).ready(function(){
        $('#ref-dataset').slideUp(100);
        $('#query-dataset').slideUp(100);
    });


    $('#ensembl-site-ref').change(function() {
        $('#ref-site-val-error').slideUp(100);
    });

    $('#ensembl-site-ref').focusout(function() {
        var url = $(this).val();
        $.ajax({
			url: '/check_url',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'url': url}),
            contentType:"application/json; charset=UTF-8"
        })
        .done(function(data) {
            if (!data['success']) {
                $('#ref-site-val-error').slideDown(100);
                $('#ref-dataset').slideUp(100);
            } else {
                if (!url.trim()) {
                    $('#ref-dataset').slideUp(100);
                } else {
                    $('#ref-dataset').slideDown(100);
                    populate_mart_dropdown('#ref-dataset-dropdown', data['content'])
                }
            }
        });
    });

    $('#ensembl-site-query').change(function() {
        $('#query-site-val-error').slideUp(100);
    });

    $('#ensembl-site-query').focusout(function() {
        var url = $(this).val();
        $.ajax({
			url: '/check_url',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'url': url}),
            contentType:"application/json; charset=UTF-8"
        })
        .done(function(data) {
            if (!data['success']) {
                 $('#query-site-val-error').slideDown(100);
                 $('#query-dataset').slideUp(100);
            } else {
                if (!url.trim()) {
                    $('#query-dataset').slideUp(100);
                } else {
                    $('#query-dataset').slideDown(100);
                    populate_mart_dropdown('#query-dataset-dropdown', data['content'])
                }
            }
        });
    });

    function populate_mart_dropdown(dropdown, obj) {
        $(dropdown).empty()
        $.each(obj, function(key, value) {
            $(dropdown).append('<option>' + value.displayName + '</option>');
        });
    }

    /*
        task checkboxes
    */
    $('#task-gene-name').click(function() {
        if($(this).prop('checked')) {
            $('#gene-name-config').slideDown(100);
            $('#task-index-position').prop('checked', false);
            $('#index-position-config').slideUp(100);
        }
        else $('#gene-name-config').slideUp(100);
    });

    // default to using gene name search
    $(document).ready(function(){
        $('#index-position-config').slideUp(100);
    });

    $('#task-index-position').click(function() {
        if($(this).prop('checked')) {
            $('#index-position-config').slideDown(100);
            $('#task-gene-name').prop('checked', false);
            $('#gene-name-config').slideUp(100);
        }
        else $('#index-position-config').slideUp(100);
    });

});
