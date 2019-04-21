function validate_fasta(fasta) {
    console.log(fasta);

    // remove any trailing spaces
    fasta = fasta.trim();

    // split into lines
    lines = fasta.split('\n');
    
    console.log(lines);

    // loop over lines, until a header is found
    var i = 0;
    var sequences = 0;
    while (i < lines.length) {
        if (lines[i][0] == '>') {
            console.log(lines[i]);
            console.log(lines[i+1]);
            // we have found a header! Validate the next line in the file
            if (lines[i+1].trim().search(/[^acgtu]/i) != -1) {   
                // the sequence contains unacceptable characters
                console.log('error');
                return false;
            }
            sequences++;
            i++; // skip 2 lines
        }
        i++;
    }

    // was at least one sequence found?
    if (sequences == 0) return false;

    // no errors, so return true
    return true;
}

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
        $('#fasta-error').slideUp(100);
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

        // use jquery.serializejson.js to serialise the configuration form
        var config = $('#config-form').serializeJSON({
            checkboxUncheckedValue: 'false'
        });

        // delete unnecessary bits from the config
        if(!config['rna_protein']) delete config['rna_protein_config'];

        if(!config['rna_rna']) {
            delete config['rna_rna_config'];
        } else {
            if(!config['rna_rna_config']['inta']) delete config['rna_rna_config']['inta_config'];

            if(!config['rna_rna_config']['vienna']) {
                delete config['rna_rna_config']['vienna_config'];
            } else {
                if(!config['rna_rna_config']['vienna_config']['rnaduplex']) 
                    delete config['rna_rna_config']['vienna_config']['rnaduplex_config']
            }
        }

        // use JSON schema to perform client-side validation on the JSON object
        var valid = validate(config);
        if(!valid) {
            // validation errors encountered!
            $('#validation-error').slideDown(100);

            // don't send the form
            return false;
        }

        // validate the fasta sequences
        if(!validate_fasta(config['cne']) || 
            !validate_fasta(config['rna_rna_config']['query_sequences'])) {
            
            // fasta errors encountered!
            $('#fasta-error').slideDown(100);

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