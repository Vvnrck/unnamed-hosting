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

    function getApp (context) {
        var here = $(context);
        var app = here.hasClass('app')? here : $(context).parents('.app');
        return {
            'appId': app.attr('data-app-id'),
            'appName': app.attr('data-app-name'),
            'desiredState': app.attr('data-app-desired-state'),
            '$sel': app,
            '$stopBtn': app.find('.stop-app'),
            '$resumeBtn': app.find('.resume-app'),
            '$currentStatus': app.find('.app-status')
        }
    }
    
    function initEvents() {
    
        $('.app').each(function () {
            var app = getApp(this);
            console.log(app)
            if (app.desiredState != 'AppStates.disabled')
                app.$resumeBtn.hide();
            else
                app.$stopBtn.hide();
        })

        $('.new-app-btn').click(function (e) {
            $('#new-app-form').show();
            $('.new-app-btn').hide();
        });

        $('.delete-app').click(function (e) {
            var app = getApp(this);
            $('#delete-app-modal-app-name').text(app.appName);
            $('#delete-app-modal').modal();

            $('.confirm-delete-app').one('click', function (e) {
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('data-action-url'),
                    data: {
                        id: app.appId,
                        csrfmiddlewaretoken: window.app_data.csrf_token
                    }
                });
                $('#delete-app-modal').modal('hide');
                app.$sel.hide();
            })
        });
        
        $('.stop-app').click(function (e) {
            var app = getApp(this);
            app.$stopBtn.text('Requesting...');
            $.ajax({
                type: 'POST',
                url: $(this).attr('data-url'),
                data: {
                    id: app.appId,
                    csrfmiddlewaretoken: window.app_data.csrf_token
                },
                success: function (e) {
                    app.$stopBtn.text('Stop').hide();
                    app.$resumeBtn.show();
                    app.$currentStatus.text('Changing...');
                },
                error: function (e) {
                    alert('Failed to stop app');
                    app.$stopBtn.text('Stop');
                }
            });
        });
        
        $('.resume-app').click(function (e) {
            var app = getApp(this);
            app.$resumeBtn.text('Requesting...');
            $.ajax({
                type: 'POST',
                url: $(this).attr('data-url'),
                data: {
                    id: app.appId,
                    csrfmiddlewaretoken: window.app_data.csrf_token
                },
                success: function (e) {
                    app.$resumeBtn.text('Resume').hide();
                    app.$stopBtn.show();
                    app.$currentStatus.text('Changing...');
                },
                error: function (e) {
                    alert('Failed to resume app');
                    app.$resumeBtn.text('Stop');
                }
            });
        });
        
    } // end function initEvents()
    
    initEvents();
    setInterval(function(){
        $.ajax({
            type: 'GET',
            url: window.app_data.get_apps_url,
            success: function(data) {
                console.log('window.app_data.get_apps_url success');
                $('.app-col:not(.new-app-form-col)').remove();
                $('.new-app-form-col').parent().prepend(data);
                initEvents();
            }
        });
    }, 10000);
}


};

window.app[window.app_data.view_name]();
});

