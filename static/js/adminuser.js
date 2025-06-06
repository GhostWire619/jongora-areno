
// Function to show the form when the button is clicked
document.getElementById("showFormBtn").addEventListener("click", function() {
    document.getElementById("formContainer").style.display = "flex";
  });

  // Function to close the form
  function closeForm() {
    document.getElementById("formContainer").style.display = "none";
  } 


//expanding booking item list



function Expand (Id, right){
  const activityitem = document.getElementById(Id)
  const activityright = document.getElementById(right)
  if (activityitem.style.height !== 'auto') {
      activityitem.style.height = 'auto'
      activityright.style.backgroundColor = 'rgba(0, 128, 0, 0.267)'
  }
  else{
      activityitem.style.height = '30px'
      activityright.style.backgroundColor = 'white'
  }
  
}



// code to delete a booking post
function confirmDelete(name) {
  const confirmation = confirm(`Are You sure You Want to delete This: ${name} ?`);
  if (confirmation) {
      return true; // Proceed with form submission
  } else {
      return false; // Cancel form submission
  }
} 

function showQstnForm() {
  const questionformcont = document.querySelector('.questionformcont')
  questionformcont.style.display = 'flex'
}
function hideQstnForm() {
  const questionformcont = document.querySelector('.questionformcont')
  questionformcont.style.display = 'none'
}

















