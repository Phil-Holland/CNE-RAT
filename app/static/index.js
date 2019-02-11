$(function() {    
    // upload data
    $('input[type=file]').on('change', function(e) {
        var target_id = '#' + $(this).attr('data-target');
        var file = $(this).prop('files')[0];

        var read = new FileReader();
        read.readAsBinaryString(file);
        
        read.onloadend = function() {
            $(target_id).val(read.result);
        }
    });

    // task checkboxes
    $('#task-rna-protein').click(function() {
        if($(this).prop('checked')) {
            $('#rna-protein-config').slideDown(100);
        } else {
            $('#rna-protein-config').slideUp(100);
        }
    });

    $('#task-rna-rna').click(function() {
        if($(this).prop('checked')) {
            $('#rna-rna-config').slideDown(100);
        } else {
            $('#rna-rna-config').slideUp(100);
        }
    });


    // email checkbox
    $('#email-check').click(function() {
        $('#email').prop('disabled', !($(this).prop('checked')));
    });

    $('#config-form').submit(function(e) {
        e.preventDefault();

        // get form data, and build js config object
        config = {};
        config['cne'] = $('#cne').val();

        config['task_rna_protein'] = $('#task-rna-protein').is(":checked");
        config['task_rna_rna'] = $('#task-rna-rna').is(":checked");

        config['task_rna_protein_config'] = {};
        config['task_rna_rna_config'] = {};

        // add values from task config div
        $('#rna-protein-config').children().each(function() {
            config['task_rna_protein_config'][$(this).prop('name')] = 
                $(this).val();
        });
        $('#rna-rna-config').children().each(function() {
            config['task_rna_rna_config'][$(this).prop('name')] = 
                $(this).val();
        });
        
        config['send_email'] = $('#email-check').is(":checked");
        config['email'] = $('#email').val();

        console.dir(config);

        // TODO: client-side validation

        // send POST request to start analysis
        $.post('/new_analysis', JSON.stringify({
            config: config
        }), function(data) {
            if(data['success']) {
                window.location.replace("/analysis/" + data.uid);
            }
        }, "json");

        return false;
    });
});