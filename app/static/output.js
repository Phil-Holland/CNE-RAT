// main script file for the CNEfinder results page

$(function() {
    update();
});

var update_content = function(tid, name) {
    $.post('/get_task_data/' + tid, function(t_data) {
        t_data = JSON.parse(t_data);

        if(t_data.success) {
            $('#task-content').html(t_data.result);
            $('#task-content').find('.dataframe').each(function(i) {
                $(this).addClass('display compact nowrap');
                $(this).DataTable({
                    paging: false,
                    "order": [[ 5, "desc" ]],
                    "sScrollX": "100%",
                    "sScrollXInner": "100%",
                    "bScrollCollapse": true,
                    "fixedColumns":   {
                       "leftColumns": 1
                    },
                    dom: 'Bfrtip',
                    buttons: {
                        dom: {
                            button: {
                                tag: 'button',
                                className: ''
                            }
                        },
                        buttons: [
                            {
                                extend: 'csv',
                                text: 'Export to csv file',
                                title: 'table',
                                className: 'export-button button button-outline'
                            }
                        ]
                    }
                });
            });
        }
    });
}

// when the 'show configuration' toggle has been clicked
$('#config-toggle').click(function() {
    if($("#config").is(':visible')) {
        $("#config").slideUp();
        $('#config-toggle').html("Show job configuration")
    } else {
        $("#config").slideDown();
        $('#config-toggle').html("Hide job configuration")
    }
});

var failure_text = 'Unfortunately, this tool has failed to complete successfully.';
var last_status = null;
var update = function() {
    // get task status from flask
    $.post('/get_cnefinder_status/' + uid, function(data) {
        data = JSON.parse(data);
        console.log(data);
        if(data.success) {
            // if status has changed, update everything
            if(last_status != data.statuses[0].status) {
                $('#status').html(data.statuses[0].status);
                if(data.statuses[0] == 'SUCCESS') {
                    update_content(data.statuses[0].id, data.statuses[0].name);
                } else if(data.statuses[0].status == 'FAILURE') {
                    $('#task-content').html(failure_text);
                }
                last_status = data.statuses[0].status
            }
        }
        // check again after 10 seconds
        setTimeout(update, 10000);
    });
}