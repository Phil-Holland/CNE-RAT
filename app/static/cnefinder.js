$(function() {

    // hide error when the form gets changed
    $('#config-form').change(function() {
        $('#validation-error').slideUp(100);
    });

    /*
        ensembl site urls
    */
    $('#ensembl-site-ref').change(function() {
        $('#ref-site-val-error').slideUp(100);
        $('#ref-mart').slideUp(100);
        $('#ref-dataset').slideUp(100);
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
                $('#ref-mart').slideUp(100);
            } else {
                if (!url.trim()) {
                    $('#ref-mart').slideUp(100);
                } else {
                    $('#ref-mart').slideDown(100);
                    populate_mart_dropdown('#ref-mart-dropdown', data['content']);
                }
            }
        });
    });

    $('#ensembl-site-query').change(function() {
        $('#query-site-val-error').slideUp(100);
        $('#query-mart').slideUp(100);
        $('#query-dataset').slideUp(100);
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
                 $('#query-mart').slideUp(100);
            } else {
                if (!url.trim()) {
                    $('#query-mart').slideUp(100);
                } else {
                    $('#query-mart').slideDown(100);
                    populate_mart_dropdown('#query-mart-dropdown', data['content']);
                }
            }
        });
    });

    // This takes the dict returned from /check_url and iterates through kv pairs
    // to add <option> tags for each `visible` biomart found at the ensembl url
    function populate_mart_dropdown(dropdown, obj) {
        $(dropdown).empty();
        $.each(obj, function(key, value) {
            $(dropdown).append('<option value=' + key + '>' + value.displayName + '</option>');
        });
        document.querySelector(dropdown).value = '';
    }

    $('#ref-mart-dropdown').change(function() {
        var mart = this.value;
        var url = $('#ensembl-site-ref').val();
        if (mart !== '') {
            populate_dataset_dropdown('#ref-dataset-dropdown', url, mart);
        }
    }).change();

    $('#query-mart-dropdown').change(function() {
        var mart = this.value;
        var url = $('#ensembl-site-query').val();
        if (mart !== '') {
            populate_dataset_dropdown('#query-dataset-dropdown', url, mart);
        }
    }).change();

    // Makes the necessary ajax call to /find_datasets to populate a dropdown
    // after a mart has been selected ny the site user
    function populate_dataset_dropdown(dropdown, url, selected_mart) {
        $(dropdown).empty();
        $.ajax({
			url: '/find_datasets',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({'url': url, 'mart': selected_mart}),
            contentType:"application/json; charset=UTF-8"
        })
        .done(function(data) {
            if (!data['success']) {
                $(dropdown).parent().slideUp(100);
                // Not sure how this could fail - maybe display an unexpected `warning` box?
            } else {
                $(dropdown).parent().slideDown(100); // make dropdown visible
                $.each(data['content'], function(key, value) {
                    $(dropdown).append('<option title=' + key + '>' + value.description + '</option>');
                });
            }
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

    // default to using index position search
    $(document).ready(function(){
        $('#gene-name-config').slideUp(100);
    });

    $('#task-index-position').click(function() {
        if($(this).prop('checked')) {
            $('#index-position-config').slideDown(100);
            $('#task-gene-name').prop('checked', false);
            $('#gene-name-config').slideUp(100);
        }
        else $('#index-position-config').slideUp(100);
    });

    /*
        submit button
    */
    $('#config-form').submit(function(e) {
        e.preventDefault();

        // get form data, and attempt to build config object
        config = {
            'ensembl_request_config': {
                'ref_site': $('#ensembl-site-ref').val(),
                'query_site': $('#ensembl-site-query').val(),
                'ref_mart': $('#ref-mart-dropdown option:selected').val(),
                'query_mart': $('#query-mart-dropdown option:selected').val(),
                'ref_dataset': $('#ref-dataset-dropdown option:selected').val(),
                'query_dataset': $('#query-dataset-dropdown option:selected').val(),

            },
            'general_config': {
                'min_cne_length': $('#min-cne-length').val(),
                'sim_threshold': $('#sim-threshold').val(),
            },
            'gene_name': $('#task-gene-name').is(':checked'),
            'gene_name_config': {
                'ref_gene_name': $('#ref-gene-name').val(),
                'query_gene_name': $('#query-gene-name').val(),
            },
            'index_position': $('#task-index-position').is(':checked'),
            'index_position_config': {
                'ref_chromosome': $('#ref-chromosome').val(),
                'ref_start_pos': $('#ref-start-pos').val(),
                'ref_end_pos': $('#ref-end-pos').val(),
                'query_chromosome': $('#query-chromosome').val(),
                'query_start_pos': $('#query-start-pos').val(),
                'query_end_pos': $('#query-end-pos').val(),
            }
        }

        // use JSON schema to perform client-side validation on the JSON object
        var valid = validate(config);
        if(!valid) {
            // validation errors encountered!
            console.log(validate.errors);

            $('#validation-error').slideDown(100);

            // don't send the form
            return false;
        }

        // send POST request to start CNEFinder pre-prep and run
        $.post('/new_cnefinder', JSON.stringify(config), function(data) {
            if(data['success']) {
                window.location.replace("/output/" + data.uid);
            }
        }, "json");

        return false;
    });

});
