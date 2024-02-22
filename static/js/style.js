// const categorySelect = document.getElementById('category');
// const buttons = document.querySelectorAll('.price__form-button__item');
// const bannerImage = document.getElementById('bannerImage');
// const titleH2 = document.querySelector('.style-title-home');
// const span = document.querySelector('.border-color');
//
// buttons.forEach(button => {
//     button.addEventListener('click', (event) => {
//         event.preventDefault();
//         buttons.forEach(btn => btn.classList.remove('btn_active'));
//         button.classList.add('btn_active');
//         const imageName = button.getAttribute('data-image');
//         bannerImage.src = `media/images/banners/${imageName}`;
//
//         const titleParts = button.getAttribute('data-title').split('||');
//         const spanText = button.getAttribute('data-span-text');
//         titleH2.innerHTML = `${titleParts[0]} <span class="border-color">${spanText}</span> ${titleParts[1]}`;
//
//         const categoryText = button.querySelector('a').innerText;
//         const categoryOption = categorySelect.querySelector(`[value="${categoryText}"]`);
//         if (categoryOption) {
//             categoryOption.selected = true;
//         }
//     });
// });
//
//
// const cardRows = document.querySelectorAll('.card-row');
// const colorClasses = ['card-color-pink', 'card-color-yellow', 'card-color-green', 'card-color-blue'];
//
// cardRows.forEach((row, index) => {
//     const colorClass = colorClasses[index % colorClasses.length];
//     row.querySelectorAll('.card__buy').forEach(card => {
//         card.classList.add(colorClass);
//     });
// });
//
//
// let currentStep = 0;
// const steps = document.querySelectorAll('.step');
//
// function nextStep() {
//     if (currentStep < steps.length - 1) {
//         steps[currentStep].style.display = 'none';
//         currentStep++;
//         steps[currentStep].style.display = 'block';
//     }
// }
