$(document).ready(function () {
    window.app = {


        'login': function () {

            $('#id_is_registration').val(1);
            $('.option-register').click(function (e) {
                $('#div_id_password2').show();
                $('#id_is_registration').val(1);
                $('.login-form-submit').val('Register');
            });

            $('.option-login').click(function (e) {
                $('#div_id_password2').hide();
                $('#id_is_registration').val(0);
                $('.login-form-submit').val('Log in');
            });
        },


        'dashboard': function () {

            $('.new-app-btn').click(function (e) {
                $('#new-app-form').show();
                $('.new-app-btn').hide();
            });

            $('.delete-app').click(function (e) {
                var app = $(this).parents('.app');
                var appId = app.attr('data-app-id');
                var appName = app.attr('data-app-name');
                $('#delete-app-modal-app-name').text(appName);
                $('#delete-app-modal').modal();

                $('.confirm-delete-app').one('click', function (e) {
                    $.ajax({
                        type: 'POST',
                        url: $(this).attr('data-action-url'),
                        data: {
                            id: appId,
                            csrfmiddlewaretoken: window.app_data.csrf_token
                        }
                    });
                    $('#delete-app-modal').modal('hide');
                    app.hide();
                })
            });
        }


    };

    window.app[window.app_data.view_name]();
});

