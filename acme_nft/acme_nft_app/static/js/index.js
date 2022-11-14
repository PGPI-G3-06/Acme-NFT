"use strict"

function main(){

    // In-out card animation

    let productCard = document.getElementsByClassName("class-card");

    for (let product of productCard) {
        product.addEventListener("mouseover", function(){
            document.querySelectorAll(".selectbox").forEach(input => {
                input.style.opacity = "0";
                input.style.transition = "all 1s";
            })
        });
    
        product.addEventListener("mouseout", function(){
            document.querySelectorAll(".selectbox").forEach(input => {
                input.style.opacity = "1";
                input.style.transition = "all 1s";
            })
        });   
    }

    // Toogle heart

    let wishList = document.getElementsByClassName("class-lista-deseos");

    for (let wishListIcon of wishList) {
        wishListIcon.addEventListener("click", function(event){

            let productId = wishListIcon.getElementsByTagName("img")[0].id.split("-")[1];

            window.location.href = "/wishlist/add/" + productId;

        });   
    }

    // Add to cart

    let cart = document.getElementsByClassName("class-carrito");
    

    for (let item of cart) { 
        item.addEventListener("click", function(){
            let icon = item.childNodes[0];   
            // Add to cart function
            icon.classList.add("fa-spin");
            setTimeout(()=>{
                icon.classList.remove("fa-spin");
            }, 2000);
        });
    }

}

document.addEventListener("DOMContentLoaded", main);