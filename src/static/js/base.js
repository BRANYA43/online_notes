$(document).ready(function(){
    function send_ajax_request(data, type, url, success, error){
        $.ajax({
            url: url,
            type: type,
            dataType: 'json',
            data: data,
            success: success,
            error: error
        });
    };

    function make_error_msg(errors) {
        var msg = ''
        for (var field in errors) {
            msg = errors[field][0] + '\n';
        }
        return msg
    }

    function clear_alert_msg(alert) {
        alert.addClass('d-none');
        alert.html('');
    }

    function set_alert_msg(alert, msg) {
        alert.removeClass('d-none');
        alert.html(msg);
    }

    $('#navbar [name="logout_link"]').click(function(event){
        event.preventDefault();

        send_ajax_request(
        data={},
        type='GET',
        url=$(this).attr('href'),
        success=function(response) {
            window.location.reload();
            console.log(response);
        },
        error=function(xhr, status, error) {
            console.error(errors);
        });
    });

    $('#login_form').submit(function(event){
        event.preventDefault();

        send_ajax_request(
        data=$(this).serialize(),
        type=$(this).attr('method'),
        url=$(this).attr('action'),
        success=function(response) {
            window.location.reload();
            console.log(response);
        },
        error=function(xhr, status, error) {
            var msg = make_error_msg(xhr.responseJSON.errors);
            set_alert_msg($('#modal_login_form .alert-danger'), msg);
            console.error(errors);
        });
    });

    $('#registration_form').submit(function(event){
        event.preventDefault();

        send_ajax_request(
        data=$(this).serialize(),
        type=$(this).attr('method'),
        url=$(this).attr('action'),
        success=function(response) {
            $('#registration_form')[0].reset();
            $('#modal_registration_form').modal('toggle');
            clear_alert_msg($('#modal_registration_form .alert-danger'));
            console.log(response);
        },
        error=function(xhr, status, error) {
            var msg = make_error_msg(xhr.responseJSON.errors);
            set_alert_msg($('#modal_registration_form .alert-danger'), msg);
            console.error(errors);
        });
    });
});