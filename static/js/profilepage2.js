



// to display the image uploaded
document.getElementById('showFilesButton').addEventListener('click', function() {
    document.getElementById('fileInputsContainer').style.display = 'flex';
  });
  
  const fileInputs = document.querySelectorAll('.file-input');
  const fileLabels = [
    document.getElementById('fileLabel1'),
    document.getElementById('fileLabel2'),
    document.getElementById('fileLabel3'),
    document.getElementById('fileLabel4'),
    document.getElementById('fileLabel5')
  ];
  
  fileInputs.forEach((input, index) => {
    input.addEventListener('change', function() {
        const fileName = input.files[0] ? input.files[0].name : '';
        fileLabels[index].textContent = fileName;
        updateButtonLabel();
    });
  });
  
  function updateButtonLabel() {
    const filledInputs = Array.from(fileInputs).filter(input => input.files.length > 0).length;
    const buttonLabel = filledInputs === 5 ? 'All files selected' : `${filledInputs} images`;
    document.getElementById('showFilesButton').textContent = buttonLabel;
  }

  const closebutton = document.querySelector('.imagesclosebutton');

  closebutton.addEventListener("click", () => {
    document.getElementById('fileInputsContainer').style.display = 'none';
  })


function showFollowing() {
  const followingdiv = document.getElementById('followingdiv');
  followingdiv.style.right = '0';
}

function closeFollowing() {
  const followingdiv = document.getElementById('followingdiv');
  
  followingdiv.style.right = '-350px';
}





