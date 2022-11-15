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
        wishlistButton.addEventListener('click', function(event){
        
            let productId = wishlistButton.getElementsByTagName('i')[0].id.split("-")[1];
    
            window.location.href='/wishlist/add/' + productId;
        
        });
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
    price.replace(" €", "");
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

document.addEventListener("DOMContentLoaded", main);