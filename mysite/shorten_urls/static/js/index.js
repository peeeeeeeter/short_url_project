$('#short-url-form').submit((event) => {
    event.preventDefault();

    const input_val = $('#url-input');
    const formData = {'url_input': input_val.val()};

    $.ajax({
        url: '/api/v1/short_urls',
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: formSubmitOnSuccess,
        error: (xhr, status, message) => {
            if (xhr.status === 400) {
                formSubmitFormError(xhr, status, message);
            } else if (xhr.status == 403) {
                formSubmitForbiddenError(xhr, status, message);
            } else {
                formSubmitGeneralError(xhr, status, message);
            }
        }
    })

});


const formSubmitOnSuccess = (data, status, xhr) => {
    const show_url = $('#shorted-url');
    const {
        data: {
            short_url_path,
            original_url,
            preview_data,
        }
    } = data;
    const web_domain = 'http://127.0.0.1:8000/'
    const short_url = `${web_domain}${short_url_path}`

    if (preview_data !== undefined) {
        showUrlPreviewData(preview_data);
    } else {
        getUrlPreviewData(original_url);
    }

    show_url.text(short_url);
    show_url.attr('href', short_url);
    show_url.data('originalUrl', original_url);
}


const getUrlPreviewData = (original_url) => {
    const formData = {'url_input': original_url}

    $.ajax({
        url: '/api/v1/short_urls/preview',
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: (data, status, xhr) => {
            showUrlPreviewData(data);
        },
        error: (xhr, status, message) => {
            if (xhr.status === 400) {
                getUrlPreviewFormError(xhr, status, message);
            } else {
                getUrlPreviewGeneralError(xhr, status, message);
            }
        }
    })
}


const showUrlPreviewData = (data) => {
    let {title, description, url, image} = data['data'];

    const MAX_TITLE_LENGTH = 64;
    const MAX_DESCRIPTION_LENGTH = 64;
    const MAX_URL_LENGTH = 64;

    let domain = url.split('/')[2].toUpperCase();
    domain = domain.substr(0, MAX_URL_LENGTH);

    $('#preview-title').text(title);
    $('#preview-description').text(description);
    $('#preview-url').text(domain);
    $('#preview-image').attr('src', image);
    $('.preview-url-div').show();
}


const formSubmitFormError = (xhr, status, message) => {
    const data = xhr.responseJSON;
    console.log(xhr);

    if (data['url_input'][0] == 'This field is required.') {
        alert('請輸入網址')
    } else {
        alert('請輸入正確的網址 (含 http/https)');
    }
}


const formSubmitGeneralError = (xhr, status, message) => {
    console.log(xhr);
    alert(message);
}


const formSubmitForbiddenError = (xhr, status, message) => {
    let data;
    try {
        data = xhr.responseJSON;
    } catch (error) {
        return formSubmitGeneralError(xhr, status, message);
    }

    if (data['message'] == 'Rate limit exceed') {
        alert('超過使用額度，請稍後再試。');
        console.log(data['message'])
    } else {
        return formSubmitGeneralError(xhr, status, message);
    }
}


const getUrlPreviewFormError = formSubmitFormError;
const getUrlPreviewGeneralError = formSubmitGeneralError
