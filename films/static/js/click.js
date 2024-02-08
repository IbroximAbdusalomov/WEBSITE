document.addEventListener("DOMContentLoaded", function () {
    var cardBuyContents = document.querySelectorAll(".card__buy-content");

    cardBuyContents.forEach(function (cardBuyContent) {
        cardBuyContent.addEventListener("click", function () {
            var productId = cardBuyContent.getAttribute("product-id");

            if (productId) {
                window.location.href = "{% url 'product-detail' 0 %}".replace('0', productId);
            } else {
                console.error("Product ID is empty or undefined");
            }
        });
    });
});
