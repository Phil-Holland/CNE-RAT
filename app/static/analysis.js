// main script file for the analysis results page

var last_statuses = null;

$(function() {
    
    // populate sidebar tool list
    function add_tool(title, name, id) {
        $('#analysis-sidebar-list').append(
            '<li data-tool=' + id + ' data-name="' + name + '" data-active=false class=\'tool-link\'>' + title + '</li>'
        );
        $('#task-content').append(
            '<div id="content-' + name + '" style="display: none"></div>'
        );
    }

    console.log(config);

    if("task_rna_protein" in config && config["task_rna_protein"] == true) {
        add_tool("RNA-protein interaction analysis tool", "rnaprotein", 1);
    }
    if("task_rna_rna" in config && config["task_rna_rna"] == true) {
        add_tool("RNA-RNA interaction analysis - ViennaRNA", "viennarna", 2);
        add_tool("RNA-RNA interaction analysis - IntaRNA", "intarna", 3);
    }
    $('#analysis-sidebar-list > li:first').attr('data-active', true);
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
                    if(el.status == 'FAILURE') {
                        overall_status = 'FAILURE';
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