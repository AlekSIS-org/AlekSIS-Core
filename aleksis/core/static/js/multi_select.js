$(document).ready(function () {
    $(".select--header-box").change(function () {
        /*
        If the top checkbox is checked, all sub checkboxes should be checked,
        if it gets unchecked, all other ones should get unchecked.
        */
        if ($(this).is(":checked")) {
            $(this).closest("table").find('input[name="selected_objects"]').prop({
                indeterminate: false,
                checked: true,
            });
        } else {
            $(this).closest("table").find('input[name="selected_objects"]').prop({
                indeterminate: false,
                checked: false,
            });
        }
    });

    $('input[name="selected_objects"]').change(function () {
        /*
        If a table checkbox changes, check the state of the other ones.
        If all boxes are checked the box in the header should be checked,
        if all boxes are unchecked the header box should be unchecked. If
        only some boxes are checked the top one should be inderteminate.
         */
        let checked = $(this).is(":checked");
        let indeterminate = false;
        let table = $(this).closest("table");
        table.find('input[name="selected_objects"]').each(function () {
            if ($(this).is(":checked") !== checked) {
                /* Set the header box to indeterminate if the boxes are not the same */
                table.find(".select--header-box").prop({
                    indeterminate: true,
                })
                indeterminate = true;
                return false;
            }
        });
        if (!(indeterminate)) {
            /* All boxes are the same, set the header box to the same value */
            table.find(".select--header-box").prop({
                indeterminate: false,
                checked: checked,
            });
        }
    });
});
