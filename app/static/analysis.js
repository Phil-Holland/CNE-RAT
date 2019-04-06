// main script file for the analysis results page

var last_statuses = null;

$(function() {
    
    // populate sidebar tool list
    function add_tool(title, name, id) {
        $('#analysis-sidebar-list').append(
            '<div class=\'row\'>' +
            '<div class=\'column column-10\'>' +
            '<i id=\'tool-icon-' + name + '\' class=\'material-icons\'>hourglass_empty</i>&nbsp;' +
            '</div>' +
            '<div class=\'column column-90\'>' +
            '<li data-tool=' + id + ' data-name="' + name + '" data-active=false class=\'tool-link\'>' + title + '</li>' +
            '</div>' +
            '</div>'
        );
        $('#task-content').append(
            '<div id="content-' + name + '" style="display: none"></div>'
        );
    }

    if('task_rna_protein' in config && config['task_rna_protein'] == true) {
        add_tool('RNA-protein interaction analysis tool', 'protein', 1);
    }
    if('task_rna_rna' in config && config['task_rna_rna'] == true) {
        var pipeline = config['task_rna_rna_config']['rna_rna_pipeline'];
        if(pipeline == 'vienna' || pipeline == 'both')
            add_tool('RNA-RNA interaction analysis - ViennaRNA', 'viennarna', 2);
        if(pipeline == 'inta' || pipeline == 'both')
            add_tool('RNA-RNA interaction analysis - IntaRNA', 'intarna', 3);
    }
    $('#analysis-sidebar-list li:first').attr('data-active', true);
    $('#task-content > div:first').show();

    // when a specific tool output has been clicked
    $('.tool-link').click(function() {
        if($(this).attr('data-active') == 'false') {
            $('.tool-link').each(function() {
                $(this).attr('data-active', false);
                $('#content-' + $(this).attr('data-name')).hide();
            });
            $(this).attr('data-active', true);
            $('#content-' + $(this).attr('data-name')).show();
        }
    });

    // when the 'show configuration' toggle has been clicked
    $('#config-toggle').click(function() {
        if($("#config").is(':visible')) {
            $("#config").slideUp();
            $('#config-toggle').html("Show analysis configuration")
        } else {
            $("#config").slideDown();
            $('#config-toggle').html("Hide analysis configuration")
        }
    });

    update();
});

var update_content = function(tid, name) {
    $.post('/get_task_data/' + tid, function(t_data) {
        t_data = JSON.parse(t_data);

        if(t_data.success) {
            $('#content-' + name).html(t_data.result);
        }
    });
}

var failure_text = 'Unfortunately, this tool has failed to complete successfully.';

var update = function() {
    // get task status from flask
    $.post('/get_analysis_status/' + uid, function(data) {
        data = JSON.parse(data);
        if(data.success) {
            console.log(data);
            // if statuses have changed, update everything
            if(last_statuses != data.statuses) {
                var overall_status = 'COMPLETED';
                for (var i = 0; i < data.statuses.length; i++) {
                    var el = data.statuses[i];
                    $('#tool-icon-' + el.name).html('hourglass_empty');

                    if(el.status == 'FAILURE') {
                        overall_status = 'FAILURE';
                        $('#tool-icon-' + el.name).html('close');
                        $('#tool-icon-' + el.name).css('color', 'red');
                        $('#tool-icon-' + el.name).css('font-weight', 'bold');

                        $('#content-' + el.name).html(failure_text);
                    } else if(el.status == 'STARTED' || 
                        el.status == 'RECEIVED' || 
                        el.status == 'PENDING') {
                        overall_status = 'PROCESSING';
                    } else if(el.status != 'SUCCESS') {
                        el.status = 'UNKNOWN';
                    } else {
                        // task completed successfully
                        if(last_statuses == null || last_statuses[i].status != 'SUCCESS') {
                            update_content(el.id, el.name);
                        }
                        $('#tool-icon-' + el.name).html('done');
                        $('#tool-icon-' + el.name).css('color', 'green');
                    }
                }
                $('#status').html(overall_status);

                last_statuses = data.statuses;
            }
        }

        // check again after 10 seconds
        setTimeout(update, 10000);
    });
}