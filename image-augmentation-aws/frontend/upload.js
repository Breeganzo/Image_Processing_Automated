// Configuration - Update these values after Terraform deployment
const AWS_CONFIG = {
    region: 'us-east-1',
    bucketName: 'YOUR_BUCKET_NAME_HERE', // Will be filled after deployment
};

class ImageAugmentationUploader {
    constructor() {
        this.selectedFile = null;
        this.uploadInProgress = false;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File input and upload area
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const downloadAllBtn = document.getElementById('downloadAllBtn');

        // Click to select file
        uploadArea.addEventListener('click', () => {
            if (!this.uploadInProgress) {
                fileInput.click();
            }
        });

        // File selection
        fileInput.addEventListener('change', (e) => this.handleFileSelection(e));

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleFileDrop(e));

        // Button clicks
        uploadBtn.addEventListener('click', () => this.uploadFile());
        cancelBtn.addEventListener('click', () => this.cancelSelection());
        downloadAllBtn.addEventListener('click', () => this.downloadAllImages());
    }

    handleFileSelection(event) {
        const file = event.target.files[0];
        if (file) {
            this.validateAndDisplayFile(file);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');
    }

    handleFileDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.validateAndDisplayFile(files[0]);
        }
    }

    validateAndDisplayFile(file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            alert('Please select a valid image file (JPG, JPEG, or PNG)');
            return;
        }

        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB in bytes
        if (file.size > maxSize) {
            alert('File size must be less than 10MB');
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
    }

    displayFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileDetails = document.getElementById('fileDetails');
        
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        const fileType = file.type.split('/')[1].toUpperCase();
        
        fileDetails.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div><strong>Name:</strong> ${file.name}</div>
                <div><strong>Size:</strong> ${fileSize} MB</div>
                <div><strong>Type:</strong> ${fileType}</div>
                <div><strong>Processing:</strong> Resize to 256×256 + 4 rotations</div>
            </div>
        `;
        
        fileInfo.style.display = 'block';
    }

    cancelSelection() {
        this.selectedFile = null;
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('fileInput').value = '';
        this.hideStatusSection();
        this.hideResultsSection();
    }

    async uploadFile() {
        if (!this.selectedFile) {
            alert('Please select a file first');
            return;
        }

        if (this.uploadInProgress) {
            return;
        }

        this.uploadInProgress = true;
        this.showStatusSection();
        
        try {
            // Step 1: Generate unique filename
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const fileExtension = this.selectedFile.name.split('.').pop();
            const uniqueFilename = `upload_${timestamp}.${fileExtension}`;
            
            // Step 2: Show upload progress
            this.updateStatus('Uploading image to AWS S3...', 20);
            
            // For demo purposes, we'll simulate the upload process
            // In a real implementation, you would:
            // 1. Get pre-signed URL from your backend
            // 2. Upload directly to S3
            // 3. Monitor processing via WebSocket or polling
            
            await this.simulateUploadProcess(uniqueFilename);
            
        } catch (error) {
            console.error('Upload failed:', error);
            this.updateStatus(`❌ Upload failed: ${error.message}`, 0);
            this.uploadInProgress = false;
        }
    }

    async simulateUploadProcess(filename) {
        // Simulate the real AWS pipeline process
        const steps = [
            { message: 'Uploading to S3...', progress: 20, delay: 1000 },
            { message: 'Triggering Lambda processor...', progress: 35, delay: 1500 },
            { message: 'Resizing image to 256×256...', progress: 50, delay: 2000 },
            { message: 'Queuing rotation tasks in SQS...', progress: 65, delay: 1000 },
            { message: 'Processing 90° rotation...', progress: 75, delay: 1500 },
            { message: 'Processing 180° rotation...', progress: 85, delay: 1000 },
            { message: 'Processing 270° rotation...', progress: 95, delay: 1000 },
            { message: '✅ All rotations complete!', progress: 100, delay: 500 }
        ];

        for (let step of steps) {
            this.updateStatus(step.message, step.progress);
            await new Promise(resolve => setTimeout(resolve, step.delay));
        }

        // Show results
        setTimeout(() => {
            this.showProcessingComplete(filename);
            this.uploadInProgress = false;
        }, 1000);
    }

    updateStatus(message, progress) {
        document.getElementById('statusMessage').innerHTML = `
            <div class="loading"></div>${message}
        `;
        document.getElementById('progressBar').style.width = `${progress}%`;
        
        // Update processing steps
        const stepsDiv = document.getElementById('processingSteps');
        const timestamp = new Date().toLocaleTimeString();
        stepsDiv.innerHTML += `<div>[${timestamp}] ${message}</div>`;
        stepsDiv.scrollTop = stepsDiv.scrollHeight;
    }

    showStatusSection() {
        document.getElementById('statusSection').style.display = 'block';
        document.getElementById('processingSteps').innerHTML = '';
    }

    hideStatusSection() {
        document.getElementById('statusSection').style.display = 'none';
    }

    showProcessingComplete(filename) {
        this.hideStatusSection();
        this.showResultsSection(filename);
    }

    showResultsSection(filename) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsGrid = document.getElementById('resultsGrid');
        
        // Create placeholder results (in real implementation, these would be actual S3 URLs)
        const rotations = [
            { angle: 90, description: '90° Clockwise' },
            { angle: 180, description: '180° Upside Down' },
            { angle: 270, description: '270° Clockwise' },
            { angle: 360, description: '360° Original' }
        ];

        resultsGrid.innerHTML = '';
        
        rotations.forEach(rotation => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.innerHTML = `
                <div style="height: 200px; background: linear-gradient(45deg, #f0f0f0, #e0e0e0); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                    <div style="text-align: center; color: #666;">
                        <div style="font-size: 2em; margin-bottom: 10px;">🖼️</div>
                        <div>Processed Image</div>
                        <div style="font-size: 0.8em;">${rotation.angle}°</div>
                    </div>
                </div>
                <h4>${rotation.description}</h4>
                <p>Stored in: /augmented-images/${rotation.angle}-degree/</p>
                <p>Size: 256×256 pixels</p>
            `;
            resultsGrid.appendChild(card);
        });
        
        resultsSection.style.display = 'block';
    }

    hideResultsSection() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    downloadAllImages() {
        // In a real implementation, this would download actual processed images
        alert('📥 Download functionality will retrieve all 4 processed images from S3.\n\nIn the actual implementation, this will:\n1. Generate pre-signed URLs for each processed image\n2. Download them as a ZIP file\n3. Include metadata about processing details');
    }
}

// Initialize the uploader when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ImageAugmentationUploader();
    
    // Show configuration reminder
    if (AWS_CONFIG.bucketName === 'YOUR_BUCKET_NAME_HERE') {
        console.warn('⚠️ Please update AWS_CONFIG in upload.js with your actual S3 bucket name after Terraform deployment');
    }
});

// Add some helpful functions for debugging
window.debugInfo = () => {
    console.log('🔧 Debug Information:');
    console.log('Selected file:', window.uploader?.selectedFile);
    console.log('Upload in progress:', window.uploader?.uploadInProgress);
    console.log('AWS Config:', AWS_CONFIG);
};

// Make uploader available globally for debugging
window.addEventListener('load', () => {
    if (window.uploader) {
        console.log('✅ Image Augmentation Uploader initialized successfully');
        console.log('💡 Type debugInfo() in console for debug information');
    }
});
