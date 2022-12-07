"use strict"


function configureModalOpinionForm(){
    let publishButton = document.querySelector('.publish-complaint-button');

    publishButton.addEventListener('click', function(event){
        event.preventDefault();

        let addComplaintForm = document.getElementById("post-complaint-form")

        let contactName = document.getElementById("contact-name").value;
        let contactSubject = document.getElementById("contact-subject").value;


        if (contactName.length >= 5 && contactName.length <= 60 && contactSubject.length >= 5 && contactSubject.length <= 60){
            addComplaintForm.submit();
        }else{
            alert("El nombre y el asunto deben tener entre 5 y 60 caracteres");
        }


    });
}



function main(){

    configureModalOpinionForm();

}

document.addEventListener("DOMContentLoaded", main);