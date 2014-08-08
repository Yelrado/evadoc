function mostrar_formulario(recomendable) {
    var form = $('#formulario');
    form.css('display','block').hide().fadeIn();
    if (recomendable) {
        form.removeClass('offset6').addClass('offset1').css('background-color','rgba(98, 196, 98, 0.2)');
        jQuery('input#recomendable').prop('value','True');
    } else {
        form.removeClass('offset1').addClass('offset6').css('background-color','rgba(238, 95, 91, 0.2)');
        jQuery('input#recomendable').prop('value','');
    }
}
