     
      //shopping main slider
const shoppingmainad = new Splide( '#shopping-main-ad', {
  perPage: 1,
  drag : 'free',
  perMove: 1,
  padding: 0,
  snap: true,
  type: 'fade',
  rewind: true,
  arrows: false,
  interval: 10000,
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
  shoppingmainad.mount()

   