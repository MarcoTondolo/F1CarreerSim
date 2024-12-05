// File: static/scripts/drag-drop.js

document.addEventListener('DOMContentLoaded', () => {
    let draggedElement = null;

    document.querySelectorAll('.driver').forEach(driver => {
        driver.addEventListener('dragstart', (event) => {
            draggedElement = event.target;
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', draggedElement.id);
        });

        driver.addEventListener('dragover', (event) => {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'move';
        });

        driver.addEventListener('drop', (event) => {
            event.preventDefault();
            const targetElement = event.target.closest('.driver');
            if (targetElement && targetElement !== draggedElement) {
                const oldTeam = draggedElement.getAttribute('data-team');
                const newTeam = targetElement.closest('.grid-item').id.split('-')[1];

                swapElements(draggedElement, targetElement);

                updateJacket(draggedElement, newTeam);
                updateJacket(targetElement, oldTeam);

                // Update the data-team attribute
                draggedElement.setAttribute('data-team', newTeam);
                targetElement.setAttribute('data-team', oldTeam);
            }
        });
    });

    function swapElements(el1, el2) {
        const parent1 = el1.parentNode;
        const sibling1 = el1.nextSibling === el2 ? el1 : el1.nextSibling;

        const parent2 = el2.parentNode;
        const sibling2 = el2.nextSibling === el1 ? el2 : el2.nextSibling;

        parent2.insertBefore(el1, sibling2);
        parent1.insertBefore(el2, sibling1);
    }

    function updateJacket(driverElement, team) {
        const jacketElement = driverElement.querySelector('.jacket img');
        jacketElement.src = `/static/images/jackets/${team}-jacket.png`;
        jacketElement.alt = team;
    }
});
