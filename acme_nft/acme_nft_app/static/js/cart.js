"use strict"

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

function checkSubmit(event) {
    event.preventDefault();

    let form = event.target;
    let formData = new FormData(form);

    console.log(formData.get("productos"));

    console.log(formData.get("direccion"));
    console.log(formData.get("metodo_pago"));

}


