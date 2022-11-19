"use strict"

function upQuantity(id, product_id, price, stock) {
    let quantity = document.getElementById(id).value;

    if (quantity == stock) {
        alert("No hay mas disponibles");
    } else {
        quantity++;
        document.getElementById(id).value = quantity;
        updateQuantityDB(product_id, quantity, price);
    }

}

function downQuantity(id, product_id, price, stock) {
    let quantity = document.getElementById(id).value;

    if (quantity == 1) {
        alert("No puedes tener menos de 1");
        return;
    } else {
        if (quantity > 1) {
            quantity--;
            document.getElementById(id).value = quantity;
        }
        updateQuantityDB(product_id, quantity, price)
    }

}

function calculateTotal(price, quantity, id) {
    console.log(price, quantity, id);
    let total_doc = document.getElementById("total-" + id);
    console.log(total_doc);
    let total = price * quantity;
    total_doc.innerHTML = total + "€";
}

async function updateQuantityDB(id, quantity, price) {
    let url = `cart/update-quantity/${id}`;
    const data = '{"quantity":' + quantity + '}';

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

        calculateTotal(price, quantity, id);

        return response.json(); // parses JSON response into native JavaScript objects
    }

    postData(url, data)
        .then((data) => {
            console.log(data); // JSON data parsed by `data.json()` call
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

function deleteProduct(id, itemId) {
    let url = `cart/delete/${id}`;

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
        let product = document.getElementById("tr-product-id-_id".replace("_id", itemId));
        product.remove();

        return response.json(); // parses JSON response into native JavaScript objects
    }

    postData(url)
        .then((data) => {
            console.log(data); // JSON data parsed by `data.json()` call
        });
}

