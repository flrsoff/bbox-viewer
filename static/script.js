function loadImage(navigation) {
    console.log(`loadImage(${navigation})`, navigation)
    fetch(`/image/${navigation}`) 
        .then(response => response.json()).then(image => {
            document.getElementById('img-file-name-id').textContent = image.file_name;
            document.getElementById('image').src = `data:image/jpeg;base64,${image.data}`;
        }).catch(error => { console.error('Error fetching image:', error);});
}

document.querySelector('.choose').addEventListener('click', function () {
    document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', function () {
    const fileInput = this;
    const chooseElement = document.querySelector('.choose');
    if (fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        if (!fileName.endsWith('.yaml')) {
            alert('Select a file with a .yaml extension');
            return;
        }
        chooseElement.textContent = fileInput.files[0].name;
        
        const formData = new FormData(); formData.append('file', fileInput.files[0]);
        fetch('/upload', {
            method: 'POST',
            body: formData,
        }).then(response => console.log(response.json()))
        .catch(error => {console.error('Error:', error);});
        
        loadImage('first');
    }
});