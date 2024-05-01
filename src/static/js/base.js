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

    $('#registration_form').submit(function(event){
        event.preventDefault();

        send_ajax_request(
        data=$(this).serialize(),
        type=$(this).attr('method'),
        url=$(this).attr('action'),
        success=function(response) {
            $('#registration_form')[0].reset();
            $('#modal_registration_form').modal('hide');
            console.log(response);
        },
        error=function(xhr, status, error) {
            var errors = xhr.responseJSON.errors;
            console.error(errors);
        });
    });
});