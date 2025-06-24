document.addEventListener('DOMContentLoaded', function () {
    const table = new DataTable('#tripTable', {
        order: [[1, 'desc']],
        pageLength: 25,
        lengthMenu: [10, 25, 50, 100],
        language: {
            url: "/static/js/ru.json"
        }
    });
    new $.fn.dataTable.FixedHeader(table);

    // Подсветка строк, где вес > тоннажа
    $('#tripTable tbody tr').each(function () {
        let weightText = $(this).find('td:eq(9)').text().replace(/[^\d.,]/g, '').replace(',', '.');
        let tonnageText = $(this).find('td:eq(7)').text().replace(/[^\d.,]/g, '').replace(',', '.');

        let weight = parseFloat(weightText);
        let tonnage = parseFloat(tonnageText);

        if (!isNaN(weight) && !isNaN(tonnage) && weight > tonnage) {
            $(this).addClass('highlight-overweight');
        }
    });
});

// Показ / скрытие одного комментария
function toggleComment(toggleEl) {
    const commentBlock = toggleEl.nextElementSibling;
    if (commentBlock.classList.contains('d-none')) {
        commentBlock.classList.remove('d-none');
        toggleEl.innerText = '▲ Скрыть';
    } else {
        commentBlock.classList.add('d-none');
        toggleEl.innerText = '▼ Показать';
    }
}

// Скрыть/показать все комментарии
function toggleAllComments() {
    document.querySelectorAll('.comment-toggle').forEach(toggleEl => {
        const commentBlock = toggleEl.nextElementSibling;
        const isHidden = commentBlock.classList.contains('d-none');
        commentBlock.classList.toggle('d-none', !isHidden);
        toggleEl.innerText = isHidden ? '▲ Скрыть' : '▼ Показать';
    });
}
