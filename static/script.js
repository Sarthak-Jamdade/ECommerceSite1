/***********************************************************
 * NAVBAR TOGGLE
************************************************************/
const bar = document.getElementById("bar");
const nav = document.getElementById("nav-links");
const closeNav = document.getElementById("close");

bar?.addEventListener("click", () => nav.classList.add("active"));
closeNav?.addEventListener("click", () => nav.classList.remove("active"));

/***********************************************************
 * DARK MODE
************************************************************/
document.getElementById("changeTheme")?.addEventListener("click", () => {
    document.body.classList.toggle("darkMode");
    // Manage Font Colors
    document.body.classList.toggle("darkMode") ?
        document.documentElement.style.setProperty("--text-color", "#fff") :
        document.documentElement.style.setProperty("--text-color", "#000");
});

/***********************************************************
 * REVEAL ANIMATION
************************************************************/
function reveal(selector) {
    document.querySelectorAll(selector).forEach(el => {
        if (el.getBoundingClientRect().top < window.innerHeight - 100) {
            el.classList.add("active");
        }
    });
}
window.addEventListener("scroll", () => {
    reveal(".reveal");
    reveal(".reveal-left");
});
window.addEventListener("load", () => {
    reveal(".reveal");
    reveal(".reveal-left");
});

/***********************************************************
 * PRODUCT DATABASE
************************************************************/
const PRODUCT_DATA = {
    1: { name: "Astronaut T-Shirt 1", price: 78, images: ["Projects/f1.jpg", "Projects/f2.jpg", "Projects/f3.jpg", "Projects/f4.jpg"] },
    2: { name: "Astronaut T-Shirt 2", price: 82, images: ["Projects/f2.jpg", "Projects/f3.jpg", "Projects/f4.jpg", "Projects/f1.jpg"] },
    3: { name: "Astronaut T-Shirt 3", price: 69, images: ["Projects/f3.jpg", "Projects/f4.jpg", "Projects/f1.jpg", "Projects/f2.jpg"] },
    4: { name: "Astronaut T-Shirt 4", price: 95, images: ["Projects/f4.jpg", "Projects/f3.jpg", "Projects/f2.jpg", "Projects/f1.jpg"] },

    5: { name: "Black Hoodie Premium", price: 120, images: ["Projects/f5.jpg", "Projects/f6.jpg", "Projects/f7.jpg", "Projects/f8.jpg"] },
    6: { name: "White Hoodie Premium", price: 110, images: ["Projects/f6.jpg", "Projects/f5.jpg", "Projects/f7.jpg", "Projects/f8.jpg"] },
    7: { name: "Printed Shirt 1", price: 65, images: ["Projects/f7.jpg", "Products/f50.png", "Products/f51.png", "Products/f49.png"] },
    8: { name: "Printed Shirt 2", price: 55, images: ["Projects/f8.jpg", "Projects/f7.jpg", "Projects/f6.jpg", "Projects/f5.jpg"] },

    9: { name: "New Black Shirt", price: 89, images: ["Projects/n1.jpg", "Projects/n2.jpg", "Projects/n3.jpg", "Projects/n4.jpg"] },
    10: { name: "New White Shirt", price: 85, images: ["Projects/n2.jpg", "Projects/n3.jpg", "Projects/n4.jpg", "Projects/n1.jpg"] },
    11: { name: "New Printed Tee", price: 70, images: ["Projects/n3.jpg", "Projects/n4.jpg", "Projects/n1.jpg", "Projects/n2.jpg"] },
    12: { name: "New Hoodie Special", price: 150, images: ["Projects/n4.jpg", "Projects/n3.jpg", "Projects/n2.jpg", "Projects/n1.jpg"] },

    13: { name: "Casual Blue Shirt", price: 75, images: ["Products/f9.png", "Products/f10.png", "Products/f11.png", "Products/f12.jpg"] },
    14: { name: "Summer Vibes Tee", price: 60, images: ["Products/f13.png", "Products/f14.png", "Products/f15.png", "Products/f16.png"] },
    15: { name: "Sporty Hoodie", price: 130, images: ["Products/f17.png", "Products/f18.png", "Products/f19.png", "Products/f20.png"] },
    16: { name: "Classic White Shirt", price: 90, images: ["Products/f26.png", "Products/f22.png", "Products/f23.png", "Products/f9.png"] },

    17: { name: "Vintage Graphic Tee", price: 72, images: ["Products/f14.png", "Products/f14.png", "Products/f15.png", "Products/f16.png"] },
    18: { name: "Modern Fit Hoodie", price: 140, images: ["Products/f18.png", "Products/f19.png", "Products/f20.png", "Products/f21.png"] },
    19: { name: "Relaxed Casual Shirt", price: 80, images: ["Products/f15.png", "Products/f16.png", "Products/f13.png", "Products/f14.png"] },
    20: { name: "Trendy Streetwear Tee", price: 68, images: ["Products/f16.png", "Products/f15.png", "Products/f14.png", "Products/f13.png"] },

    21: { name: "Trendy Streetwear Tee", price: 76, images: ["Products/f27.png", "Products/f25.png", "Products/f23.png", "Products/f24.png"] },
    22: { name: "Trendy Streetwear Tee", price: 77, images: ["Products/f20.png", "Products/f20.png", "Products/f26.png", "Products/f25.png"] },
    23: { name: "Trendy Streetwear Tee", price: 232, images: ["Products/f25.png", "Products/f17.png", "Products/f25.png", "Products/f27.png"] },
    24: { name: "Trendy Streetwear Tee", price: 98, images: ["Products/f23.png", "Products/f25.png", "Products/f22.png", "Products/f26.png"] },
    24: { name: "Trendy Streetwear Tee", price: 289, images: ["Products/f23.png", "Products/f25.png", "Products/f22.png", "Products/f21.png"] },

    25: { name: "Trendy Streetwear Tee", price: 123, images: ["Products/f28.png", "Products/f29.png", "Products/f30.png", "Products/f31.png"] },
    26: { name: "Trendy Streetwear Tee", price: 165, images: ["Products/f32.png", "Products/f33.png", "Products/f34.png", "Products/f35.png"] },
    27: { name: "Trendy Streetwear Tee", price: 212, images: ["Products/f35.png", "Products/f34.png", "Products/f33.png", "Products/f32.png"] },
    28: { name: "Trendy Streetwear Tee", price: 99, images: ["Products/f31.png", "Products/f34.png", "Products/f29.png", "Products/f39.png"] },

    29: { name: "Trendy Streetwear Tee", price: 123, images: ["Products/f39.png", "Products/f40.png", "Products/f41.png", "Products/f42.png"] },
    30: { name: "Trendy Streetwear Tee", price: 165, images: ["Products/f43.png", "Products/f44.png", "Products/f45.png", "Products/f46.png"] },
    31: { name: "Trendy Streetwear Tee", price: 212, images: ["Products/f51.png", "Products/f48.png", "Products/f49.png", "Products/f50.png"] },
    32: { name: "Trendy Streetwear Tee", price: 99, images: ["Products/f46.png", "Products/f43.png", "Products/f44.png", "Products/f40.png"] }

};


/***********************************************************
 * GENERATE SHOP PAGE PRODUCTS
************************************************************/
const productList = document.getElementById("product-list");

if (productList) {
    productList.innerHTML = Object.keys(PRODUCT_DATA)
        .map(id => {
            let p = PRODUCT_DATA[id];
            return `
            <div class="pro reveal" data-id="${id}">
                <img src="${p.images[0]}" alt="">
                <div class="des">
                    <span>adidas</span>
                    <h5>${p.name}</h5>
                    <div class="star">
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fa-regular fa-star" style="color: gold;"></i>
                    </div>
                    <h4>$${p.price}</h4>
                </div>
                <a href="#"><i class="fas fa-shopping-cart Cart"></i></a>
            </div>`;
        })
        .join("");
}

/***********************************************************
 * CLICK PRODUCT CARD → OPEN SINGLE PRODUCT PAGE
************************************************************/
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("Cart")) return;

    const box = e.target.closest(".pro");

    if (box) {
        const id = box.dataset.id;
        window.location.href = "singleProduct.html?id=" + id;
    }
});

/***********************************************************
 * SINGLE PRODUCT PAGE SETUP
************************************************************/
const url = new URLSearchParams(window.location.search);
const prodId = url.get("id");
const product = PRODUCT_DATA[prodId];

if (document.getElementById("MainImg") && product) {

    // Set main image
    document.getElementById("MainImg").src = product.images[0];

    // Set small images
    let imagesHTML = "";
    product.images.forEach(img => {
        imagesHTML += `
            <div class="small-img-col">
                <img src="${img}" class="smallIMg" width="100%">
            </div>
        `;
    });
    document.querySelector(".small-img-group").innerHTML = imagesHTML;

    // Set name + price
    document.getElementById("p-name").innerText = product.name;
    document.getElementById("p-price").innerText = "$" + product.price;

    // Handle thumbnail clicks
    setTimeout(() => {
        const mainImg = document.getElementById("MainImg");
        const thumbs = document.getElementsByClassName("smallIMg");

        for (let i = 0; i < thumbs.length; i++) {
            thumbs[i].addEventListener("click", function () {
                mainImg.src = this.src;
            });
        }
    }, 200);
}

// Loading product description (static for demo)
if (document.getElementById("product-desc")) {
    document.getElementById("product-desc").innerText =
        "This is a high-quality product made from the finest materials. Perfect for everyday wear and special occasions.";
}

/***********************************************************
 * PAGINATION SETTINGS
************************************************************/
const ITEMS_PER_PAGE = 8;   // 1 page = 8 products
let currentPage = 1;

/***********************************************************
 * FUNCTION TO DISPLAY PRODUCTS BY PAGE
************************************************************/
function loadProducts(page) {
    const productList = document.getElementById("product-list");
    if (!productList) return;

    const keys = Object.keys(PRODUCT_DATA);

    const start = (page - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;

    const pageItems = keys.slice(start, end);

    productList.innerHTML = pageItems
        .map(id => {
            let p = PRODUCT_DATA[id];
            return `
            <div class="pro reveal" data-id="${id}">
                <img src="${p.images[0]}" alt="">
                <div class="des">
                    <span>adidas</span>
                    <h5>${p.name}</h5>
                    <div class="star">
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fas fa-star" style="color: gold;"></i>
                        <i class="fa-regular fa-star" style="color: gold;"></i>
                    </div>
                    <h4>$${p.price}</h4>
                </div>
                <a href="#"><i class="fas fa-shopping-cart Cart"></i></a>
            </div>`;
        })
        .join("");
}

/***********************************************************
 * PAGINATION BUTTON CLICK HANDLER
************************************************************/
function goToPage(page) {
    const totalPages = Math.ceil(Object.keys(PRODUCT_DATA).length / ITEMS_PER_PAGE);

    if (page < 1 || page > totalPages) return;
    currentPage = page;

    loadProducts(currentPage);
}

/***********************************************************
 * PAGINATION BUTTON EVENTS
************************************************************/
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("page-btn")) {
        const page = parseInt(e.target.dataset.page);
        goToPage(page);
    }
});

// Loading Screen Script
window.addEventListener("load", function () {
    const loadingScreen = document.querySelector(".Loading");
    loadingScreen.classList.add("hidden");
    setTimeout(function () {
        loadingScreen.style.display = "none";
    }, 1000);
});

/***********************************************************
 * AUTO PRODUCT REVEAL ON SCROLL
************************************************************/

function autoRevealProducts() {

    const products = document.querySelectorAll(".pro");

    products.forEach((product, index) => {

        const productTop = product.getBoundingClientRect().top;

        const windowHeight = window.innerHeight;

        if (productTop < windowHeight - 80) {

            setTimeout(() => {

                product.classList.add("active");

            }, index * 100);
        }
    });
}

/***********************************************************
 * RUN ON SCROLL + LOAD
************************************************************/

window.addEventListener("scroll", autoRevealProducts);

window.addEventListener("load", autoRevealProducts);



const toggleBtn =
    document.getElementById("categoryToggle");

const categoryMenu =
    document.getElementById("categoryMenu");

toggleBtn.onclick = () => {

    categoryMenu.classList.toggle("active");
};

const floatingBtn =
    document.querySelector(".floating-category");

let isDragging = false;

let offsetX, offsetY;

/* DESKTOP */

floatingBtn.addEventListener("mousedown", (e) => {

    isDragging = true;

    offsetX =
        e.clientX - floatingBtn.offsetLeft;

    offsetY =
        e.clientY - floatingBtn.offsetTop;
});

document.addEventListener("mousemove", (e) => {

    if (!isDragging) return;

    floatingBtn.style.left =
        (e.clientX - offsetX) + "px";

    floatingBtn.style.top =
        (e.clientY - offsetY) + "px";
});

document.addEventListener("mouseup", () => {

    isDragging = false;
});

/* MOBILE TOUCH */

floatingBtn.addEventListener("touchstart", (e) => {

    isDragging = true;

    const touch = e.touches[0];

    offsetX =
        touch.clientX - floatingBtn.offsetLeft;

    offsetY =
        touch.clientY - floatingBtn.offsetTop;
});

document.addEventListener("touchmove", (e) => {

    if (!isDragging) return;

    const touch = e.touches[0];

    floatingBtn.style.left =
        (touch.clientX - offsetX) + "px";

    floatingBtn.style.top =
        (touch.clientY - offsetY) + "px";
});

document.addEventListener("touchend", () => {

    isDragging = false;
});

