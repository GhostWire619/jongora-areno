// code for refreshing more activities
let loadmore = document.querySelector('.loadmore');
let currentItem = 6;

loadmore.onclick = () => {
    let productboxes = [...document.querySelectorAll('.event')];
    for (var i = currentItem; i < Math.min(currentItem + 6, productboxes.length); i++) {
        productboxes[i].style.display = 'flex';
    }
    currentItem += 6;

    if (currentItem >= productboxes.length) {
        loadmore.style.display = 'none';
    }
};

//loading more hosts
let hostcurrentItem = 10; // Initial number of items to display

function loadMoreItems() {
    let storeboxes = [...document.querySelectorAll('.store')];
    let maxItems = hostcurrentItem + 10;

    for (let i = hostcurrentItem; i < maxItems && i < storeboxes.length; i++) {
        storeboxes[i].style.display = 'flex';
    }

    hostcurrentItem += 10;

    if (hostcurrentItem >= storeboxes.length) {
        document.querySelector('.loadmore').style.display = 'none';
    }
}