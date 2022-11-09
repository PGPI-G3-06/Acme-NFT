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