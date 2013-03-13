$(document).ready(function() {

    $.ajaxSetup({
        cache: false
    });

    $('.vote-up-off, .vote-up-on').click(function(e) {
        if ($(this).hasClass('vote-up-off') && $(this).siblings().hasClass('vote-down-off')) {
            var question_id = $(this).attr('data-question-id');
            var url = '/questions/vote/' + question_id + '/up/';
            var target = $(this);
            // Deprecation Notice:
            // The jqXHR.success(), jqXHR.error(), and jqXHR.complete() callbacks will be deprecated in jQuery 1.8.
            // To prepare your code for their eventual removal, use jqXHR.done(), jqXHR.fail(), and jqXHR.always() instead.
            var jqXHR = $.ajax(url)
                .done(function(data, successCode, jqXHR) { // success
                    //console.log('from jQuery done (success) successCode: ' + successCode);
                    //console.log('from jQuery done (success) jqXHR: ' + jqXHR);
                    //console.log('from jQuery done (success) jqXHR.status: ' + jqXHR.status);
                    //console.log('from jQuery done (success) data: ' + data);
                    //// if data is a json object, check attributes
                    target.parent().find('.votes-up').html(data.votes_up);
                    target.toggleClass('vote-up-on').toggleClass('vote-up-off');
                })
                .fail(function(jqXHR, errorType, errorException) { // error
                    //console.log('from jQuery fail (error) jqXHR: ' + jqXHR);
                    //console.log('from jQuery fail (error) jqXHR.status: ' + jqXHR.status);
                    //console.log('from jQuery fail (error) errorType: ' + errorType);
                    //console.log('from jQuery fail (error) errorException: ' + errorException);
                })
                .always(function(jqXHR, returnCode) { // complete
                    //console.log('from jQuery always (complete) jqXHR:' + jqXHR);
                    //console.log('from jQuery always (complete) returnCode:' + returnCode);
                })
        }

        e.preventDefault();

    });

    $('.vote-down-off, .vote-down-on').click(function(e) {
        if ($(this).hasClass('vote-down-off') && $(this).siblings().hasClass('vote-up-off')) {
            var question_id = $(this).attr('data-question-id');
            var url = '/questions/vote/' + question_id + '/down/';
            var target = $(this);
            // Deprecation Notice:
            // The jqXHR.success(), jqXHR.error(), and jqXHR.complete() callbacks will be deprecated in jQuery 1.8.
            // To prepare your code for their eventual removal, use jqXHR.done(), jqXHR.fail(), and jqXHR.always() instead.
            var jqXHR = $.ajax(url)
                .done(function(data, successCode, jqXHR) { // success
                    //console.log('from jQuery done (success) successCode: ' + successCode);
                    //console.log('from jQuery done (success) jqXHR: ' + jqXHR);
                    //console.log('from jQuery done (success) jqXHR.status: ' + jqXHR.status);
                    //console.log('from jQuery done (success) data: ' + data);
                    //// if data is a json object, check attributes
                    target.parent().find('.votes-down').html(data.votes_down);
                    target.toggleClass('vote-down-on').toggleClass('vote-down-off');
                })
                .fail(function(jqXHR, errorType, errorException) { // error
                    //console.log('from jQuery fail (error) jqXHR: ' + jqXHR);
                    //console.log('from jQuery fail (error) jqXHR.status: ' + jqXHR.status);
                    //console.log('from jQuery fail (error) errorType: ' + errorType);
                    //console.log('from jQuery fail (error) errorException: ' + errorException);
                })
                .always(function(jqXHR, returnCode) { // complete
                    //console.log('from jQuery always (complete) jqXHR:' + jqXHR);
                    //console.log('from jQuery always (complete) returnCode:' + returnCode);
                })
        }

        e.preventDefault();
    });

    //$(".ajax-login").colorbox({iframe: true, height: "300px", width: "500px", onClosed:function() { location.reload(true); }});

});
