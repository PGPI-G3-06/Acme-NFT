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
    let url = `cart/update-quantity/${id}`;
    const data = '{"quantity":' + quantity + '}';


    calculateTotal(price, quantity, id);

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

function addAddress() {

    let addressForm = document.getElementById("address-form");
    addressForm.onsubmit = addAddressSubmit;
}

function addAddressSubmit(event) {
    event.preventDefault();

    let form = event.target;
    let formData = new FormData(form);

    console.log(formData);
}

// function addAddressSubmit2(event) {
//
//     const addressForm = document.getElementById("address-form");
//
//     addressForm.addEventListener("submit", (event) => {
//         event.preventDefault();
//
//         let form = event.target;
//         let formData = new FormData(form);
//
//         let error = false;
//
//         let streetName = formData.get("street_name");
//         let number = formData.get("number");
//         let block = formData.get("block");
//         let floor = formData.get("floor");
//         let door = formData.get("door");
//         let postalCode = formData.get("postal_code");
//         let city = formData.get("city");
//
//         if (streetName === "") {
//             error = true;
//             addressForm.street_name.classList.add("is-invalid");
//         }
//
//         if (!error) {
//             return addressForm.submit();
//         }
//
//
//     });
//
//
// }


function checkSubmit(event) {
    event.preventDefault();

    let form = event.target;
    let formData = new FormData(form);

    console.log(formData.get("productos"));

    console.log(formData.get("direccion"));
    console.log(formData.get("metodo_pago"));

}

