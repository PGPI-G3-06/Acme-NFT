let selectAuthor = false;


function showSelectAuthor() {
    document.getElementById('elige-autor').style.display = 'block';
    document.getElementById('crea-autor').style.display = 'none';
    document.getElementsByName('select-author').value = true;
    selectAuthor = true;
}

function showCreateAuthor() {
    document.getElementById('elige-autor').style.display = 'none';
    document.getElementById('crea-autor').style.display = 'block';
    document.getElementsByName('select-author').value = false;
    selectAuthor = false;
}


function checkForm(){
    let form = document.getElementById('form');

    form.addEventListener('submit', (e) => {
        let name = document.getElementById('name').value;
        let collection = document.getElementById('collection').value;
        let author = document.getElementById('author-input').value;

        let nameBool = name.trim().length ===0;
        let collectionBool = collection.trim().length === 0;
        let authorBool = author.trim().length === 0;

        if (!selectAuthor && (nameBool ||
            collectionBool ||
            authorBool)) {
            e.preventDefault();
            alert('No puede haber campos vacíos');
        }else if(selectAuthor && (nameBool||
            collectionBool)) {
            e.preventDefault();
            alert('No puede haber campos vacíos');
        }

       document.forms['form'].elements['select-author'].value = selectAuthor;

    });




}


document.addEventListener("DOMContentLoaded", checkForm);