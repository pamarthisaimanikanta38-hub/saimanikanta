const startButton = document.getElementById('start-camera');
const captureButton = document.getElementById('capture-photo');
const videoFeed = document.getElementById('camera-feed');

startButton.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoFeed.srcObject = stream;
        startButton.disabled = true;
        startButton.textContent = 'Camera Started';
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Unable to access camera. Please check permissions.');
    }
});

captureButton.addEventListener('click', async () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoFeed.videoWidth;
    canvas.height = videoFeed.videoHeight;
    
    const context = canvas.getContext('2d');
    context.drawImage(videoFeed, 0, 0);
    
    canvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append('photo', blob, 'attendance.jpg');
        
        fetch('/capture', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Attendance marked successfully!');
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }, 'image/jpeg');
});