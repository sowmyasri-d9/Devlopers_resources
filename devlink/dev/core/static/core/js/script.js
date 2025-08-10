$(document).ready(function () {
    $('#share').on('click', function (e) {
        e.stopPropagation();
        $('#shareContainer').toggleClass('d-none');
    });

    // Handle clicks on share buttons and clicks outside the container
    $(document).on('click', function (e) {
        const $container = $('#shareContainer');

        if (!$container.hasClass('d-none')) {
            if (!$(e.target).closest('#shareContainer').length && !$(e.target).closest('#share').length) {
                $container.addClass('d-none');
            }


            if ($(e.target).is('a.btn')) {
                setTimeout(() => {
                    $container.addClass('d-none');
                }, 100);
            }
        }
    });
});
