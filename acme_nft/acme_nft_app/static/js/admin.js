function showSelectAuthor() {
    document.getElementById('elige-autor').style.display = 'block';
    document.getElementById('crea-autor').style.display = 'none';
}

function showCreateAuthor() {
    document.getElementById('elige-autor').style.display = 'none';
    document.getElementById('crea-autor').style.display = 'block';
}


function checkForm(){
    let form = document.getElementById('form');

    form.addEventListener('submit', (e) => {
        let name = document.getElementById('name').value;
        let collection = document.getElementById('collection').value;
        let author = document.getElementById('author-input').value;

        debugger;

        if (name.trim.length ===0 ||
            collection.trim.length === 0 ||
            author.trim.length === 0) {
            e.preventDefault();
            alert('No puede haber campos vacíos');
        }

    });


}


document.addEventListener("DOMContentLoaded", checkForm);