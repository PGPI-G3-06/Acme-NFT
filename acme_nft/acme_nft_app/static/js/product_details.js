"use strict"

function configureModal(){
    let background = document.querySelector('.modal-background');
    let modalBody = document.querySelector('.modal');
    let modalButton = document.querySelector('.new-comment-button');

    modalButton.addEventListener('click', function() {
        setTimeout(function(){
            document.querySelector(".face-3d").style = "backface-visibility: hidden;"
        }, 1000);
        document.querySelector('.modal-background').classList.add('show');
        document.querySelector('.modal').classList.add('show');
        document.querySelector('.modal-background').classList.remove('hide');
        document.querySelector('.modal').classList.remove('hide');
    });
    
    background.addEventListener('click', function(e) {
        e.preventDefault();
        setTimeout(function(){
            document.querySelector(".face-3d").style = "";
        }, 1000);
        background.classList.remove('show');
        background.classList.add('hide');
        modalBody.classList.remove('show');
        modalBody.classList.add('hide');
    });
    
    modalBody.addEventListener('click', function(e) {
        e.preventDefault();
    });
}

function configureModalForm(){
    let publishButton = document.querySelector('.publish-comment-button');

    publishButton.addEventListener('click', function(event){
    
        let addCommentForm = document.getElementById("post-comment-form")

        let commentText = document.getElementById("comment-input").value;

        if (commentText.length >= 5){
            addCommentForm.submit();
        }else{
            alert("No se puede publicar un comentario que tenga menos de 5 caracteres");
        }

    });
}

function main(){

    /* Wishlist button functionality */

    let wishlistButton = document.getElementById('wishlist-button');

    if (wishlistButton != null){
        let productId = wishlistButton.getElementsByTagName('img')[0].id.split("-")[1];
        wishlistButton.addEventListener('click', function(event){
    
            window.location.href='/wishlist/add/' + productId;
        
        });
        
        /* Load suggestions */

        getSuggestions(productId).then(response => {
            
            let showcase = document.getElementsByTagName('showcase')[0];
            let current_url = window.location.href;
            let domain = current_url.split("/")[0] + "//" + current_url.split("/")[2];

            for(let suggestion of response.suggestions){
                
                let showcaseElement = document.createElement('div');
                showcaseElement.classList.add('showcase-element');

                let elementImg = document.createElement('img');
                elementImg.src = `/static/${suggestion.image_url}`;
                elementImg.alt = suggestion.name;
                showcaseElement.appendChild(elementImg);

                let elementLink = document.createElement('a');
                elementLink.href = domain + `/product/${suggestion.id}`;
                elementLink.innerHTML = "Ver producto";
                elementLink.classList.add('class-link');
                showcaseElement.appendChild(elementLink);

                showcase.appendChild(showcaseElement);

            }
        })
    }

    /* Cart functionality */

    let addToCartBtn = document.getElementById('add-to-cart-btn');
    let cartForm = document.getElementById('cart-form');
    let quantityInput = document.getElementById('quantity');

    addToCartBtn.addEventListener('click', function(event){
        
        event.preventDefault();

        let cartError = document.getElementById('cart-error');
        cartError.style.display = 'block';

        let quantity = quantityInput.value;
        if (quantity > 0){
            cartForm.submit();
        }else{
            cartError.getElementsByTagName("span")[0].innerHTML = "La cantidad debe ser mayor a 0";
        }
    });

    let price = document.getElementById('price').innerHTML;
    price = price.replace(" €", "");
    price = parseFloat(price);
    document.getElementById('price').innerHTML = price.toFixed(2) + " €";

    quantityInput.addEventListener('change', function(event){

        event.preventDefault();

        let newPrice = (price * quantityInput.value).toFixed(2);

        document.getElementById('price').innerHTML = newPrice + " €";
    });

    /* Modal functionality */

    configureModal();
    configureModalForm();

}

async function getSuggestions(product_id) {

    let current_url = window.location.href;
    let domain = current_url.split("/")[0] + "//" + current_url.split("/")[2];
    let url = domain + `/suggestions/${product_id}`;

    // Default options are marked with *
    const response = await fetch(url, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie('csrftoken'),

            // 'Content-Type': 'application/x-www-form-urlencoded',
        }, redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    },);


    return response.json(); // parses JSON response into native JavaScript objects
}

document.addEventListener("DOMContentLoaded", main);