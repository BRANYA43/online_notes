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

    function add_new_note_to_list(data) {
        $('#note_list').prepend(`
            <div id="${data.note.id}" class="card" data-url="${data.url}" data-category-id="${data.category ? data.category.id : ''}">
              <div class="card-body" style="${data.category ? 'color: ' + data.category.color + ';' : ''}">
                <p class="card-subtitle">Category: ${data.category ? data.category.title : '---'}</p>
                <p class="card-subtitle">Title: ${data.note.title}</p>
                <p class="card-subtitle">Date: ${data.note.date}</p>
              </div>
                <div class="card-footer d-flex justify-content-end gap-2">
                  <button class="btn btn-outline-secondary btn-sm" type="button">E</button>
                  <button class="btn btn-outline-secondary btn-sm" type="button">A</button>
                  <button class="btn btn-outline-secondary btn-sm" type="button">X</button>
                </div>
            </div>
        `);
    }

    $('#note_form').submit(function(event){
        event.preventDefault();

        send_ajax_request(
            data=$(this).serialize(),
            type=$(this).attr('method'),
            url=$(this).attr('action'),
            success=function(response) {
                add_new_note_to_list(response)
                var form = $('#note_form')
                form.attr('action', response.url)
                console.log(response);
            },
        );
    });

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
            console.error(xhr.responseJSON.errors);
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
            $('#user_registered_success_alert').removeClass('d-none');
            console.log(response);
        },
        error=function(xhr, status, error) {
            var msg = make_error_msg(xhr.responseJSON.errors);
            set_alert_msg($('#modal_registration_form .alert-danger'), msg);
            console.error(errors);
        });
    });
});