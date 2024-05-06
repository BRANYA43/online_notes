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
            <div id="${data.note.id}" class="card" data-category-id="${data.category ? data.category.id : ''}">
              <div class="card-body" style="${data.category ? 'color: ' + data.category.color + ';' : ''}">
                <p class="card-subtitle">Category: ${data.category ? data.category.title : '---'}</p>
                <p class="card-subtitle">Title: ${data.note.title}</p>
                <p class="card-subtitle">Date: ${data.note.date}</p>
              </div>
                <div class="card-footer d-flex justify-content-end gap-2">
                  <a id="edit" href="${data.urls.retrieve}" class="btn btn-outline-secondary btn-sm" ><i data-feather="edit"></i></a>
                  <a id="archive" href="${data.urls.archive}" class="btn btn-outline-secondary btn-sm" ><i data-feather="archive"></i></a>
                  <a id="delete" href="${data.urls.delete}" class="btn btn-outline-secondary btn-sm"><i data-feather="trash-2"></i></a>
                </div>
            </div>
        `);
    }

    function add_new_category_to_list(data) {
        $('#category_list').append(`
          <div id="${data.category.id}" class="card">
            <div class="card-body" style="color: ${data.category.color}">
              <p class="card-subtitle">Title: ${data.category.title}</p>
            </div>
            <div class="card-footer d-flex justify-content-end gap-2">
              <a id="edit" href="${data.urls.retrieve}" class="btn btn-outline-secondary btn-sm"><i data-feather="edit"></i></a>
              <a id="delete" href="${data.urls.delete}" class="btn btn-outline-secondary btn-sm"><i data-feather="trash-2"></i></a>
            </div>
          </div>
        `);
    }

    $('#category_list').on('click', '#edit', function(event) {
        event.preventDefault();

        send_ajax_request(
            data={},
            type='GET',
            url=$(this).attr('href'),
            success=function(response) {
                var form = $('form#category_form');
                form.attr('action', response.urls.update);
                form.find('#id_title').val(response.category.title);
                form.find('#id_color').val(response.category.color);
                console.log(response)
            },
            error=function(xhr, error, status) {
                console.error(error);
        });

    });

    $('form#category_form').submit(function(event) {
        event.preventDefault();

        send_ajax_request(
            data=$(this).serialize(),
            type=$(this).attr('method'),
            url=$(this).attr('action'),
            success=function(response) {
                var form = $('form#category_form');
                if(form.attr('action').includes('create')) {
                    form.attr('action', response.urls.update);
                    add_new_category_to_list(response);
                }
                else if(form.attr('action').includes('update')) {
                    $(`#${response.category.id} p:contains('Title')`).html(`Title: ${response.category.title}`);
                    $(`#${response.category.id}`).find('.card-body').css('color', response.category.color);
                }
                console.log(response);
            },
            error=function(xhr, status, error){
                console.error(error);
            }
        );
    });

    $('#note_list').on('click', '#archive', function(event) {
        event.preventDefault();

        send_ajax_request(
            data={},
            type='GET',
            url=$(this).attr('href'),
            success=function(response) {
                var form = $('form#note_form');
                if(form.attr('action').includes('update') && form.attr('action').includes(`${response.note.id}`)){
                    form.trigger('reset');
                    form.attr('action', form.attr('data-create-url'));
                }
                $(`#${response.note.id}`).remove();
            },
            error=function(xhr, status, error){
                console.error(error);

        });
    });

    $('#note_list').on('click', '#delete', function (event){
        event.preventDefault();

        send_ajax_request(
            data={},
            type='GET',
            url=$(this).attr('href'),
            success=function(response) {
                var form = $('form#note_form');
                if(form.attr('action').includes('update') && form.attr('action').includes(`${response.note.id}`)){
                    form.trigger('reset');
                    form.attr('action', form.attr('data-create-url'));
                }
                $(`#${response.note.id}`).remove();
            },
            error=function(xhr, status, error){
                console.error(error);

        });
    });

    $('#note_list').on('click', '#edit', function(event) {
        event.preventDefault();

        send_ajax_request(
            data={},
            type='GET',
            url=$(this).attr('href'),
            success=function(response) {
                var form = $('form#note_form');
                form.attr('action', response.urls.update);
                form.find('#id_title').val(response.note.title);
                form.find('#id_text').val(response.note.text);
                if(response.category) {
                    form.find('#id_category').val(response.category.id);
                }
                console.log(response)
            },
            error=function(xhr, error, status) {
                console.error(error);
        });
    });

    $('#note_form').submit(function(event){
        event.preventDefault();

        send_ajax_request(
            data=$(this).serialize(),
            type=$(this).attr('method'),
            url=$(this).attr('action'),
            success=function(response) {
                var form = $('#note_form');
                if(form.attr('action').includes('create')) {
                    form.attr('action', response.urls.update);
                    add_new_note_to_list(response);
                }
                else if(form.attr('action').includes('update')) {
                    if(response.category) {
                        $(`#${response.note.id} p:contains('Category')`).html(`Category: ${response.category.title}`);
                        $(`#${response.note.id}`).find('.card-body').css('color', response.category.color);
                    }
                    $(`#${response.note.id} p:contains('Title')`).html(`Title: ${response.note.title}`);
                }
                console.log(response);
            },
            error=function(xhr, status, error) {
                console.error(error);
        });
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