/**
 * Created by Administrator on 2017/9/26 0026.
 */

$(function () {
    bindChangeCaptcha();
    bindLoginSubmit();
});

function bindChangeCaptcha() {
    $('#check_code_img').click(function () {
        var old_src = $(this).attr('src');
        var new_src = old_src + '?';
        $(this).attr('src', new_src);
    })
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function bindLoginSubmit() {
    $('#submit').click(function () {
        $.ajaxSetup({
            'beforeSend': function (xhr, settings) {
                var csrftoken = getCookie('csrftoken');
                //2.在header当中设置csrf_token的值
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        });
        var $email = $('#email').val();
        var $password = $('#password').val();
        var $captcha = $('#captcha').val();
        var $remember = $('#remember').prop('checked');
        $.ajax({
            url: '/account/login/',
            type: 'POST',
            //data: {'email': $email, 'password': $password, 'captcha': $captcha, 'remember': $remember},
            data: $('[role="form"]').serialize(),
            dataType: 'JSON',
            success: function (arg) {
                console.log(arg);
                if (!arg.status) {
                    if (arg.errors.hasOwnProperty('captcha')){
                        var err = arg.errors.captcha[0].message;
                        $('#err_msg').text(err);
                    } else {
                        var err = '用户名或者密码错误';
                        $('#err_msg').text(err);
                    }
                }
                else {
                    window.location.href = arg.data
                }
            }
        })
    })}




