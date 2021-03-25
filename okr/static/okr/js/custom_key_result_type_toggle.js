const keyResultSelector = '#id_key_result';

const fieldValueTextSelector = '.field-value_text';
const fieldValueIntegerSelector = '.field-value_integer';

const fieldValueSelectors = [fieldValueTextSelector, fieldValueIntegerSelector];

const toggleValueFields = (keyResult) => {
    fieldValueSelectors.forEach(function (selector) {
        django.jQuery(selector).hide();
    });

    if (keyResultTypes[keyResult] === "integer") {
        django.jQuery(fieldValueIntegerSelector).show();
    } else if (keyResultTypes[keyResult] === "text") {
        django.jQuery(fieldValueTextSelector).show();
    }
}

django.jQuery(document).ready(function () {
    fieldValueSelectors.forEach(function (selector) {
        django.jQuery(selector).addClass("manual-required");
    });

    toggleValueFields(django.jQuery(keyResultSelector)[0].value);

    django.jQuery(keyResultSelector).change(function () {
        toggleValueFields(this.value);
    })
});
