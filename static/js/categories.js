   //categories main ad slider
   const categoriesmainad = new Splide( '#categories-main-ad', {
    perPage: 1,
    drag : 'free',
    perMove: 1,
    padding: 0,
    snap: true,
    type: 'fade',
    rewind: true,
    arrows: false,
    interval: 9000,
    pagination: true,
    autoplay: true,
    breakpoints: {
      1200: {
      perPage: 1,
      },
      
      764: {
      perPage: 1,
      },
      678: {
        perPage: 1,
      },
      610: {
        perPage: 1,
      },
      580: {
        perPage: 1,
      },
      
      },
    } );
    categoriesmainad.mount()
  



// code for refreshing more products
let loadmore = document.querySelector('.loadmore')
let currentItem = 10;

loadmore.onclick = () => {
    let storeboxes = [...document.querySelectorAll('.store')];
    for (var i = currentItem; i < currentItem + 10; i++) {
        storeboxes[i].style.display = 'flex';
    }
    currentItem +=10;

    if (currentItem >= storeboxes.length){
        loadmore.style.display = 'none';
    }
    
}




