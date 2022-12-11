"use strict"

function addAddress() {

    let addressForm = document.getElementById("address-form");
    addressForm.onsubmit = addAddressSubmit;
}

function addAddressSubmit(event) {
    event.preventDefault();

    let form = event.target;
    let formData = new FormData(form);

}

function checkSubmit(event) {
    event.preventDefault();

    let form = event.target;
    let formData = new FormData(form);

}




