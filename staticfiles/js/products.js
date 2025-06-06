

// code for refreshing more products
let loadmore = document.querySelector('.loadmore')
let currentItem = 20;

loadmore.onclick = () => {
    let productboxes = document.querySelectorAll('.product-productpage');
    let hiddenProductBoxes = Array.from(productboxes).slice(currentItem, currentItem + 20);
    
    hiddenProductBoxes.forEach(box => {
        box.style.display = 'flex';
    });

    currentItem += 20;

    if (currentItem >= productboxes.length) {
        loadmore.style.display = 'none';
    }
};





 
