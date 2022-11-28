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

            let productId = item.getElementsByTagName("form")[0].id.replace("add-cart-", "");

            let icon = item.getElementsByTagName("i")[0];   

            let form = document.getElementById("add-cart-" + productId);

            icon.classList.add("fa-spin");
            setTimeout(()=>{
                icon.classList.remove("fa-spin");
            }, 2000);
            form.submit()
        });
    }

}

function nextPage(minPages, maxPages){
    let min = parseInt(minPages);
    let max = parseInt(maxPages)-1;
    if(window.location.search){
        let page = new URL(location.href).searchParams.get('page')
        if(page < max && page >= min){
            page++;
            window.location.href = "?page=" + page;
        }
    } else{
        min++;
        window.location.href = "?page=" + min;
    }
}

function previousPage(minPages, maxPages){
    let min = parseInt(minPages);
    let max = parseInt(maxPages)-1;
    if(window.location.search){
        let page = new URL(location.href).searchParams.get('page')
        if(page <= max && page > min){
            page--;
            window.location.href = "?page=" + page;
        }
    }
}

document.addEventListener("DOMContentLoaded", main);