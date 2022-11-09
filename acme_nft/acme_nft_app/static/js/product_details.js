"use strict"

function configureModal(){
    let background = document.querySelector('.modal-background');
    let modalBody = document.querySelector('.modal');
    let modal = document.querySelector('.modal-flip-from-left');
    modal.addEventListener('click', function() {
        console.log("Dentro");
        document.querySelector('.modal-background').classList.add('show');
        document.querySelector('.modal-background').classList.remove('hide');
        document.querySelector('.modal').classList.add('show');
        document.querySelector('.modal').classList.remove('hide');
    });
    
    background.addEventListener('click', function(e) {
        e.preventDefault();
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

        // Se podrían realizar validaciones del comentario aquí

        addCommentForm.submit();

    });
}

function main(){

    let wishlistForm = document.getElementById('wishlist-form');

    let wishlistButton = document.getElementById('wishlist-button');

    wishlistButton.addEventListener('click', function(event){
        
        let productId = wishlistButton.getElementsByTagName('i')[0].id.split("-")[1];

        window.location.href='/wishlist/add/' + productId;
    
    });

    configureModal();
    configureModalForm();

}

document.addEventListener("DOMContentLoaded", main);