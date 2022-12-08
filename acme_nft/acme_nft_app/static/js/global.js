"use strict"


function upQuantity(id, product_id, price, stock) {
    let quantity = document.getElementById(id).value;

    if (quantity == stock) {
        alert("No hay mas disponibles");
    } else {
        quantity++;
        let quantityFields = document.getElementsByClassName("quantity-field-" + id);
        
        for(let field of quantityFields) {
            field.value = quantity;
        }

        updateQuantityDB(product_id, quantity, price);
    }

}

function downQuantity(id, product_id, price, stock) {
    let quantity = document.getElementById(id).value;

    if (quantity == 1) {
        alert("No puedes tener menos de 1");
    } else {
        if (quantity > 1) {
            quantity--;
            let quantityFields = document.getElementsByClassName("quantity-field-" + id);
        
            for(let field of quantityFields) {
                field.value = quantity;
            }
        }
        updateQuantityDB(product_id, quantity, price)
    }
}

function calculateTotal(price, quantity, id) {
    let total_doc_fields = document.getElementsByClassName("total-" + id + "-class");
    let total = price * quantity;

    for(let field of total_doc_fields) {
        field.innerHTML = total.toFixed(2) + "€";
    }
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

function deleteProduct(id) {
    let current_url = window.location.href;
    let domain = current_url.split("/")[0] + "//" + current_url.split("/")[2];
    let url = domain + `/cart/delete/${id}`;

    async function postData(url = '') {
        // Default options are marked with *
        const response = await fetch(url, {
            method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            }, redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url// body data type must match "Content-Type" header
        },);
        let product_entries = document.getElementsByClassName("product-" + id + "-entry");

        for(let product of product_entries) {
            product.remove();
        }

        return response.json(); // parses JSON response into native JavaScript objects
    }

    postData(url)
        .then((data) => {
            console.log(data); // JSON data parsed by `data.json()` call
        });
}

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


    return response.json(); // parses JSON response into native JavaScript objects
}

async function updateQuantityDB(id, quantity, price) {
    let current_url = window.location.href;
    let domain = current_url.split("/")[0] + "//" + current_url.split("/")[2];
    let url = domain + `/cart/update-quantity/${id}`;
    const data = '{"quantity":' + quantity + '}';

    calculateTotal(price, quantity, id);

    postData(url, data)
        .then((data) => {
            console.log(data); // JSON data parsed by `data.json()` call
        });

}