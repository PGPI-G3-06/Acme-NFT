"use strict"

function main(){

    // In-out card animation

    let productCard = document.getElementsByClassName("class-card");

    productCard.addEventListener("mouseover", function(){
        document.querySelectorAll(".selectbox").forEach(input => {
            input.style.opacity = "0";
            input.style.transition = "all 1s";
        })
    });

    productCard.addEventListener("mouseout", function(){
        document.querySelectorAll(".selectbox").forEach(input => {
            input.style.opacity = "1";
            input.style.transition = "all 1s";
        })
    });

    // Toogle heart

    let wishList = document.getElementsByClassName("class-lista-deseos");
    let toggler = false; // Hay que inicializarlo según si está o no en la lista de deseos

    wishList.addEventListener("click", function(){
        if(toggler){
            // Delete from wishlist
            wishImg.current.src = "./images/heart.png";
            toggler = false;
            if(toggler !== undefined){
                toggler = !toggler;
            }
        }else{
            // Add to wishlist
            wishImg.current.src = "./images/heart-lleno.png";
            toggler = true;
        }
    });

    // Add to cart

    let cart = document.getElementsByClassName("class-carrito");
    let icon = cart.childNodes[0];

    cart.addEventListener("click", function(){
        // Add to cart function
        icon.classList.add("fa-spin");
        setTimeout(()=>{
            icon.classList.remove("fa-spin");
        }, 2000);
    });

}

document.addEventListener("DOMContentLoaded", main);