let selectAuthor = false;


function showSelectAuthor() {
    document.getElementById('elige-autor').style.display = 'block';
    document.getElementById('crea-autor').style.display = 'none';
    document.getElementsByName('select-author').value = true;
    selectAuthor = true;
}

function showCreateAuthor() {
    document.getElementById('elige-autor').style.display = 'none';
    document.getElementById('crea-autor').style.display = 'block';
    document.getElementsByName('select-author').value = false;
    selectAuthor = false;
}


function checkForm() {
    let form = document.getElementById('form');

    form.addEventListener('submit', (e) => {
        let name = document.getElementById('name').value;
        let collection = document.getElementById('collection').value;
        let author = document.getElementById('author-input').value;

        let nameBool = name.trim().length === 0;
        let collectionBool = collection.trim().length === 0;
        let authorBool = author.trim().length === 0;

        if (!selectAuthor && (nameBool ||
            collectionBool ||
            authorBool)) {
            e.preventDefault();
            alert('No puede haber campos vacíos');
        } else if (selectAuthor && (nameBool ||
            collectionBool)) {
            e.preventDefault();
            alert('No puede haber campos vacíos');
        }

        document.forms['form'].elements['select-author'].value = selectAuthor;

    });

}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function changeStatus(orderId) {
    let status = document.getElementsByName('status')[0].value;

    async function postData(url = '', data = {}) {
        // Default options are marked with *
        const response = await fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie('csrftoken'),

                // 'Content-Type': 'application/x-www-form-urlencoded',
            }, redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: data, // body data type must match "Content-Type" header

        },);
    }

    postData(`orders/status/${orderId}`, `{"status": "${status}"}`).then(r => {window.location.reload()});

}


document.addEventListener("DOMContentLoaded", checkForm);