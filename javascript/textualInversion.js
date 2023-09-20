


function start_training_textual_inversion() {
    gradApp().querySelector('#ti_error').innerHTML = '';

    var id = randomId();
    requestProgress(id, gradApp().getElementById('ti_output'), gradApp().getElementById('ti_gallery'), function() {}, function(progress) {
        gradApp().getElementById('ti_progress').innerHTML = progress.textinfo;
    });

    var res = Array.from(arguments);

    res[0] = id;

    return res;
}
