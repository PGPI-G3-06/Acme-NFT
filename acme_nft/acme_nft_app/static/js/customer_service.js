"use strict"

function configureModal(){
    let background = document.querySelector('.modal-background');
    let modalBody = document.querySelector('.modal');
    let modalButton = document.querySelector('.new-complaint-button');

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
    let publishButton = document.querySelector('.publish-complaint-button');

    publishButton.addEventListener('click', function(event){

        let addComplaintForm = document.getElementById("post-complaint-form")

        let complaintTitle = document.getElementById("complaint-title").value;
        let complaintText = document.getElementById("complaint-input").value;

        if (complaintTitle.length >= 5 && complaintTitle.length <= 60 && complaintText.length >= 5){
            addComplaintForm.submit();
        }else{
            alert("El título de la queja debe tener entre 5 y 60 caracteres y el texto de la queja debe tener más de 5 caracteres.");
        }


    });
}



function main(){




    /* Modal functionality */

    configureModal();
    configureModalForm();

}

document.addEventListener("DOMContentLoaded", main);