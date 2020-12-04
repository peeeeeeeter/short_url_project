$('#short-url-form').submit((event) => {
    event.preventDefault();

    const input_val = $('#url-input');
    const formData = {'url_input': input_val.val()};

    $('.show-url').hide();

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


$('#get-original-url').on('click', (event) => {

    event.preventDefault();

    const input_val = $('#url-input');
    const formData = {'short_url': input_val.val()};

    $('.show-url').hide();

    $.ajax({
        url: '/api/v1/short_urls/original_url',
        type: 'GET',
        data: formData,
        dataType: 'json',
        success: getOriginalUrlOnSuccess,
        error: (xhr, status, message) => {
            if (xhr.status === 400) {
                console.log(xhr);
                alert('無效的輸入，請輸入有效的五位字元')
            } else {
                formSubmitGeneralError(xhr, status, message);
            }
        }
    })
})

const formSubmitOnSuccess = (data, status, xhr) => {
    const show_url = $('.shorted-url-div a');

    const {
        data: {
            short_url_path,
            original_url,
            preview_data,
        }
    } = data;
    const web_domain = 'http://54.90.86.112:8000/'
    const short_url = `${web_domain}${short_url_path}`

    if (preview_data !== undefined) {
        showUrlPreviewData(preview_data);
    } else {
        getUrlPreviewData(original_url);
    }

    $('#shorted-url').text(short_url);
    show_url.attr('href', short_url);
    show_url.data('originalUrl', original_url);
}


const getOriginalUrlOnSuccess = (data, status, xhr) => {
    let {data: {original_url, short_url_path}} = data;

    const web_domain = 'http://127.0.0.1:8000/'
    const short_url = `${web_domain}${short_url_path}`

    const show_url = $('.shorted-url-div a');
    $('#shorted-url').text(short_url);
    show_url.attr('href', short_url);
    show_url.data('originalUrl', original_url);

    getUrlPreviewData(original_url);
}


const getUrlPreviewData = (original_url) => {
    const formData = {'url_input': original_url}

    $.ajax({
        url: '/api/v1/short_urls/preview',
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: (data, status, xhr) => {
            showUrlPreviewData(data, original_url);
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


const showUrlPreviewData = (data, original_url) => {
    console.log('hi');
    let {title, description, url, image_url} = data['data'];

    const MAX_TITLE_LENGTH = 64;
    const MAX_DESCRIPTION_LENGTH = 64;
    const MAX_URL_LENGTH = 64;

    let domain = url.split('/')[2].toUpperCase();
    domain = domain.substr(0, MAX_URL_LENGTH);

    if (image_url.startsWith('http')) {
        $('#preview-image').attr('src', image_url);
    }

    $('#show-original-url').text(original_url);
    $('#preview-title').text(title);
    $('#preview-description').text(description);
    $('#preview-url').text(domain);
    $('.preview-url-div').show();
    $('.show-url').show();
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
