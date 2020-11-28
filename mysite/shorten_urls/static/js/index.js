$('#short-url-form').submit((event) => {
    event.preventDefault();

    const input_val = $('#url-input');
    const formData = {'url_input': input_val.val()};
    console.log(formData);

    $.ajax({
        url: '/api/v1/short_urls/',
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: onSuccess,
        error: (xhr, status, message) => {
            if (xhr.status === 400) {
                formError(xhr, status, message);
            } else {
                generalError(xhr, status, message);
            }
        }
    })

});

const onSuccess = (data, status, xhr) => {
    const {data: {short_url, original_url}} = data;
    const show_url = $('#shorted-url');
    show_url.text(short_url);
    show_url.data('originalUrl', original_url);
}


const formError = (xhr, status, message) => {
    const data = xhr.responseJSON;
    console.log(xhr);

    if (data['url_input'][0] == 'This field is required.') {
        alert('請輸入網址')
    } else {
        alert('請輸入正確的網址 (含 http/https)');
    }
}

const generalError = (xhr, status, message) => {
    console.log(xhr);
    alert(message);
}