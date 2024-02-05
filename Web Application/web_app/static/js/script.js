// script.js
function displayFilePath() {
    const fileInput = document.getElementById('file');
    const filePath = document.getElementById('filePath');

    if (fileInput.files.length > 0) {
        filePath.innerHTML = `File Path: ${fileInput.files[0].name}`;
    } else {
        filePath.innerHTML = '';
    }
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.scrollIntoView({ behavior: 'smooth' });
}

function openSignInPopup() {
    const signInPopup = document.getElementById('signInPopup');
    signInPopup.style.display = 'block';
}

function closeSignInPopup() {
    const signInPopup = document.getElementById('signInPopup');
    signInPopup.style.display = 'none';
    const alert = document.getElementById('alert');
    alert.style.display = 'none';
}

function validateSignInForm() {
    const signInUsername = document.getElementById('signInUsername').value;
    const signInPassword = document.getElementById('signInPassword').value;

    if (!signInUsername || !signInPassword) {
        alert('Username and Password are required.');
        return false;
    }

    // Additional validation logic if needed

    return true;
}

function validateRegisterForm() {
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const mobileNo = document.getElementById('mobileNo').value;
    const registerPassword = document.getElementById('registerPassword').value;
    const reenterPassword = document.getElementById('reenterPassword').value;

    if (!firstName || !lastName || !email || !mobileNo || !registerPassword || !reenterPassword) {
        alert('All fields are required.');
        return false;
    }

    if (registerPassword !== reenterPassword) {
        alert('Passwords do not match.');
        return false;
    }

    // Additional validation logic if needed

    return true;
}

// Close popup if the user clicks outside the popup
window.onclick = function (event) {
    const signInPopup = document.getElementById('signInPopup');
    const registerPopup = document.getElementById('registerPopup');

    if (event.target === signInPopup) {
        signInPopup.style.display = 'none';
    }

    if (event.target === registerPopup) {
        registerPopup.style.display = 'none';
    }
};

function autofillUsername() {
    // Get the value of the email field
    var emailInput = document.getElementById('email');
    var emailValue = emailInput.value;

    // Extract the part before the '@' symbol
    var username = emailValue.split('@')[0];

    // Autofill the registerUsername field
    var usernameInput = document.getElementById('registerUsername');
    usernameInput.value = username;
}




// async function uploadFile() {
//     const fileInput = document.getElementById('file');
//     const file = fileInput.files[0];

//     if (file) {
//         const formData = new FormData();
//         formData.append('file', file);

//         try {
//             const response = await fetch('/upload', {
//                 method: 'POST',
//                 body: formData
//             });

//             if (response.ok) {
//                 const result = await response.json();
//                 console.log('Data from server:', result);
//             } else {
//                 console.error('Failed to upload file.');
//             }
//         } catch (error) {
//             console.error('Error:', error);
//         }
//     } else {
//         console.log('No file selected.');
//     }
// }

