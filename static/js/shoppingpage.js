

//expanding menu bar
const menu = document.querySelector('.nav-menu');
const secondmenu = document.querySelector('.second-menu');
const minimize = document.querySelector('.minimize-menu');
const minimizediv = document.querySelector('.menu');
const darkside = document.querySelector('.darkside');
const menudiv = document.querySelector('.menudiv');

  menu.addEventListener("click", () => {
      menudiv.style.display = 'flex'
      minimizediv.style.display = 'flex'
      minimizediv.style.width = '100%'
      darkside.style.width = '100%'
  })

  minimize.addEventListener("click", () => {
      menudiv.style.display = 'none'
      minimizediv.style.width = '0px'
      darkside.style.width = 'auto'
  })
  darkside.addEventListener("click", () => {
      menudiv.style.display = 'none'
      minimizediv.style.width = '0px'
      darkside.style.width = 'auto'
  })
  

//expanding categories in filter menu div

const filtermenudiv = document.getElementById('filtercategory')
const morefiltercategory = document.getElementById('morefiltercategory')
const filtercategoriesdiv = document.querySelector('.filtercategoriesdiv')

  filtermenudiv.addEventListener("click", () => {
    if (filtercategoriesdiv.style.height === '264px' || filtercategoriesdiv.style.height === '') {
      filtercategoriesdiv.style.height = 'auto';
      filtermenudiv.textContent = 'Minimize Categories'
      morefiltercategory.textContent = 'View Less'
      filtermenudiv.style.backgroundColor = 'rgba(0, 0, 0, 0)'
      filtermenudiv.style.border = '1px solid rgba(0, 0, 0, 0.253)'
      
    } else {
      filtercategoriesdiv.style.height = '264px';
      filtermenudiv.textContent = 'Categories'
      morefiltercategory.textContent = 'View More'
      filtermenudiv.style.backgroundColor = 'rgba(128, 128, 128, 0.226)'
      filtermenudiv.style.border = '1px solid rgba(0, 0, 0, 0)'

      
    }
    
    
  });

  morefiltercategory.addEventListener("click", () => {
    if (filtercategoriesdiv.style.height === '264px' || filtercategoriesdiv.style.height === '') {
      filtercategoriesdiv.style.height = 'auto';
      filtermenudiv.textContent = 'Minimize Categories'
      morefiltercategory.textContent = 'View Less'
      filtermenudiv.style.backgroundColor = 'rgba(0, 0, 0, 0)'
      filtermenudiv.style.border = '1px solid rgba(0, 0, 0, 0.253)'
      
    } else {
      filtercategoriesdiv.style.height = '264px';
      filtermenudiv.textContent = 'Categories'
      morefiltercategory.textContent = 'View More'
      filtermenudiv.style.backgroundColor = 'rgba(128, 128, 128, 0.226)'
      filtermenudiv.style.border = '1px solid rgba(0, 0, 0, 0)'

      
    }
  });


//expanding filter menu bar
const filter = document.querySelector('.filter-icon');
const filtermenu = document.querySelector('.filtermenu');
const filterdarkside = document.querySelector('.filterdarkside');
const filterdiv = document.querySelector('.filtermenudiv');

  filter.addEventListener("click", () => {
      filtermenu.style.width = '100%'
      filterdiv.style.transform = 'translateX(0%)'
      filterdarkside.style.width = '100%'
  })
  filterdarkside.addEventListener("click", () => {
    filterdiv.style.transform = 'translateX(100%)'
    filtermenu.style.width = 'auto'
    filterdarkside.style.width = 'auto'
  })


function goBack() {
  // Go back to the previous page
  window.history.back();
}


function displayshoppingcat () {

  const shoppingcatbtn = document.getElementById('shoppingcatbtn');
  const restaurantcatbtn = document.getElementById('restaurantcatbtn');
  const shoppingcat = document.getElementById('shoppingcat');
  const restaurantcat = document.getElementById('restaurantcat');
  const restaurantcatinput = document.getElementById('restaurantcatinput');
  const shoppingcatinput = document.getElementById('shoppingcatinput');

  if (shoppingcat.style.display !== 'flex'){
    shoppingcat.style.display = 'flex';
    restaurantcat.style.display = 'None';
    shoppingcatbtn.style.backgroundColor = 'rgba(0, 128, 0, 0.438)';
    restaurantcatbtn.style.backgroundColor = 'rgba(0, 128, 0, 0.26)'
    restaurantcatinput.disabled = true;
    shoppingcatinput.disabled = false;
  }

}

function displayrestaurantcat () {

  const shoppingcatbtn = document.getElementById('shoppingcatbtn');
  const restaurantcatbtn = document.getElementById('restaurantcatbtn');
  const shoppingcat = document.getElementById('shoppingcat');
  const restaurantcat = document.getElementById('restaurantcat');
  const shoppingcatinput = document.getElementById('shoppingcatinput');
  const restaurantcatinput = document.getElementById('restaurantcatinput');

  if (restaurantcat.style.display !== 'flex'){
    restaurantcat.style.display = 'flex';
    shoppingcat.style.display = 'None';
    restaurantcatbtn.style.backgroundColor = 'rgba(0, 128, 0, 0.438)';
    shoppingcatbtn.style.backgroundColor = 'rgba(0, 128, 0, 0.26)';
    shoppingcatinput.disabled = true;
    restaurantcatinput.disabled = false;
  }

}






