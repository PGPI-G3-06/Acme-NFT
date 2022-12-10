function main(){
    let titleForm = document.getElementById("title_form");
    let title = document.getElementById("title");
    let streetNameForm = document.getElementById("street_name_form");
    let streetName = document.getElementById("street_name");
    let numberForm = document.getElementById("number_form");
    let number = document.getElementById("number");
    let blockForm = document.getElementById("block_form");
    let block = document.getElementById("block");
    let floorForm = document.getElementById("floor_form");
    let floor = document.getElementById("floor");
    let doorForm = document.getElementById("door_form");
    let door = document.getElementById("door");
    let cityForm = document.getElementById("city_form");
    let city = document.getElementById("city");
    let codePostalForm = document.getElementById("code_postal_form");
    let codePostal = document.getElementById("code_postal");

    if(floor.value == "None"){
        floor.value = "";
    }

    if(block.value == "None"){
        block.value = "";
    }

    if(door.value == "None"){
        door.value = "";
    }

    checkBtn();

    title.addEventListener("change", function(){
        deleteErrors(titleForm);
    });

    streetName.addEventListener("change", function(){
        deleteErrors(streetNameForm);
    });

    number.addEventListener("change", function(){
        deleteErrors(numberForm);
    });

    block.addEventListener("change", function(){
        deleteErrors(blockForm);
    });

    floor.addEventListener("change", function(){
        deleteErrors(floorForm);
    });

    door.addEventListener("change", function(){
        deleteErrors(doorForm);
    });

    city.addEventListener("change", function(){
        deleteErrors(cityForm);
    });

    codePostal.addEventListener("change", function(){
        deleteErrors(codePostalForm);
    });
}

function deleteErrors(form){
    if(form.classList.contains("class-error-form")){
        form.classList.remove("class-error-form");
        let nodes = [];

        for (let i = 0; i < form.children.length; i++) {
            let node = form.children[i];
            if(node.classList.contains("class-error-message")){
                nodes.push(node);
            }
        }

        for (let node of nodes){
            node.parentNode.removeChild(node)
        }
        checkBtn();
    }
}

function checkBtn(){
    let btn = document.getElementById("profile_btn");
    if(document.getElementsByClassName("class-error-form").length > 0){
        btn.disabled = true;
    } else{
        btn.disabled = false;
    }
}

function deleteAddress(url){
    if(confirm("¿Estás seguro de que quieres eliminar esta dirección?")==true){
        return window.location.href = url;
    }
}

document.addEventListener("DOMContentLoaded", main);