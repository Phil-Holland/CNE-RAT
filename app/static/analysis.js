// main script file for the analysis results page

var last_statuses = null;
var scrolls = {};
var failure_text = 'Unfortunately, this tool has failed to complete successfully.';

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
            '<div id="content-' + name + '" class="task" style="display: none"></div>'
        );
    }

    if(config['rna_protein'] == true) {
        add_tool('RNA-protein interaction analysis tool', 'protein', 1);
    }
    if(config['rna_rna'] == true) {
        if(config['rna_rna_config']['vienna'])
            add_tool('RNA-RNA interaction analysis - ViennaRNA', 'viennarna', 2);
        if(config['rna_rna_config']['inta'])
            add_tool('RNA-RNA interaction analysis - IntaRNA', 'intarna', 3);
    }
    $('#analysis-sidebar-list li:first').attr('data-active', true);
    $('#task-content > div:first').show();

    // when a specific tool output has been clicked
    $('.tool-link').click(function() {
        if($(this).attr('data-active') == 'false') {
            var el = this;
            $('.tool-link').each(function() {
                if($(this).attr('data-active') == 'true') {
                    $(this).attr('data-active', false);
                    scrolls[$(this).attr('data-name')] = $(document).scrollTop();
                    $('#content-' + $(this).attr('data-name')).hide();
                }
            }).promise().done(function() {
                $(el).attr('data-active', true);
                $('#content-' + $(el).attr('data-name')).show();
                $('#content-' + $(el).attr('data-name')).find('table').each(function(i) {
                    $(this).resize();
                });
                window.scrollTo(0, scrolls[$(el).attr('data-name')]);
            });
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
    
    // when the window is resized
    $(window).resize(resize_window);

    update();
    resize_window();
});

var resize_window = function() {
    if($(window).width() <= 960) {
        $('.tool-link').each(function() {
            $('#content-' + $(this).attr('data-name')).show();
        });
    } else {
        $('.tool-link').each(function() {
            if($(this).attr('data-active') == 'true') {
                $('#content-' + $(this).attr('data-name')).show();
            } else {
                $('#content-' + $(this).attr('data-name')).hide();
            }
        });
    }
}


var update_content = function(tid, name) {
    $.post('/get_task_data/' + tid, function(t_data) {
        t_data = JSON.parse(t_data);

        if(t_data.success) {
            $('#content-' + name).html(t_data.result);
            $('#content-' + name).find('svg').each(function(i) {
                $(this).attr('width', null);
                $(this).attr('height', null);

                $(this).click(function() {
                    $("#svg-modal-content").html('');
                    $("#svg-modal-content").append($(this).clone());
                    $("#svg-modal").modal();

                    svgPanZoom($("#svg-modal-content > svg")[0], {
                        controlIconsEnabled: true,
                        zoomScaleSensitivity: 0.5,
                        contain: true
                    });

                });
            });
            $('#content-' + name).find('table').each(function(i) {
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

            scrolls[name] = 0;
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