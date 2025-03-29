import { sendImageAndAnalyze } from './script.js';

class ImageUploadModal {
    constructor(onImageSelected) {
        
        this.modal = null;
        this.onImageSelected = onImageSelected;
        this.imagePreview = null;

        this.createModal();
    }

    createModal() {
        // Create the modal container
        this.modal = document.createElement('div');
        this.modal.id = 'image-upload-modal';
        this.modal.style.display = 'none';
        this.modal.style.position = 'fixed';
        this.modal.style.top = '50%';
        this.modal.style.left = '50%';
        this.modal.style.transform = 'translate(-50%, -50%)';
        this.modal.style.backgroundColor = 'white';
        this.modal.style.padding = '20px';
        this.modal.style.border = '1px solid black';
        this.modal.style.zIndex = '100';

        // Create modal content container
        const modalContent = document.createElement('div');
        this.modal.appendChild(modalContent);

        // Create drag-and-drop area
        const dropArea = document.createElement('div');
        dropArea.id = 'drop-area';
        dropArea.style.border = '2px dashed #ccc';
        dropArea.style.padding = '20px';
        dropArea.style.textAlign = 'center';
        dropArea.textContent = 'Drag and drop your image here';
        modalContent.appendChild(dropArea);

        const closeButton = document.createElement('span');
        closeButton.id = 'close-modal-button'; // optional ID
        closeButton.classList.add('close-button'); //Add a class for styling
        closeButton.innerHTML = '&#10006;'; // or use other HTML character codes
        closeButton.addEventListener('click', () => this.hide());
    
        // Append to modal (add styles in CSS)
        this.modal.appendChild(closeButton);

        // Create image preview
        this.imagePreview = document.createElement('img');
        this.imagePreview.id = 'image-preview-container';
        this.imagePreview.style.maxWidth = '100%';
        this.imagePreview.style.display = 'none';
        modalContent.appendChild(this.imagePreview);


        // Create file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/jpeg, image/png, image/jpg';
        fileInput.style.display = 'none';
        fileInput.addEventListener('change', (event) => this.handleFileSelect(event));
        modalContent.appendChild(fileInput);


        // Placeholder text
        const placeholderText = document.createElement('p');
        placeholderText.textContent = 'Allowed file types: JPEG, PNG, JPG';
        modalContent.appendChild(placeholderText);


        // Drag and drop event listeners
        dropArea.addEventListener('dragenter', (event) => this.handleDragEnter(event));
        dropArea.addEventListener('dragover', (event) => this.handleDragOver(event));
        dropArea.addEventListener('drop', (event) => this.handleDrop(event));

        // Append modal to body
        document.body.appendChild(this.modal);
    }

    handleDragEnter(event) {
        event.preventDefault();
        event.target.style.backgroundColor = '#eee';
    }

    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(event) {
        event.preventDefault();
        event.target.style.backgroundColor = '';
        const file = event.dataTransfer.files[0];
        this.handleFile(file);

        const dropArea = document.getElementById('drop-area');
        dropArea.textContent = 'Getting tube details now...';

        sendImageAndAnalyze(file).then(() => {
            dropArea.textContent = 'Drag and drop your image here';
            this.hide();
        }).catch(error => {
            this.hide();
            alert(error);
    });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        this.handleFile(file);
    }

    handleFile(file) {
        if (file && file.type.startsWith('image/')) {
            this.showImagePreview(file);
            if (this.onImageSelected) {
                this.onImageSelected(file);
            }
        } else {
            alert('Please select a valid image file.');
        }
    }
    
    showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.imagePreview.src = e.target.result;
            this.imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    show() {
        this.modal.style.display = 'block';
    }

    hide() {
        this.modal.style.display = 'none';
        this.imagePreview.style.display = 'none';
        this.file = null;
    }
}

export {ImageUploadModal};