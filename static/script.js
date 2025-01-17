function loadImage(navigation) {
    fetch(`/image/${navigation}`) 
        .then(response => response.json())
        .then(image => {
            document.getElementById('img-file-name-id').innerHTML = image.file_name;
            document.getElementById('image').src = `data:image/jpeg;base64,${image.data}`;
        })
        .catch(error => {
            console.error('Error fetching image:', error);
        });
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
        chooseElement.textContent = fileName;
        loadImage('first')
    }
});