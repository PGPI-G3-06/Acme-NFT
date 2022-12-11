"use strict"


function configureModalOpinionForm(){
    let publishButton = document.querySelector('.publish-opinion-button');

    publishButton.addEventListener('click', function(event){
        event.preventDefault();

        let addComplaintForm = document.getElementById("post-opinion-form")

        let complaintTitle = document.getElementById("opinion-title").value;
        let complaintText = document.getElementById("opinion-input").value;

        if (complaintTitle.length >= 5 && complaintTitle.length <= 60 && complaintText.length >= 5){
            addComplaintForm.submit();
        }else{
            alert("El título de la opinion debe tener entre 5 y 60 caracteres y el texto de la opinion debe tener más de 5 caracteres.");
        }


    });
}



function main(){




    /* Modal functionality */

    configureModalOpinionForm();

}

document.addEventListener("DOMContentLoaded", main);