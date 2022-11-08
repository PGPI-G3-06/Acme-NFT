function main(){

    let wishlistForm = document.getElementById('wishlist-form');

    let wishlistButton = document.getElementById('wishlist-button');

    wishlistButton.addEventListener('click', function(event){
        
        let productId = wishlistButton.getElementsByTagName('i')[0].id.split("-")[1];

        window.location.href='/wishlist/add/' + productId;
    
    });

}

document.addEventListener("DOMContentLoaded", main);