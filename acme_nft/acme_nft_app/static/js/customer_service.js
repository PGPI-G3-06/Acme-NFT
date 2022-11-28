"use strict"



function configureModalForm(){
    let publishButton = document.querySelector('.publish-complaint-button');

    publishButton.addEventListener('click', function(event){
        event.preventDefault();

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

function configureModalOpinionForm(){
    let publishButton = document.querySelector('.publish-opinion-button');

    publishButton.addEventListener('click', function(event){
        event.preventDefault();

        let addComplaintForm = document.getElementById("post-opinion-form")

        let complaintTitle = document.getElementById("opinion-title").value;
        let complaintText = document.getElementById("opinion-input").value;

        console.log(complaintTitle.length);
        console.log(complaintText.length);
        console.log(complaintTitle.length >= 5 && complaintTitle.length <= 60 && complaintText.length >= 5);
        if (complaintTitle.length >= 5 && complaintTitle.length <= 60 && complaintText.length >= 5){
            addComplaintForm.submit();
        }else{
            alert("El título de la opinion debe tener entre 5 y 60 caracteres y el texto de la opinion debe tener más de 5 caracteres.");
        }


    });
}



function main(){




    /* Modal functionality */
    configureModalForm();
    configureModalOpinionForm();

}

document.addEventListener("DOMContentLoaded", main);