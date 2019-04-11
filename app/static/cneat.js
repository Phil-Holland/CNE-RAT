$(function() {
    // upload data
    $('fieldset, .rna-rna-query-sequence').on('change', 'input[type=file]', function(e) {
        var target_id = '#' + $(this).attr('data-target');
        var file = $(this).prop('files')[0];

        var read = new FileReader();
        read.readAsBinaryString(file);

        read.onloadend = function() {
            $(target_id).val(read.result);
        }
    });

    // hide error when the form gets changed
    $('#config-form').change(function() {
        $('#validation-error').slideUp(100);
    });

    // task checkboxes
    $('#task-rna-protein').click(function() {
        if($(this).prop('checked')) $('#rna-protein-config').slideDown(100);
        else $('#rna-protein-config').slideUp(100);
    });

    $('#task-rna-rna').click(function() {
        if($(this).prop('checked')) $('#rna-rna-config').slideDown(100);
        else $('#rna-rna-config').slideUp(100);
    });

    $('#run-vienna').click(function() {
        if($(this).prop('checked')) $('#vienna-config').slideDown(100);
        else $('#vienna-config').slideUp(100);
    });

    $('#run-inta').click(function() {
        if($(this).prop('checked')) $('#inta-config').slideDown(100);
        else $('#inta-config').slideUp(100);
    });

    $('#run-rnaduplex').click(function() {
        if($(this).prop('checked')) $('#rnaduplex-config').slideDown(100);
        else $('#rnaduplex-config').slideUp(100);
    });

    $('#run-rnacofold').click(function() {
        if($(this).prop('checked')) $('#rnacofold-config').slideDown(100);
        else $('#rnacofold-config').slideUp(100);
    });

    $('#config-form').submit(function(e) {
        e.preventDefault();

        // get form data, and attempt to build config object
        config = {
            'cne': $('#cne').val(),
            'rna_protein': $('#task-rna-protein').is(':checked'),
            'rna_protein_config': {
                'drosophila_melanogaster': $('#species-drosophila').is(':checked'),
                'homo_sapiens': $('#species-homo').is(':checked'),
                'mus_musculus': $('#species-mus').is(':checked')
            },
            'rna_rna': $('#task-rna-rna').is(':checked'),
            'rna_rna_config': {
                'query_sequences': $('#query-sequences').val(),
                'vienna': $('#run-vienna').is(':checked'),
                'vienna_config': {
                    'rnaduplex': $('#run-rnaduplex').is(':checked'),
                    'rnaduplex_config': {
                        'deltaenergy': parseFloat($('#rnaduplex-deltaenergy').val())
                    },
                    'rnacofold': $('#run-rnacofold').is(':checked'),
                    'rnacofold_config': {}
                },
                'inta': $('#run-inta').is(':checked'),
                'inta_config': {}
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

        // send POST request to start analysis
        $.post('/new_analysis', JSON.stringify(config), function(data) {
            if(data['success']) {
                window.location.replace("/analysis/" + data.uid);
            }
        }, "json");

        return false;
    });
});
